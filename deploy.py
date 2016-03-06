from deploy_credentials import CREDENTIALS, SUBSCRIPTION_ID
from uuid import uuid4

# Create a resource group for our deployment
RESOURCE_GROUP = "buildtest" + uuid4().hex
LOCATION = "West US"

COMPANY_NAME = "Contoso"
DEPLOYMENT = "DoIStillHaveAJob"
WEBSITE = "DoIStillHaveAJob"
STORAGE = 's' + uuid4().hex[:23].lower()
WEBSITE_SOURCE = "https://github.com/zooba/DoIStillHaveAJob.git"


# Import and configure management clients for resources and web sites

from azure.mgmt.resource.resources import ResourceManagementClientConfiguration, ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClientConfiguration, WebSiteManagementClient
rc = ResourceManagementClient(ResourceManagementClientConfiguration(
    credentials=CREDENTIALS,
    subscription_id=SUBSCRIPTION_ID,
))
ws = WebSiteManagementClient(WebSiteManagementClientConfiguration(
    credentials=CREDENTIALS,
    subscription_id=SUBSCRIPTION_ID,
))


#################################################
# Create a resource group
#
# A resource group contains our entire deployment
# and makes it easy to manage related services.

print("Creating resource group:", RESOURCE_GROUP)

from azure.mgmt.resource.resources.models import ResourceGroup
rc.resource_groups.create_or_update(RESOURCE_GROUP, ResourceGroup(location=LOCATION))

#################################################
# Deploy a resource manager template
#
#
print("Deploying:", DEPLOYMENT)

TEMPLATE = {
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "siteName": { "type": "string" },
        "hostingPlanName": { "type": "string" },
        "storageName": { "type": "string" },
        "siteLocation": { "type": "string" },
        "repoUrl": { "type": "string" },
    },
    "resources": [
        # Create a server farm for us to run our web site in
        {
            "apiVersion": "2015-08-01",
            "name": "[parameters('hostingPlanName')]",
            "type": "Microsoft.Web/serverfarms",
            "location": "[parameters('siteLocation')]",
            "sku": { "name": "F1" },
        },
        # Create a storage account for our table
        {
            "apiVersion": "2015-05-01-preview",
            "name": "[parameters('storageName')]",
            "type": "Microsoft.Storage/storageAccounts",
            "location": "[parameters('siteLocation')]",
            "properties": {
                "accountType": "Standard_LRS"
            }
        },
        # Create and configure our web site
        {
            "apiVersion": "2015-08-01",
            "name": "[parameters('siteName')]",
            "type": "Microsoft.Web/sites",
            "location": "[parameters('siteLocation')]",
            "dependsOn": [ "[resourceId('Microsoft.Web/serverfarms', parameters('hostingPlanName'))]" ],
            "properties": {
                "serverFarmId": "[parameters('hostingPlanName')]",
            },
            "resources": [
                # Configure appsettings for the website
                {
                    "apiVersion": "2015-08-01",
                    "name": "appsettings",
                    "type": "config",
                    "dependsOn": [
                        "[resourceId('Microsoft.Web/Sites', parameters('siteName'))]",
                        "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageName'))]",
                    ],
                    "properties": {
                        "COMPANY_NAME": COMPANY_NAME,

                        # Include the name and key from the storage account we
                        # created above.
                        "STORAGE_ACCOUNT_NAME": "[parameters('storageName')]",
                        "STORAGE_ACCOUNT_KEY": "[listkeys(" +
                        "resourceId('Microsoft.Storage/storageAccounts', parameters('storageName')), " +
                            "providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]" + 
                        ").key1]",
                    }
                },
                # Configure deployment from source control
                {
                    "apiVersion": "2015-08-01",
                    "name": "web",
                    "type": "sourcecontrols",
                    "dependsOn": [ 
                        "[resourceId('Microsoft.Web/Sites', parameters('siteName'))]",
                        "[resourceId('Microsoft.Web/Sites/config', parameters('siteName'), 'appSettings')]",
                    ],
                    "properties": {
                        "repoUrl": "[parameters('repoUrl')]",
                        "branch": "master",
                        "isManualIntegration": True,
                    }
                },
            ]
        },
    ]
}

PARAMETERS = {
    "siteLocation": { "value": "West US" },
    "hostingPlanName": { "value": "InternalApps" },
    "siteName": { "value": WEBSITE },
    "storageName": { "value": STORAGE },
    "repoUrl": { "value": WEBSITE_SOURCE },
}

from azure.mgmt.resource.resources.models import DeploymentProperties, DeploymentMode
rc.deployments.create_or_update(
    RESOURCE_GROUP,
    DEPLOYMENT,
    properties=DeploymentProperties(
        mode=DeploymentMode.incremental,
        template=TEMPLATE,
        parameters=PARAMETERS,
    )
).wait()

#################################################
# Get our website's URL
#
# The URL is generally predictable, but may be
# affected by configuration in the template.

conf = ws.sites.get_site(RESOURCE_GROUP, WEBSITE)
print('Site is available at:')
for name in conf.host_names:
    print('   ', name)

if input("Browse to {}? [y/N] ".format(conf.host_names[0])):
    import webbrowser
    webbrowser.open(conf.host_names[0])

#################################################
# Delete the resource group
#
# This quickly cleans up all of our resources.

if input("Delete resource group? [y/N] "):
    rc.resource_groups.delete(RESOURCE_GROUP).wait()

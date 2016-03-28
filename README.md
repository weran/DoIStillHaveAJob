# DoIStillHaveAJob

This project is a sample of using Azure Resource Management (ARM) deployment of a Python-based web site.

See `deploy.py` for the deployment script. This script creates a resource group with a storage account and web site, configures the site to pull from this github repository, and provides the storage access key to the site via an environment variable.

To run the script, you will need to update it to include credentials and an Azure subscription.

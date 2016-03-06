"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

import os
import sys
from bottle import default_app

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    import bottle
    bottle.debug(True)

import routes

if __name__ == '__main__':
    import bottle
    @bottle.route('/static/<filename:re:.*\.css>')
    def static_css(filename):
        return bottle.static_file(filename, root='static')

    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    bottle.run(server='wsgiref', host=HOST, port=PORT)

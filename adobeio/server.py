import argparse
import json
import logging
import os
import urllib
from os.path import expanduser
from .ims import IMS
from requests import HTTPError

import flask
import requests

# Start flask app
app = flask.Flask(__name__)


@app.route('/')
def home():
    return flask.render_template('index.html')


@app.route('/authorize')
def authorize():
    authorization_url = app.config['ims_client'].generate_authorize_url(
        app.config['scopes'], app.config['DEF_REDIRECT_URI'] + '/callback')

    # This will prompt users with the approval page if consent has not been given
    # Once permission is provided, users will be redirected to the specified page
    return flask.redirect(authorization_url)


@app.route('/callback')
def callback():
    error = flask.request.args.get('error', None)
    if error is not None:
        return flask.render_template('index.html', response='Failed with ' + error)

    # Retrive the authorization code from callback
    authorization_code = flask.request.args.get('code')

    try:
        # Get the token data
        token = app.config['ims_client'].token(authorization_code)

        # If an output file is specified, save the token data there.
        if 'output' in app.config:
            logging.info('Saving token data to ' + app.config['output'])
            with open(app.config['output'], 'w') as f:
                json.dump(token, f)
        
        flask.session['credentials'] = token

        return flask.render_template('index.html', response='login success')
    except HTTPError:
        logging.exception('Could not get access token for user')
        return flask.render_template('index.html', response='login failed')


@app.route('/profile')
def profile():
    if 'credentials' not in flask.session:
        return flask.render_template('index.html', response='Please log in first')

    try:
        userinfo = app.config['ims_client'].userinfo(flask.session['credentials']['access_token'])
        return flask.render_template('index.html', response=json.dumps(userinfo))
    except HTTPError:
        logging.exception('Could not get profile')
        return flask.render_template('index.html', response='profile could not be retrieved')
            


def load_config(config_file):
    with open(config_file, 'r') as f:
        app.config.update(json.load(f))


def main():

    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='A simple http server for getting, saving, and refreshing adobe io tokens.')

    parser.add_argument('-c', '--config', default='/etc/adobeio.config.json',
                        help='The json file to load with your app credentials (from https://console.adobe.io/). Default: /etc/adobeio.config.json.')
    parser.add_argument('--cert', default='cert.pem',
                        help='The path to the cert file for ssl.')
    parser.add_argument('--key', default='key.pem',
                        help='The path to the key file for ssl.')
    parser.add_argument('--secret', default=None,
                        help='The flask secret to use. If unset, a random one is generated')
    parser.add_argument('-s', '--scopes', type=str, default='openid,creative_sdk',
                        help='The scopes to request for the app.')
    parser.add_argument('--host', type=str, default='localhost',
                        help='The host to start the server on.')
    parser.add_argument('-p', '--port', type=str, default='443',
                        help='The port to start the server on.')
    parser.add_argument('-d', '--debug', dest='debug',
                        help='Sets the flask app to debug mode', action='store_true')
    parser.add_argument('-o', '--output', default=None,
                        help='Where the token is written to upon success')

    parser.set_defaults(debug=False)

    args = parser.parse_args()

    # Load the config file
    load_config(args.config)
    app.config['scopes'] = args.scopes
    if args.output:
        app.config['output'] = args.output

    # Create an IMS client
    app.config['ims_client'] = IMS(
        app.config['API_KEY'], app.config['CLIENT_SECRET'])

    if args.secret:
        app.secret_key = args.secret
    else:
        app.secret_key = os.urandom(16)

    # Start the server
    app.run(args.host, args.port, debug=args.debug,
            ssl_context=(args.cert, args.key))

if __name__ == '__main__':
    main()
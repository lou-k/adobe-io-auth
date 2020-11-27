import argparse
import json
import logging
import os
from datetime import datetime

from .ims import IMS


def load_json(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def main():

    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Refreshes a token file with the refresh_token if needed')

    parser.add_argument('-c', '--config', default='/etc/adobeio.config.json', required=True,
                        help='The json file to load with your app credentials (from https://console.adobe.io/). Default: /etc/adobeio.config.json.')
    parser.add_argument('-t', '--token', required=True,
                        help='The token json file written by the server.')

    args = parser.parse_args()

    app_config = load_json(args.config)
    token_config = load_json(args.token)

    # Check if the token is expired.
    is_expired = True
    if 'expires' in token_config:
        expires = datetime.fromisoformat(token_config['expires'])
        is_expired = expires < datetime.today()

    # If not, exit.
    if not is_expired:
        logging.info('Token does not expire until ' + expires)
        return

    # Otherwise refresh it
    ims = IMS(app_config['API_KEY'], app_config['CLIENT_SECRET'])
    new_token = ims.refresh(token_config['refresh_token'])

    # Save the results
    logging.info(
        f'Saving new token to {args.token} that expires on ' + new_token['expires'])
    with open(args.token, 'w') as f:
        json.dump(new_token, f)


if __name__ == '__main__':
    main()

# adobe-io-auth
A simple webserver for authenticating with Adobe IO.

It's based off of the [Adobe's python example](https://github.com/AdobeDocs/adobeio-auth/tree/stage/OAuth/samples/adobe-auth-python), but adds some niceties I needed for my [Lightroom Sync](https://github.com/lou-k/lightroom-cc-api) app.

This code is helpful if, like me, you're hitting Adobe API's for a hobby projects and you don't intend to have any extra users of your project.

## Installation



## Installation
From the repository:
```
pip install .
```

As a package:
```
pip install git+https://github.com/lou-k/adobe-io-auth.git@VERSION
```

## Generating an Acess Token


### Configuring Your Project
First, create a new project at https://developer.adobe.com/console/ with the scopes that you need.

Next, go to the "OAuth Web" page and set the redirect URI to `https://localhost:8443`.

Third, go to the project's page, and click "Download" to get the json file with `CLIENT_SECRET`, `API_KEY`, etc.

### Generate the SSL Certs

Run the following in your root directory:

```
$ openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

(see [adobe example](https://github.com/AdobeDocs/adobeio-auth/tree/stage/OAuth/samples/adobe-auth-python#createanopensslcert) for more info or use [this handy guide](https://betterprogramming.pub/trusted-self-signed-certificate-and-local-domains-for-testing-7c6e6e3f9548) to self-sign and install your root cert).

### Launch the Server

Launch the server:
```console
adobe-io-server -c <your_downloaded_file.json> -c <scopes> -o token.json
```

or if running without installing:

```
PYTHONPATH=. python -m adobeio.server -c <your_downloaded_file.json> -p 8443 -s <scopes> -o token.json
```

Where:
`<scopes>` is a comma-separated list of scopes you need for your application.

So, for example, to get access to lightroom:
```
PYTHONPATH=. python -m adobeio.server -c <your_downloaded_file.json> -p 8443 -s openid,offline_access,lr_partner_apis -o token.json
```

The flask server will attempt to launch on the url specified in the `DEF_REDIRECT_URI` field of your project. Visit that URL in your browser to authenticate.

## Features
* If you specify a file in the `--output` option, the app will save the user token there. This is useful if you're developing an app or using it in a hobby project.
* A partial IMS client (see below)
* Lets you set options via command line flags (see `server --help` for all options)

## Other Commands
The `adobe-io-refresh-token` command takes a saved token file from the server and refreshes it. This is useful if you're automating anything.

## IMS Usage
Included in this project is a partial implementation of the [IMS](https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/Resources/IMS.md) api.

A simple example:
```python
from adobeio import IMS

api_client = IMS(client_id, client_secret)
api_client.userinfo(access_token)
```

## [LICENSE](LICENSE)

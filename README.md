# adobe-io-auth
A simple webserver for authenticating with Adobe IO.

It's based off of the [Adobe's python example](https://github.com/AdobeDocs/adobeio-auth/tree/stage/OAuth/samples/adobe-auth-python), but adds some niceties I needed for my [Lightroom Sync](https://github.com/lou-k/lightroom-cc-api) app.

This code is helpful if, like me, you're hitting Adobe API's for a hobby projects and you don't intend to have any extra users of your project.

## Installation
```console
pip install .
```

## Server Usage

* First, make sure you have generated the OpenSSL certs as specified by the [adobe example](https://github.com/AdobeDocs/adobeio-auth/tree/stage/OAuth/samples/adobe-auth-python#createanopensslcert)
* Go to your project page on https://console.adobe.io/ and click the `Download` button to save your app's config to disk.
* Launch the server:
```console
adobe-io-server --config your_downloaded_file.json --debug
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
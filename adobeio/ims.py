
import datetime
import urllib

import requests


class IMS:
    """
    Implements the adobe IMS api. See:
    https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/OAuth/OAuth.md
    https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/Resources/IMS.md
    """

    def __init__(self, client_id: str, client_secret: str, base: str = 'https://ims-na1.adobelogin.com/ims/', session: requests.Session = None):
        """Creates a new instance of the IMS API client.

        Args:
            client_id (str): The client id of your application
            client_secret (str): Your app's client secret
            base (str, optional): The base url for the service. Defaults to 'https://ims-na1.adobelogin.com/ims/'.
            session (requests.Session, optional): A requests session object to use. If None, a new one is created.
        """
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session
        self.base = base
        self.client_id = client_id
        self.client_secret = client_secret

    def generate_authorize_url(self, scopes: str, redirect_uri: str, response_type: str = 'code'):
        """Generates the `authorization url <https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/OAuth/OAuth.md#authorization>_`
            that you should redirect your user to for oauth. If successful, they'll be logged in and redirected to your callback endpoint.

        Args:
            scopes (str): The `oauth scopes <https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/OAuth/Scopes.md>_` you are requesting. 
            redirect_uri (str): The url that the user should be redirected to for your app's callback. 
            response_type (str, optional): Defaults to 'code' but other values are possible. See the authorization doc.

        Returns:
            str: A URL to redirect your users to for oath,
        """
        params = {
            'client_id': self.client_id,
            'scope': scopes,
            'response_type': response_type,
            'redirect_uri': redirect_uri
        }
        return self.base + 'authorize/v2?' + urllib.parse.urlencode(params)

    def _token(self, **kwargs):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            **kwargs
        }
        resp = self.session.post(self.base + 'token/v3',
                                 params=params,
                                 headers={'content-type': 'application/x-www-form-urlencoded'})
        resp.raise_for_status()
        res = resp.json()

        # Compute the expiration date and time
        now = datetime.datetime.today()
        if 'expires_in' in res:
            expires = now + datetime.timedelta(seconds=res['expires_in'])
            res['expires'] = expires.isoformat()

        return res

    def token(self, code: str):
        """Retrieves an access token for a user.

        Args:
            code (str): The code returned to the oath callback url.

        Returns:
            dict: A dictionary with the following fields:
                access_token	Generated access token
                refresh_token	Generated refresh token (if the offline_access scope was requested)
                token_type      Token type will always be bearer.
                id_token        Generated ID token.
                expires_in      Number of seconds from now when the token expires
                expired         An ISO formatted datetime of when the token expires.
        """
        return self._token(code=code, grant_type='authorization_code')

    def refresh(self, refresh_token: str):
        """Refreshes an access token.

        Args:
            refresh_token (str): The refresh token returned by :func:`~adobeio.ims.IMS.token`

        Returns:
            dict: A dictionary with the same fields as :func:`~adobeio.ims.IMS.token`.
        """
        return self._token(refresh_token=refresh_token, grant_type='refresh_token')

    def userinfo(self, access_token: str):
        """Get's the users info

        Args:
            access_token (str): The user's access token returned by :func:`~adobeio.ims.IMS.token`

        Returns:
            dict: A dictionary with `user information <https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/Resources/IMS.md#userinfo>_`
        """
        params = {
            'client_id': self.client_id
        }
        resp = self.session.get(self.base + 'userinfo',
                                params=params,
                                headers={'Authorization': 'Bearer {}'.format(access_token)})
        resp.raise_for_status()
        return resp.json()

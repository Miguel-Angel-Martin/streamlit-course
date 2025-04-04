# Why the fuck cant httpx use the OS certificate store by default instead of certifi
# This would have avoided many headaches with the stupid 
# "certificate verify failed: unable to get local issuer certificate" error
#import truststore
#truststore.inject_into_ssl()
from httpx_oauth.oauth2 import OAuth2
#from ldap3 import Server, Connection, SAFE_SYNC, ALL_ATTRIBUTES

import streamlit as st
from typing import List, Dict, Tuple, Callable

DEFAULT_OAUTH_AUTHORIZE_ENDPOINT = "https://auth.avl.com:443/auth/oauth2/user/authorize"
DEFAULT_OAUTH_ACCESS_TOKEN_ENDPOINT = "https://auth.avl.com:443/auth/oauth2/user/access_token"
DEFAULT_OAUTH_REFRESH_TOKEN_ENDPOINT = "https://auth.avl.com:443/auth/oauth2/user/access_token"
DEFAULT_OAUTH_REVOKE_TOKEN_ENDPOINT = "https://auth.avl.com:443/auth/oauth2/user/token/revoke"
DEFAULT_OAUTH_USERINFO_ENDPOINT = "https://auth.avl.com:443/auth/oauth2/user/userinfo"

DEFAULT_LDAP_HOST = "avl01.avlcorp.lan"
DEFAULT_LDAP_BASE_DN = "dc=avl01,dc=avlcorp,dc=lan"

async def get_user_auth(
        authorizeFunc : Callable[[str], str],
        redirectURL : str,
        clientID : str,
        clientSecret : str,
        authorizeEndpoint : str = DEFAULT_OAUTH_AUTHORIZE_ENDPOINT,
        accessTokenEndpoint : str = DEFAULT_OAUTH_ACCESS_TOKEN_ENDPOINT,
        refreshTokenEndpoint : str = DEFAULT_OAUTH_REFRESH_TOKEN_ENDPOINT,
        revokeTokenEndpoint : str = DEFAULT_OAUTH_REVOKE_TOKEN_ENDPOINT,
        userinfoEndpoint : str = DEFAULT_OAUTH_USERINFO_ENDPOINT
    ) -> Tuple[str, str, str]:
    """
    Helper to perform oauth authentication. 
    Run with asyncio.run().

    Args:
        authorizeFunc: this is a callback to a function that takes 
            an url as a parameter and will:
            1. Check if the web app has received a parameter called "code"
               in its url parameters
            2. If it hasn't been received send the user to the given url
            3. Otherwise return the code
        redirectURL: after sending the user in authorizeFunc() where
            should the server redirect back. You probably want this to
            point to your web page.

        The rest of arguments are parameters of your oauth client and server.

    Returns:
        4 strings: user, given name, family name and email

    Raises:
        GetAccessTokenError: An error occurred while getting the access token.
        HTTPStatusError: An error occurred while getting the user info.

    Example:
        name, given_name, family_name, email = get_user_auth(
            my_redirect_func,
            http://localhost:8501/,
            "awesome_app",
            "very secret"
        )
    """

    # Flow
    # client                                                      server
    #   | authorize_endpoint (params=redirect_url, client_id, scope) |
    #   | ---------------------------------------------------------> |
    #   |                                                            |
    #   | redirect_url (params=code)                                 |
    #   | <--------------------------------------------------------- |
    #   |                                                            |
    #   | access_token_endpoint (request_data=redirect_url, code)    |
    #   | ---------------------------------------------------------> |
    #   |                                                            |
    #   | access_token                                               |
    #   | <--------------------------------------------------------- |
    #Where to obtain info about endpoints:
    #https://auth9.avl.com/auth/oauth2/realms/user/.well-known/openid-configuration

    # Create the oauth client
    client = OAuth2(
        client_id = clientID,
        client_secret =  clientSecret,
        authorize_endpoint = authorizeEndpoint,
        access_token_endpoint = accessTokenEndpoint,
        refresh_token_endpoint = refreshTokenEndpoint,
        revoke_token_endpoint = revokeTokenEndpoint,
        name = "avl",
        base_scopes = ["openid", "profile", "email"],
        token_endpoint_auth_method = "client_secret_basic",
        revocation_endpoint_auth_method = "client_secret_basic",
    )

    # Returns something like this:
    # https://auth9.avl.com:443/auth/oauth2/user/authorize?response_type=code&client_id=ibe-ai-rag&redirect_uri=https%3A%2F%2FESBOEWD110240.avl01.avlcorp.lan%2Fopenid%2Fcallback&scope=openid+email
    # This url contains the parameters (everything after the ?) 
    # we need to send to the oauth server to get our authorization code, 
    # which we will later exchange with the access token that contains user info
    #
    # What we will do is redirect the user to this url, and the server
    # will go back to us (with the url specified as redirect_uri, check the 
    # params in the above example). Inside the url the server uses to go back
    # the code will be contained in its parameters
    authorizationURL = await client.get_authorization_url(
        redirectURL,
    )

    code = authorizeFunc(authorizationURL)

    # We have the code, now exchange it with the token that contains the data
    token = await client.get_access_token(
        code, redirectURL
    )

    # The token itself does not contain all info, we have to manually make
    # an additional call.
    # This is based on the google client integration of the library 
    # (get_id_email() function)
    # https://github.com/frankie567/httpx-oauth/blob/master/httpx_oauth/clients/google.py
    async with client.get_httpx_client() as httpx_client:
        response = await httpx_client.get(
            # The endpoint to get the additional data from
            userinfoEndpoint,
            headers = { "Authorization" : f"Bearer {token['access_token']}" },
        )

    if response.status_code != 200:
        response.raise_for_status()

    #Read data recieved from server
    return (
        response.json()["sub"], 
        response.json()["given_name"], 
        response.json()["family_name"],
        response.json()["email"]
    )

def get_user_groups_and_account(
        user : Tuple[str, str], 
        ldapAccount : str,
        ldapPass : str,
        ldapBaseDn : str = DEFAULT_LDAP_BASE_DN,
        ldapHost : str = DEFAULT_LDAP_HOST,
    ) -> List[str]:
    """
    Finds which groups the given user is a member of and its account
    name (the sAMAccountName attribute inside ldap)

    Args:
        user: The given name and family name of the user to search.
        ldapHost: Optional. Where is the ldap server located.
        ldapAccount: Optional. With which ldap account search in the given server.
        ldapPass: Optional. The password of the ldap account.

    Returns:
        A list of strings with the groups of the user and its account name

    Raises:
        ConnectionError: could not stablish the connection to the server.

    Examples:
        st.session_state["user_groups"], st.session_state["account"] = \
            get_user_groups(st.session_state["user_name"])
    """

    server = Server(ldapHost, get_info = "ALL")
    conn = Connection(
        server, 
        ldapAccount, 
        ldapPass, 
        client_strategy = SAFE_SYNC
    ) 
    if not conn.bind():
        raise ConnectionError(conn.result)

    searchFilter = f"(&(givenName={user[0]})(sn={user[1]}))"
    results = conn.search(
        ldapBaseDn, 
        searchFilter, 
        attributes = ["memberOf", "sAMAccountName"] #Attributes to return
    )

    #results[0] and results[1] contain some metadata about the query
    if results[0] != True:
        raise ConnectionError("Cannot get ldap information")
    
    #If no user was found return empty list
    if "attributes" not in results[2][0]:
        return [], user

    #print("\n\n\nAttr " + str(results[2][0]["attributes"]))
    accountName = user 
    if "sAMAccountName" in results[2][0]["attributes"]:
        accountName = results[2][0]["attributes"]["sAMAccountName"]

    groupNames = []
    if "memberOf" in results[2][0]["attributes"]:
        #This only contains the complete path to the groups the user is a member of...
        #We need to extract the names
        groupDNs = results[2][0]["attributes"]["memberOf"]
        for dn in groupDNs: 
            #Example group DN:
            #CN=Global-License-Exclaimer,OU=FIM,OU=GROUPS,OU=GRZ,OU=LIST,OU=AT,OU=AVL,DC=avl01,DC=avlcorp,DC=lan
            #The name is Global-License-Exclaimer, and all group DNs have the same format
            groupNames.append(dn[dn.find('=')+1:dn.find(',')])

    return groupNames, accountName

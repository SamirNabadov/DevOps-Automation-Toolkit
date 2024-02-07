from core.settings.config_variables import GitlabEnvConf, PathConf
from urllib3 import disable_warnings, exceptions
import gitlab, logging
from os import system
from hvac import Client

# Disabling GitLab warnings due to self-signed certificate usage
disable_warnings(exceptions.InsecureRequestWarning)

class GitlabAuth:
    """
    Class for handling GitLab authentication and creating a session instance.
    """

    @staticmethod
    def connect(ssl_verify: bool, gitlab_server: str, token: str, api_version: str) -> gitlab.Gitlab:
        """
        Establishes a connection to a GitLab server.

        Parameters:
        ssl_verify (bool): Whether to verify SSL certificate.
        gitlab_server (str): URL of the GitLab server.
        token (str): Private token for GitLab authentication.
        api_version (str): GitLab API version.

        Returns:
        gitlab.Gitlab: An authenticated session to the GitLab server.

        Raises:
        RuntimeError: If GitLab token authentication fails.
        """
        # Creating a GitLab session
        gitlab_session = gitlab.Gitlab(url=gitlab_server,
                                       private_token=token,
                                       ssl_verify=ssl_verify,
                                       api_version=api_version)
        # Authenticating the session
        gitlab_session.auth()
        try:
            # Checking if the session can access GitLab version information
            gitlab_session.version()
        except gitlab.exceptions.GitlabAuthenticationError:
            # Raising an error if authentication fails
            raise RuntimeError("Invalid or missing GITLAB TOKEN")

        logging.info("Connected to: %s", gitlab_server)
        return gitlab_session

class VaultAuth:
    """
    Class for handling Vault authentication and creating a client instance.
    """

    @staticmethod
    def connect(url: str, token: str, verify: bool) -> Client:
        """
        Establishes a connection to a Vault server.

        Parameters:
        url (str): URL of the Vault server.
        token (str): Token for Vault authentication.
        verify (bool): Whether to verify SSL certificate.

        Returns:
        hvac.Client: An authenticated client to the Vault server.
        """
        # Creating a Vault client instance
        client = Client(url=url, token=token, verify=verify)
        return client


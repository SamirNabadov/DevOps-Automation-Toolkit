from core.settings.config_variables import GitlabEnvConf, VaultAuthConf
import hvac

class EnvironmentValidator:
    """
    A class to validate various environment and configuration settings.
    It ensures that necessary external connections and configurations are properly set up.
    """

    @staticmethod
    def _check_vault_connection() -> None:
        """
        Validates the connection to the Vault server.
        Exits the process if the Vault server is unreachable.
        """
        client = hvac.Client(url=VaultAuthConf.VAULT_URL, token=VaultAuthConf.VAULT_TOKEN, verify=VaultAuthConf.VAULT_SSL_VERIFY)
        if not client.is_authenticated():
            print("Vault is unreachable!")
            exit(1)

    @staticmethod
    def check_environment() -> None:
        """
        Performs checks on various environment settings, including the connection to the Vault server
        and the presence of essential GitLab configuration parameters.
        Exits the process if any check fails.
        """
        EnvironmentValidator._check_vault_connection()
        
        # Check for conflicts in project name and group name
        if GitlabEnvConf.CI_SUBGROUP_NAME is None or GitlabEnvConf.CI_PROJECT_NAME is None:
            exit("Group or Project name can not be null!")

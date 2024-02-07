from hvac.exceptions import InvalidPath
from base64 import b64encode
from typing import Optional, Tuple, Any, Dict

from core.authentication.auth_manager import VaultAuth
from core.settings.config_variables import VaultAuthConf
from core.operation.template_handler import TemplateGenerator

class VaultManager:
    """
    This class manages interactions with HashiCorp's Vault, including policy and secret management.

    Methods in this class allow for the creation of policies, roles, and handling secret IDs within Vault.
    """

    def __init__(self) -> None:
        """
        Initializes the VaultManager by setting up a Vault client instance with the specified configuration.
        """
        # Initialize Vault client instance using configuration variables
        self.client = VaultAuth.connect(VaultAuthConf.VAULT_URL, VaultAuthConf.VAULT_TOKEN, VaultAuthConf.VAULT_SSL_VERIFY)

    def _create_policy(self, policy_name: str, policy_rules: str) -> Optional[Any]:
        """
        Creates or updates a policy in Vault.

        Args:
            policy_name (str): The name of the policy to create or update.
            policy_rules (str): The rules that define the policy.

        Returns:
            Optional[Any]: The result of policy creation or update, None if an error occurred.
        """
        try:
            # Attempt to create or update the specified policy
            self.client.sys.create_or_update_policy(name=policy_name, policy=policy_rules)
        except Exception as e:
            print(f"Error creating policy: {e}")
            return None

    def _create_or_get_role_id(self, role_name: str, policy_name: str) -> str:
        """
        Creates a new AppRole or retrieves the existing one from Vault.

        Args:
            role_name (str): The name of the role to create or retrieve.
            policy_name (str): The name of the policy to associate with the role.

        Returns:
            str: The role ID.
        """
        try:
            # Check if the role already exists and retrieve its ID
            role_id_response = self.client.auth.approle.read_role_id(role_name=role_name)
            role_id: str = role_id_response['data']['role_id']
            #print('Vault Role ID already exists, using existing role.')
        except InvalidPath:
            # Create a new role if it doesn't exist
            print("Vault Role does not exist, creating a new one...")
            self.client.auth.approle.create_or_update_approle(role_name=role_name, token_policies=[policy_name], token_type='service')
            role_id_response = self.client.auth.approle.read_role_id(role_name=role_name)
            role_id = role_id_response['data']['role_id']
        return role_id

    def _generate_secret_id_and_login(self, role_name: str, role_id: str) -> Tuple[str, str]:
        """
        Generates a secret ID for an AppRole and performs a login to receive a client token.

        Args:
            role_name (str): The name of the AppRole.
            role_id (str): The ID of the AppRole.

        Returns:
            Tuple[str, str]: A tuple containing the secret ID and the client token.
        """
        # Generate a secret ID for the role
        secret_id_response = self.client.auth.approle.generate_secret_id(role_name=role_name)
        secret_id: str = secret_id_response["data"]["secret_id"]
        
        # Perform a login with the role ID and secret ID to get a client token
        login_response = self.client.auth.approle.login(role_id=role_id, secret_id=secret_id)
        client_token: str = login_response['auth']['client_token']
        print(f"Vault Client Token: {client_token}")
        return secret_id, client_token

    def generate_vault_secret(self, group_name: str, environment_name: str, namespace: str) -> str:
        """
        Generates a Vault secret for a specified group, environment, and namespace.

        Args:
            group_name (str): The name of the group for which the secret is being generated.
            environment_name (str): The environment name.
            namespace (str): The namespace for the secret.

        Returns:
            str: The Kubernetes secret YAML containing the Vault secret.
        """
        # Define policy name based on group and environment
        policy_name: str = f'{group_name}_{environment_name}_policy'
        
        # Generate policy rules JSON using TemplateGenerator
        policy_rules: str = TemplateGenerator.generate_vault_policy_json(group_name, environment_name)
        
        # Create or update the policy in Vault
        self._create_policy(policy_name, policy_rules)
        
        # Define role name and create or retrieve the role ID
        role_name: str = f'{group_name}_{environment_name}_role'
        role_id: str = self._create_or_get_role_id(role_name, policy_name)
        
        # Generate a secret ID and perform login to receive a client token
        secret_id, _ = self._generate_secret_id_and_login(role_name, role_id)
        
        # Encode the ROLE_ID and SECRET_ID to ensure safe transmission/storage
        encoded_role_id: str = b64encode(role_id.encode()).decode()
        encoded_secret_id: str = b64encode(secret_id.encode()).decode()
        
        # Generate the Kubernetes secret YAML using TemplateGenerator
        # This YAML can be used to store the secret in a Kubernetes environment
        secret_yaml: str = TemplateGenerator.generate_vault_k8s_secret(group_name, namespace, encoded_role_id, encoded_secret_id)
        return secret_yaml

    def write_secret_to_vault(self, mount_point: str, secret_path: str, secret_key: str, secret_value: str) -> None:
        """
        Appends or creates a secret to the specified path in Vault for the KV version 1 secret engine.
        Also ensures that the client is connected to Vault.

        Args:
            mount_point (str): The mount point where the KV version 1 secret engine is enabled.
            secret_path (str): The path where the secret will be written.
            secret_key (str): The key name of the secret.
            secret_value (str): The value of the secret.

        Returns:
            None
        """
        # Reinitialize Vault client instance
        self.client = VaultAuth.connect(VaultAuthConf.VAULT_URL, VaultAuthConf.VAULT_TOKEN, VaultAuthConf.VAULT_SSL_VERIFY)

        try:
            # Try to read the existing secret
            existing_data = self.client.secrets.kv.v1.read_secret(mount_point=mount_point, path=secret_path)['data']
        except InvalidPath:
            # If the path does not exist, initialize as empty
            existing_data = {}
            print("No existing data found, initializing new secret.")

        # Update existing data with the new key-value pair
        updated_data = {**existing_data, secret_key: secret_value}

        # Write the updated data back to the Vault
        write_response = self.client.secrets.kv.v1.create_or_update_secret(mount_point=mount_point, path=secret_path, secret=updated_data)
        print(f"Secret written/appended to {mount_point}/{secret_path} successfully.")



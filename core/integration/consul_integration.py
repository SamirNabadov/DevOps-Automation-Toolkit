import requests
import json
from typing import Optional, Dict, List, Any
from core.operation.template_handler import TemplateGenerator

class ConsulManager:
    """
    This class manages interactions with a Consul server, allowing for the creation and management of policies and tokens.

    Attributes:
        url (str): The URL of the Consul server.
        token (str): The access token for the Consul server.
        headers (Dict[str, str]): Headers to include in requests to the Consul server.
        verify_ssl (bool): Whether to verify SSL certificates when making requests.
    """

    def __init__(self, url: str, token: str, verify_ssl: bool = False) -> None:
        """
        Initializes the ConsulManager with the given URL, token, and SSL verification preference.

        Args:
            url (str): The URL of the Consul server.
            token (str): The access token for the Consul server.
            verify_ssl (bool): Whether to verify SSL certificates. Defaults to False.
        """
        self.url = url
        self.token = token
        self.headers = {
            "X-Consul-Token": token,
            "Content-Type": "application/json"
        }
        self.verify_ssl = verify_ssl

    def _get_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a policy by name from the Consul server.

        Args:
            name (str): The name of the policy to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The policy data if found, None otherwise.
        """
        response = requests.get(f"{self.url}/v1/acl/policies", headers=self.headers, verify=self.verify_ssl)
        response.raise_for_status()
        policies = response.json()
        for policy in policies:
            if policy['Name'] == name:
                return policy
        return None

    def _create_policy(self, name: str, rules: str) -> Dict[str, Any]:
        """
        Creates a new policy or updates an existing one on the Consul server.

        Args:
            name (str): The name of the policy.
            rules (str): The rules of the policy in HCL format.

        Returns:
            Dict[str, Any]: The response from the Consul server.
        """
        existing_policy = self._get_policy(name)
        if existing_policy:
            #print(f"Policy '{name}' already exists.")
            return existing_policy

        acl_policy = {"Name": name, "Rules": rules}
        response = requests.put(f"{self.url}/v1/acl/policy", headers=self.headers, data=json.dumps(acl_policy), verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()

    def _get_tokens(self) -> List[Dict[str, Any]]:
        """
        Retrieves all tokens from the Consul server.

        Returns:
            List[Dict[str, Any]]: A list of tokens.
        """
        response = requests.get(f"{self.url}/v1/acl/tokens", headers=self.headers, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()

    def _token_exists(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Checks if a token with the given description exists.

        Args:
            description (str): The description of the token to find.

        Returns:
            Optional[Dict[str, Any]]: The token data if found, None otherwise.
        """
        tokens = self._get_tokens()
        for token in tokens:
            if token['Description'] == description:
                return token
        return None

    def _create_token(self, policies: Optional[List[str]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new token on the Consul server.

        Args:
            policies (Optional[List[str]]): A list of policy IDs to attach to the token.
            description (Optional[str]): A description for the token.

        Returns:
            Dict[str, Any]: The response from the Consul server.
        """
        existing_token = self._token_exists(description)
        if existing_token:
            print(f"Token with description '{description}' already exists.")
            return existing_token

        token_options = {
            "Description": description,
            "Policies": [{"ID": policy_id} for policy_id in (policies or [])]
        }
        response = requests.put(f"{self.url}/v1/acl/token", headers=self.headers, data=json.dumps(token_options), verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()

    def generate_consul_secret(self, group_name: str, namespace: str) -> str:
        """
        Generates a Consul secret for a specified group and namespace.

        Args:
            group_name (str): The name of the group.
            namespace (str): The namespace for the secret.

        Returns:
            str: The Kubernetes secret YAML for the Consul secret.
        """
        policy_name = group_name
        policy_rules = f'key_prefix "{policy_name}/" {{ policy = "write" }}'
        policy_response = self._create_policy(policy_name, policy_rules)
        policy_id = policy_response['ID']

        token_description = group_name
        token_response = self._create_token(policies=[policy_id], description=token_description)
        token_secret = token_response['SecretID']
        print("-------------------------------")
        print(f"Consul Client Token: {token_secret}")

        # Generate the Kubernetes secret YAML using TemplateGenerator
        secret_yaml = TemplateGenerator.generate_consul_k8s_secret(group_name, namespace, token_secret)
        
        return secret_yaml


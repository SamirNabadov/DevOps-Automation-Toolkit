import os
import yaml
import json
from base64 import b64encode
from core.settings.config_variables import GitlabEnvConf
from typing import Dict, Any

class TemplateGenerator:
    """
    TemplateGenerator provides static methods to generate various configuration templates in YAML and JSON formats.
    These templates are used for Kubernetes, ArgoCD, Vault, Consul, and GitLab CI configurations.
    """

    @staticmethod
    def generate_argocd_app_project_yaml(cd_subgroup_name: str, cd_helm_namespace: str) -> Dict[str, Any]:
        """
        Generates an ArgoCD AppProject YAML configuration file.

        Parameters:
        cd_subgroup_name (str): The name of the CD subgroup.
        cd_helm_namespace (str): The Kubernetes namespace for the Helm deployment.

        Returns:
        Dict[str, Any]: A dictionary representing the ArgoCD AppProject YAML configuration.
        """
        app_project = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "AppProject",
            "metadata": {
                "name": cd_subgroup_name,
                "namespace": "argocd",
                "finalizers": ["resources-finalizer.argocd.argoproj.io"]
            },
            "spec": {
                "description": f"{cd_subgroup_name} project",
                "sourceRepos": ["*"],
                "destinations": [{
                    "namespace": cd_helm_namespace,
                    "server": "https://kubernetes.default.svc"
                }],
                "clusterResourceWhitelist": [{"group": "", "kind": "Namespace"}],
                "namespaceResourceWhitelist": [{"group": "*", "kind": "*"}],
                "roles": [{
                    "name": f"{cd_subgroup_name}-application-admin",
                    "description": f"{cd_subgroup_name} team's deployment role",
                    "policies": [f"p, proj:{cd_subgroup_name}:{cd_subgroup_name}-application-admin, applications, *, {cd_subgroup_name}/*, allow"],
                    "groups": [f"{cd_subgroup_name}"]
                }],
                "orphanedResources": {
                    "warn": True
                }
            }
        }

        return app_project

    @staticmethod
    def generate_argocd_application_yaml(ci_server_host: str, cd_subgroup_name: str, ci_environment_name: str, 
                                          cd_helm_chart_name: str, ci_branch_name: str, 
                                          cd_group_name: str, cd_project_name: str, cd_helm_namespace: str) -> Dict[str, Any]:
        """
        Generates an ArgoCD Application YAML configuration file.

        Parameters:
        (All parameters are str): Various configuration parameters for the Application YAML.

        Returns:
        Dict[str, Any]: A dictionary representing the ArgoCD Application YAML configuration.
        """
        application = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": f"{ci_environment_name}-{cd_helm_chart_name}-{cd_subgroup_name}",
                "namespace": "argocd"
            },
            "spec": {
                "project": cd_subgroup_name,
                "source": {
                    "helm": {
                        "valueFiles": [f"{ci_branch_name}.yaml"]
                    },
                    "path": ".",
                    "repoURL": f"https://{ci_server_host}/{cd_group_name}/{cd_subgroup_name}/{cd_project_name}.git",
                    "targetRevision": ci_branch_name
                },
                "destination": {
                    "namespace": cd_helm_namespace,
                    "server": "https://kubernetes.default.svc"
                },
                "syncPolicy": {
                    "automated": {
                        "selfHeal": True,
                        "prune": True,
                        "allowEmpty": False
                    }
                }
            }
        }

        return application

    @staticmethod
    def generate_k8s_namespace_yaml(namespace: str) -> Dict[str, Any]:
        """
        Creates a Kubernetes namespace YAML file.

        Parameters:
        namespace (str): The name of the Kubernetes namespace.

        Returns:
        Dict[str, Any]: A dictionary representing the Kubernetes namespace YAML configuration.
        """
        # Create the namespace dictionary
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": namespace
            }
        }

        # Write the namespace to a YAML file
        return namespace
    
    @staticmethod
    def generate_gitlab_ci_yaml() -> Dict[str, Any]:
        """
        Generate the GitLab CI configuration data.

        Returns:
        Dict[str, Any]: A dictionary containing the GitLab CI configuration data.
        """
        return {
            "include": [
                {
                    "project": "devops/cicd-template/ci-template",
                    "file": "gitlab-ci-template.yml"
                }
            ],
            "variables": {
                "CI_BRANCHING_TYPE": f"{GitlabEnvConf.CI_BRANCHING_TYPE}",
                "CI_PROJECT_TYPE": f"{GitlabEnvConf.CI_PROJECT_TYPE}",
                "CI_PROJECT_TYPE_BACKEND_DMZ": f"{GitlabEnvConf.CI_PROJECT_TYPE_BACKEND_DMZ}",
                "CI_PROJECT_MODE": f"{GitlabEnvConf.CI_PROJECT_MODE}",
                "CI_APPLICATION_TYPE": f"{GitlabEnvConf.CI_APPLICATION_TYPE}",
                "CI_RELEASE_TYPE": f"{GitlabEnvConf.CI_RELEASE_TYPE}",
                "CI_CODE_STYLE": f"{GitlabEnvConf.CI_CODE_STYLE}",
                "CI_CODE_CHECK_SNYK": f"{GitlabEnvConf.CI_CODE_CHECK_SNYK}",
                "CI_PROJECT_TEST_STAGE": f"{GitlabEnvConf.CI_PROJECT_TEST_STAGE}",
                "CI_BACKEND_IMAGE_JRE": f"$CI_SERVER_HOST:4567/devops/image/openjdk:11-jre-slim",
                "CI_BACKEND_IMAGE_GRADLE": f"$CI_SERVER_HOST:4567/devops/image/openjdk:11-jdk-slim",
                "CI_BACKEND_IMAGE_MAWEN": f"$CI_SERVER_HOST:4567/devops/image/mawen:3.8.5-openjdk-11"
            }
        }

    @staticmethod
    def generate_k8s_regcred(docker_server: str, docker_username: str, docker_password: str, namespace: str) -> str:
        """
        Creates a Kubernetes Docker registry credentials secret in YAML format.

        Parameters:
        docker_server (str): Docker registry server.
        docker_username (str): Docker registry username.
        docker_password (str): Docker registry password.
        namespace (str): Kubernetes namespace where the secret will be used.

        Returns:
        str: A string representation of the Kubernetes secret in YAML format.
        """
        # Create the authentication string
        auth_string = b64encode(f"{docker_username}:{docker_password}".encode()).decode()
        
        # Create the secret content
        secret_content = {
            "auths": {
                docker_server + ":4567": {
                    "auth": auth_string
                }
            }
        }

        # Encode the secret content as base64
        data = {
            ".dockerconfigjson": b64encode(json.dumps(secret_content).encode()).decode()
        }

        # Create the secret
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "regcred",
                "namespace": namespace,
            },
            "data": data,
            "type": "kubernetes.io/dockerconfigjson"
        }

        # Serialize the dictionary to a YAML-formatted string
        return yaml.dump(secret)

    @staticmethod
    def generate_consul_k8s_secret(group_name: str, namespace: str, secret_id: str) -> str:
        """
        Creates a Kubernetes secret for Consul in YAML format.

        Parameters:
        group_name (str): The name of the group.
        namespace (str): Kubernetes namespace where the secret will be used.
        secret_id (str): The Secret ID to be encoded in the Kubernetes secret.

        Returns:
        str: A string representation of the Kubernetes secret in YAML format.
        """
        secret_id_encoded = b64encode(secret_id.encode()).decode()
        consul_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"consul-{group_name}",
                "namespace": namespace,
            },
            "type": "Opaque",
            "data": {"CONSUL_TOKEN": secret_id_encoded}
        }
        
        return yaml.dump(consul_secret)

    @staticmethod
    def generate_vault_k8s_secret(group_name: str, namespace: str, role_id: str, secret_id: str) -> str:
        """
        Creates a Kubernetes secret for Vault in YAML format.

        Parameters:
        group_name (str): The name of the group.
        namespace (str): Kubernetes namespace where the secret will be used.
        role_id (str): The Vault role ID.
        secret_id (str): The Vault secret ID.

        Returns:
        str: A string representation of the Kubernetes secret in YAML format.
        """
        encoded_role_id = b64encode(role_id.encode()).decode()
        encoded_secret_id = b64encode(secret_id.encode()).decode()

        vault_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"vault-{group_name}",
                "namespace": namespace,
            },
            "type": "Opaque",
            "data": {
                "VAULT_ROLE_ID": encoded_role_id,
                "VAULT_SECRET_ID": encoded_secret_id
            }
        }
        
        return yaml.dump(vault_secret)

    @staticmethod
    def generate_vault_policy_json(group_name: str, environment_name: str) -> str:
        """
        Generates a JSON representation of a Vault policy.

        Parameters:
        group_name (str): The name of the group.
        environment_name (str): The environment name (e.g., 'dev', 'prod').

        Returns:
        str: A string representation of the Vault policy in JSON format.
        """
        policy = {
            "path": {
                "secret/*": {"capabilities": ["list"]},
                f"secret/{group_name}/+/{environment_name}": {"capabilities": ["read", "list", "update", "create", "delete"]}
            }
        }
       
        return json.dumps(policy, indent=4)


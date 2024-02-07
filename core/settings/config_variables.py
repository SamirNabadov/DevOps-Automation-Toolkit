from core.utilities.command_executor import CommandManager
from os import getenv, getcwd
from typing import Optional, List

class GitlabAuthConf:
    """
    Configuration class for GitLab authentication details.
    It holds environment variables related to GitLab server configuration and access credentials.
    """

    CI_GITLAB_SERVER: Optional[str] = getenv("CI_SERVER_URL")
    CI_GITLAB_TOKEN_NAME: Optional[str] = getenv("CI_GITLAB_TOKEN_NAME")
    CI_GITLAB_TOKEN: Optional[str] = getenv("CI_GITLAB_TOKEN")
    CI_GITLAB_SSL_VERIFY: bool = False
    CI_GITLAB_API_VERSION: str = "4"
    CI_GITLAB_USERNAME: Optional[str] = getenv("CI_GITLAB_USERNAME")
    CI_GITLAB_PASSWORD: Optional[str] = getenv("CI_GITLAB_PASSWORD")

class GitlabEnvConf:
    """
    Configuration class for GitLab environment variables.
    It includes settings for project names, subgroup names, branching types, project modes, and other related configurations.
    These settings are typically used to configure CI/CD pipelines and deployment strategies.
    """
    CI_SUBGROUP_NAME: Optional[str] = getenv("CI_SUBGROUP_NAME").lower().strip() if getenv("CI_SUBGROUP_NAME") else None
    CI_PROJECT_NAME: Optional[str] = getenv("CI_PROJECT_NAME").lower().strip() if getenv("CI_PROJECT_NAME") else None
    CI_PROJECT_CREATION: Optional[str] = getenv("CI_PROJECT_CREATION")
    CI_BRANCHING_TYPE: Optional[str] = getenv("CI_BRANCHING_TYPE")
    CI_PROJECT_TYPE: Optional[str] = getenv("CI_PROJECT_TYPE")
    CI_PROJECT_TYPE_BACKEND_DMZ: Optional[str] = getenv("CI_PROJECT_TYPE_BACKEND_DMZ")
    CI_PROJECT_MODE: Optional[str] = getenv("CI_PROJECT_MODE")
    CI_PROJECT_MM_MODULE_NAME: Optional[str] = getenv("CI_PROJECT_MM_MODULE_NAME").lower() if getenv("CI_PROJECT_MM_MODULE_NAME") else None
    CI_PROJECT_MM_CODE_EXISTS: Optional[str] = getenv("CI_PROJECT_MM_CODE_EXISTS")
    CI_APPLICATION_TYPE: Optional[str] = getenv("CI_APPLICATION_TYPE")
    CI_APPLICATION_VERSION: Optional[str] = getenv("CI_APPLICATION_VERSION")
    CI_RELEASE_TYPE: Optional[str] = getenv("CI_RELEASE_TYPE")
    CI_CODE_STYLE: Optional[str] = getenv("CI_CODE_STYLE")
    CI_CODE_CHECK_SNYK: Optional[str] = getenv("CI_CODE_CHECK_SNYK")
    CI_PROJECT_TEST_STAGE: Optional[str] = getenv("CI_PROJECT_TEST_STAGE")
    CD_HELM_NAMESPACE: Optional[str] = getenv("CD_HELM_NAMESPACE").lower().strip() if getenv("CD_HELM_NAMESPACE") else None
    CD_HELM_PORT_POD_SVC_MGMT: Optional[str] = getenv("CD_HELM_PORT_POD_SVC_MGMT")
    CD_HELM_CONTAINER_PORT: Optional[str] = CD_HELM_PORT_POD_SVC_MGMT.split('|')[0].strip() if CD_HELM_PORT_POD_SVC_MGMT else None
    CD_HELM_SERVICE_PORT: Optional[str] = CD_HELM_PORT_POD_SVC_MGMT.split('|')[1].strip() if CD_HELM_PORT_POD_SVC_MGMT else None
    CD_HELM_MANAGEMENT_PORT: Optional[str] = CD_HELM_PORT_POD_SVC_MGMT.split('|')[2].strip() if CD_HELM_PORT_POD_SVC_MGMT else None
    CD_REPLICA_COUNT: Optional[str] = getenv("CD_REPLICA_COUNT")
    CD_REPLICA_COUNT_DEV: Optional[str] = CD_REPLICA_COUNT.split('|')[0].strip() if CD_REPLICA_COUNT else None
    CD_REPLICA_COUNT_PROD: Optional[str] = CD_REPLICA_COUNT.split('|')[1].strip() if CD_REPLICA_COUNT else None
    CD_HELM_DOMAIN: Optional[str] = getenv("CD_HELM_DOMAIN")
    CD_CLUSTER_TYPE: Optional[str] = getenv("CD_CLUSTER_TYPE").lower() if getenv("CD_CLUSTER_TYPE") else None
    CD_HELM_DOMAIN_NAME_DEV: Optional[str] = None
    CD_HELM_DOMAIN_NAME_PROD: Optional[str] = None
    CD_HELM_DOMAIN_NAME_MM_DEV: Optional[str] = None
    CD_HELM_DOMAIN_NAME_MM_PROD: Optional[str] = None
    # Additional initialization for domain names based on available configuration
    if CD_CLUSTER_TYPE:
        CD_HELM_DOMAIN_NAME_DEV = f"{CI_PROJECT_NAME}.{CI_SUBGROUP_NAME}.k8s-{CommandManager.determine_domain_name(CD_CLUSTER_TYPE, 'dev')}.{CD_HELM_DOMAIN}".lower()
        CD_HELM_DOMAIN_NAME_PROD = f"{CI_PROJECT_NAME}.{CI_SUBGROUP_NAME}.k8s-{CommandManager.determine_domain_name(CD_CLUSTER_TYPE, 'prod')}.{CD_HELM_DOMAIN}".lower()
        CD_HELM_DOMAIN_NAME_MM_DEV = f"{CI_PROJECT_NAME}.{CI_SUBGROUP_NAME}.k8s-{CommandManager.determine_domain_name(CD_CLUSTER_TYPE, 'dev')}.{CD_HELM_DOMAIN}".lower()
        CD_HELM_DOMAIN_NAME_MM_PROD = f"{CI_PROJECT_NAME}.{CI_SUBGROUP_NAME}.k8s-{CommandManager.determine_domain_name(CD_CLUSTER_TYPE, 'prod')}.{CD_HELM_DOMAIN}".lower()
    
    CI_ACCESS_MAINTAINER: Optional[str] = getenv("CI_ACCESS_MAINTAINER").lower() if getenv("CI_ACCESS_MAINTAINER") else None
    CI_ACCESS_DEVELOPER: Optional[str] = getenv("CI_ACCESS_DEVELOPER").lower() if getenv("CI_ACCESS_DEVELOPER") else None
    CI_ACCESS_REPORTER: Optional[str] = "".join([CI_ACCESS_MAINTAINER, " ", CI_ACCESS_DEVELOPER]) if CI_ACCESS_MAINTAINER and CI_ACCESS_DEVELOPER else None
    CI_MAIN_GROUP: str = "development"
    CI_MAIN_GROUP_DEVOPS: str = "devops"
    CD_GROUP_NAME: str = "".join([CI_MAIN_GROUP, '/chart'])
    CI_GROUP_NAME: str = "".join([CI_MAIN_GROUP, '/code'])
    CI_TEMPLATE_PROJECT_NAME: str = "devops/cicd-template"
    CI_SERVER_HOST: Optional[str] = getenv("CI_SERVER_HOST")
    envBranches: List[str] = [branch.strip() for branch in CD_CLUSTER_TYPE.split('|')] if CD_CLUSTER_TYPE else []
    CI_CODE_GROUP_ID: int = 453
    CI_CHART_GROUP_ID: int = 452
    CI_IMAGE_REPO_ID: int = 2021
    CI_TEMPLATE_REPO_ID: int = 827
    CI_DEVOPS_PROJECT_PROVISIONING_ID: int = 3502
    visibility: str = 'private'
    branches: List[str] = ["develop", 'master']

class ContainerExprPolicy:
    """
    Configuration class for container expiration policies.
    Specifies the policy attributes for container registry cleanup.
    """

    ENABLED: bool = True
    TIME_CLEANUP: str = "7d"
    TAGS_COUNT_KEEP: int = 5
    NAME_REGEX_KEEP: str = 'dev-*, prod-*'
    TIME_TAGS_DELETE: str = "30d"
    NAME_REGEX_DELETE: str = 'dev-*, prod-*'

class PathConf:
    """
    Configuration class for various file and directory paths used in the project.
    Defines paths for chart directories, CI templates, code repositories, and others.
    """
    current_directory: str = getcwd()
    code_path: str = 'code'
    chart_path: str ='chart'
    helm_chart_path: str = 'helm-charts'
    gitlab_ci_path: str = 'ci-template'
    devops_project_provisioning: str = 'devops-project-provisioning'
    gradle_single_module_java_11_path: str = 'gradle-single-module-java-11-template'
    gradle_single_module_java_21_path: str = 'gradle-single-module-java-21-template'
    gradle_multi_module_path: str = 'gradle-multi-module-template'
    gradle_settings: str                                    = f"{current_directory}/{code_path}/settings.gradle"
    gradle_application_yaml: str                            = f"{current_directory}/{code_path}/src/main/resources/application.yaml"
    gitlab_ci_source_path: str                              = f"{current_directory}/{gitlab_ci_path}/gitlab-ci-for-project.yml"
    gitlab_ci_destination_path: str                         = f"{current_directory}/{code_path}.gitlab-ci.yml"
    project_gradle_single_module_java_11_source_path: str   = f"{current_directory}/{gradle_single_module_java_11_path}/"
    project_gradle_single_module_java_21_source_path: str   = f"{current_directory}/{gradle_single_module_java_21_path}/"
    project_gradle_multi_module_source_path: str            = f"{current_directory}/{gradle_multi_module_path}/"
    project_destination_folder: str                         = f"{current_directory}/{code_path}/"
    helm_chart_source_path: str                             = f"{current_directory}/core/template_library/helm_charts/"
    helm_chart_destination_path: str                        = f"{current_directory}/{chart_path}/"
    helm_chart_yaml: str                                    = f"{current_directory}/{chart_path}/Chart.yaml"
    helm_values_dev_yaml: str                               = f"{current_directory}/{chart_path}/develop.yaml"
    helm_values_prod_yaml: str                              = f"{current_directory}/{chart_path}/master.yaml"
    k8s_namespace_resource_path: str                        = f"{devops_project_provisioning}/manifests/k8s_namespace_setup"
    argo_workflow_proj_path: str                            = f"{devops_project_provisioning}/manifests/argocd_proj_workflow"
    argo_workflow_app_path: str                             = f"{devops_project_provisioning}/manifests/argocd_app_workflow"

class VaultAuthConf:
    """
    Configuration class for Vault authentication details.
    Contains the Vault server URL and access token.
    """

    VAULT_URL: Optional[str] = getenv("CI_VAULT_URL")
    VAULT_TOKEN: Optional[str] = getenv("CI_VAULT_TOKEN")
    VAULT_SSL_VERIFY: bool = False

class ConsulAuthConf:
    """
    Configuration class for Consul environment variables.
    Includes the Consul server URL and access token.
    """

    CONSUL_URL: Optional[str] = getenv("CI_CONSUL_URL")
    CONSUL_TOKEN: Optional[str] = getenv("CI_CONSUL_TOKEN")
    CONSUL_SSL_VERIFY: bool = False


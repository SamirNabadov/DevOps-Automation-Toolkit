from git import Repo, GitCommandError
from core.settings.config_variables import PathConf, GitlabEnvConf
from core.utilities.command_executor import CommandManager
from core.operation.template_handler import TemplateGenerator
from typing import Tuple
from os import rename

class GitPushManager:
    """
    Class responsible for automating Git operations related to pushing changes
    to code, chart, and devops project provisioning repositories.
    """

    @staticmethod
    def configure_code() -> None:
        """
        Configures the code repository by copying files and making necessary replacements.
        This includes setting up project structure and generating GitLab CI configuration.
        """
        if GitlabEnvConf.CI_PROJECT_CREATION == "GENERATION" and GitlabEnvConf.CI_PROJECT_TYPE == "BACKEND" and GitlabEnvConf.CI_PROJECT_MODE == "MULTI" and GitlabEnvConf.CI_APPLICATION_TYPE == "GRADLE" and GitlabEnvConf.CI_PROJECT_MM_CODE_EXISTS == "FALSE":
            CommandManager.recursive_copy(PathConf.project_gradle_multi_module_source_path, PathConf.project_destination_folder)
            
        elif GitlabEnvConf.CI_PROJECT_CREATION == "GENERATION" and GitlabEnvConf.CI_PROJECT_TYPE == "BACKEND" and GitlabEnvConf.CI_PROJECT_MODE == "MONO" and GitlabEnvConf.CI_APPLICATION_TYPE == "GRADLE":
            if GitlabEnvConf.CI_APPLICATION_VERSION == "JAVA_11":
                CommandManager.recursive_copy(PathConf.project_gradle_single_module_java_11_source_path, PathConf.project_destination_folder)
            elif GitlabEnvConf.CI_APPLICATION_VERSION == "JAVA_21":
                CommandManager.recursive_copy(PathConf.project_gradle_single_module_java_21_source_path, PathConf.project_destination_folder)
            
            CommandManager.replacement(PathConf.gradle_application_yaml,'__CD_APPLICATION_NAME__', GitlabEnvConf.CI_PROJECT_NAME)
            CommandManager.replacement(PathConf.gradle_application_yaml,'__CD_HELM_CONTAINER_PORT__', GitlabEnvConf.CD_HELM_CONTAINER_PORT)
            CommandManager.replacement(PathConf.gradle_application_yaml,'__CD_HELM_MANAGEMENT_PORT__', GitlabEnvConf.CD_HELM_MANAGEMENT_PORT)
        
            CommandManager.replacement(PathConf.gradle_settings,'__CD_HELM_CHART_NAME__', GitlabEnvConf.CI_PROJECT_NAME)
        
        yaml_content = TemplateGenerator.generate_gitlab_ci_yaml()
        CommandManager.save_dict_as_yaml(yaml_content, f"{PathConf.project_destination_folder}/.gitlab-ci.yml")

    @staticmethod
    def push_to_code() -> None:
        """
        Pushes changes to the code repository. Handles branch creation, file configuration,
        commit and push operations for each environment branch.
        """
        try:
            repo = Repo(PathConf.code_path)
        except GitCommandError as e:
            print(f"(GitCommandError) Git command failed: {e}", file=sys.stderr)
            return

        # Fetch from the remote to make sure we have the latest info
        repo.remotes.origin.fetch()

        for branch in GitlabEnvConf.branches:
            try:
                # Checkout the branch
                repo.git.checkout(branch)

                # Perform configuration
                GitPushManager.configure_code()

                repo.git.add(A=True)
                repo.git.commit(m="Configured project")

                # Push changes
                repo.git.push('--set-upstream', 'origin', branch)

            except GitCommandError as e:
                print(f"Git command failed in {branch}: {e}")

    @staticmethod
    def setup_chart_config() -> Tuple[str, str, str, str, str]:
        """
        Sets up common chart configuration values used in push_to_chart.

        Returns:
            Tuple[str, str, str, str, str]: A tuple containing configuration values
            including module name, project name, helm domain names, and helm management settings.
        """
        if GitlabEnvConf.CI_PROJECT_MODE == "MULTI" and GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME != None:
            module = GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME
            project_name = GitlabEnvConf.CI_PROJECT_NAME + "/" + module
            helm_domain_name_dev = GitlabEnvConf.CD_HELM_DOMAIN_NAME_MM_DEV
            helm_domain_name_prod = GitlabEnvConf.CD_HELM_DOMAIN_NAME_MM_PROD
            cd_helm_management_enabled = "true" if GitlabEnvConf.CI_PROJECT_TYPE == "BACKEND" else "false"
        else:
            module = GitlabEnvConf.CI_PROJECT_NAME
            project_name = module
            helm_domain_name_dev = GitlabEnvConf.CD_HELM_DOMAIN_NAME_DEV
            helm_domain_name_prod = GitlabEnvConf.CD_HELM_DOMAIN_NAME_PROD
            cd_helm_management_enabled = "true" if GitlabEnvConf.CI_PROJECT_TYPE == "BACKEND" else "false"

        return module, project_name, helm_domain_name_dev, helm_domain_name_prod, cd_helm_management_enabled

    @staticmethod
    def configure_chart(module: str, helm_values_yaml: str, project_name: str, helm_domain_name: str, cd_helm_management_enabled: str, cd_replica_count: str, branch: str, profile: str) -> None:
        """
        Configures chart repository for a specific environment.

        Parameters:
        - module (str): Module name for the chart.
        - helm_values_yaml (str): Path to the Helm values YAML file.
        - project_name (str): Project name for the chart.
        - helm_domain_name (str): Helm domain name.
        - cd_helm_management_enabled (str): Indicates if Helm management is enabled.
        - cd_replica_count (str): Replica count of pod (dev or prod).
        - branch (str): Git branch name.
        - profile (str): Deployment profile (dev or prod).
        """
        CommandManager.recursive_copy(PathConf.helm_chart_source_path, PathConf.helm_chart_destination_path)
        rename(PathConf.helm_chart_destination_path + 'values.yaml', PathConf.helm_chart_destination_path + branch + ".yaml")
        CommandManager.replacement(PathConf.helm_chart_yaml,'__CD_HELM_CHART_NAME__', module)
        CommandManager.replacement(helm_values_yaml,'__CD_HELM_CHART_NAME__', module)
        CommandManager.replacement(helm_values_yaml, '__CD_PROJECT_NAME__', project_name)
        CommandManager.replacement(helm_values_yaml, '__CD_APPLICATION_NAME__', module)
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_NAMESPACE__', GitlabEnvConf.CD_HELM_NAMESPACE)
        CommandManager.replacement(helm_values_yaml, '__CD_GROUP_NAME__', GitlabEnvConf.CI_GROUP_NAME)
        CommandManager.replacement(helm_values_yaml, '__CD_SUBGROUP_NAME__', GitlabEnvConf.CI_SUBGROUP_NAME)
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_CONTAINER_PORT__', GitlabEnvConf.CD_HELM_CONTAINER_PORT)
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_MANAGEMENT_PORT__', GitlabEnvConf.CD_HELM_MANAGEMENT_PORT)
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_MANAGEMENT_ENABLED__', cd_helm_management_enabled)
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_SERVICE_PORT__', GitlabEnvConf.CD_HELM_SERVICE_PORT)
        CommandManager.replacement(helm_values_yaml, '__CD_REPLICA_COUNT__', cd_replica_count)   
        CommandManager.replacement(helm_values_yaml, '__CD_HELM_DOMAIN_NAME__', helm_domain_name)
        CommandManager.replacement(helm_values_yaml, '__CI_SERVER_HOST__', GitlabEnvConf.CI_SERVER_HOST)
        CommandManager.replacement(helm_values_yaml, '__CD_PROFILE_NAME__', profile)

    @staticmethod
    def push_to_chart() -> None:
        """
        Pushes chart configuration changes to the GitLab repository.
        Configures charts differently based on the branch (develop or master).
        """
        try:
            repo = Repo(PathConf.chart_path)
        except GitCommandError as e:
            print(f"(GitCommandError) Git command failed: {e}", file=sys.stderr)

        module, project_name, helm_domain_name_dev, helm_domain_name_prod, cd_helm_management_enabled = GitPushManager.setup_chart_config()

        # Fetch from the remote to make sure we have the latest info
        repo.remotes.origin.fetch()

        for branch in GitlabEnvConf.branches:
            try:
                # Checkout the branch
                repo.git.checkout(branch)

                if branch == "develop":
                    GitPushManager.configure_chart(module, PathConf.helm_values_dev_yaml, project_name, helm_domain_name_dev, cd_helm_management_enabled, GitlabEnvConf.CD_REPLICA_COUNT_DEV, branch, "dev")
                elif branch == "master":
                    GitPushManager.configure_chart(module, PathConf.helm_values_prod_yaml, project_name, helm_domain_name_prod, cd_helm_management_enabled, GitlabEnvConf.CD_REPLICA_COUNT_PROD, branch, "prod")

                repo.git.add(A=True)
                repo.git.commit(m="Configured project")

                # Push changes
                repo.git.push('--set-upstream', 'origin', branch)
            except GitCommandError as e:
                print(f"Git command failed: {e}")

    @staticmethod
    def check_git_status(repo: Repo) -> None:
        """
        Check the status of the Git repository similar to `git status`.

        Parameters:
        - repo (Repo): The Git repository object.
        """
        changed_files = [item.a_path for item in repo.index.diff(None)]
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        untracked_files = repo.untracked_files

        if changed_files or staged_files or untracked_files:
            print("Uncommitted changes:")
            if staged_files:
                print("Staged files:", staged_files)
            if changed_files:
                print("Modified but not staged files:", changed_files)
            if untracked_files:
                print("Untracked files:", untracked_files)
        else:
            print("No changes to commit.")

    @staticmethod
    def push_to_devops_project_provisioning() -> None:
        """
        Pushes configuration changes to the DevOps project provisioning repository.
        Handles multiple environments and their respective branches.
        """
        MODULE = GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME if GitlabEnvConf.CI_PROJECT_MODE == "MULTI" and GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME != None else GitlabEnvConf.CI_PROJECT_NAME

        try:
            repo = Repo(PathConf.devops_project_provisioning)
        except GitCommandError as e:
            print(f"(GitCommandError) Git command failed: {e}", file=sys.stderr)

        # Fetch from the remote to make sure we have the latest info
        repo.remotes.origin.fetch()

        for branch in GitlabEnvConf.envBranches:
            try:
                # Checkout the branch
                repo.git.checkout(branch)

                CommandManager.create_directory(PathConf.argo_workflow_proj_path)
                CommandManager.create_directory(PathConf.argo_workflow_app_path)
                CommandManager.create_directory(f"{PathConf.argo_workflow_app_path}/{CommandManager.convert_key_format(GitlabEnvConf.CI_SUBGROUP_NAME)}")
                CommandManager.create_directory(PathConf.k8s_namespace_resource_path)
                
                # Create and clear directories and Generate YAML files
                yaml_content = TemplateGenerator.generate_argocd_app_project_yaml(GitlabEnvConf.CI_SUBGROUP_NAME, GitlabEnvConf.CD_HELM_NAMESPACE)
                CommandManager.save_dict_as_yaml(yaml_content, f"{PathConf.argo_workflow_proj_path}/{CommandManager.convert_key_format(GitlabEnvConf.CI_SUBGROUP_NAME)}.yml")

                env = "dev" if branch in ["dev", "devdmz"] else "prod"
                git_branch = "develop" if branch in ["dev", "devdmz"] else "master"
                yaml_content = TemplateGenerator.generate_argocd_application_yaml(GitlabEnvConf.CI_SERVER_HOST, GitlabEnvConf.CI_SUBGROUP_NAME, env, MODULE, git_branch, GitlabEnvConf.CD_GROUP_NAME, GitlabEnvConf.CI_PROJECT_NAME, GitlabEnvConf.CD_HELM_NAMESPACE)
                CommandManager.save_dict_as_yaml(yaml_content, f"{PathConf.argo_workflow_app_path}/{CommandManager.convert_key_format(GitlabEnvConf.CI_SUBGROUP_NAME)}/{CommandManager.convert_key_format(GitlabEnvConf.CI_PROJECT_NAME)}.yml")

                yaml_content = TemplateGenerator.generate_k8s_namespace_yaml(GitlabEnvConf.CD_HELM_NAMESPACE)
                CommandManager.save_dict_as_yaml(yaml_content, f"{PathConf.k8s_namespace_resource_path}/{CommandManager.convert_key_format(GitlabEnvConf.CD_HELM_NAMESPACE)}__.yml")

                repo.git.add(A=True)
                repo.git.commit(m="Configured project")

                # Push changes
                repo.git.push('--set-upstream', 'origin', branch)
            except GitCommandError as e:
                print(f"Git command failed: {e}")


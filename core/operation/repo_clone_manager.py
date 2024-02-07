
from git import Repo
from core.utilities.command_executor import CommandManager
from core.settings.config_variables import PathConf, GitlabEnvConf, GitlabAuthConf
from typing import ClassVar

class GitCloneManager:
    """
    GitCloneManager is a utility class for cloning various Git repositories. 
    It provides methods to clone different types of repositories such as Helm charts, 
    GitLab CI templates, Gradle modules, and project-specific source code and Helm charts.
    Each method constructs the appropriate repository URL and clones the repository into a local path.
    """

    @staticmethod
    def _clone_repository(repo_url: str, local_path: str) -> None:
        """
        Clones a repository from a given URL to a local path and removes the .git directory.

        Args:
            repo_url (str): The URL of the repository to be cloned.
            local_path (str): The local path where the repository will be cloned to.
        """
        CommandManager.create_folder(local_path)
        CommandManager.delete_folder(local_path)
        Repo.clone_from(repo_url, local_path)
        CommandManager.delete_folder(f"{local_path}/.git")

    @staticmethod
    def _clone_repository_without_git(repo_url: str, local_path: str) -> None:
        """
        Clones a repository from a given URL to a local path, keeping the .git directory.

        Args:
            repo_url (str): The URL of the repository to be cloned.
            local_path (str): The local path where the repository will be cloned to.
        """
        CommandManager.create_folder(local_path)
        CommandManager.delete_folder(local_path)
        Repo.clone_from(repo_url, local_path)

    @staticmethod
    def _construct_repo_url(project_path: str) -> str:
        """
        Constructs the full repository URL for a given project path.

        Args:
            project_path (str): The specific path of the project in the repository.

        Returns:
            str: The full URL of the repository.
        """
        return f"https://{GitlabAuthConf.CI_GITLAB_TOKEN_NAME}:{GitlabAuthConf.CI_GITLAB_TOKEN}@{GitlabEnvConf.CI_SERVER_HOST}/{GitlabEnvConf.CI_TEMPLATE_PROJECT_NAME}/{project_path}.git"

    @staticmethod
    def template_gradle_single_module_java_11() -> None:
        """
        Clones the single module Gradle template repository.
        """
        url: str = GitCloneManager._construct_repo_url(PathConf.gradle_single_module_java_11_path)
        GitCloneManager._clone_repository(url, PathConf.gradle_single_module_java_11_path)

    @staticmethod 
    def template_gradle_single_module_java_21() -> None:
        """
        Clones the single module Gradle template repository.
        """
        url: str = GitCloneManager._construct_repo_url(PathConf.gradle_single_module_java_21_path)
        GitCloneManager._clone_repository(url, PathConf.gradle_single_module_java_21_path)

    @staticmethod
    def template_gradle_multi_module() -> None:
        """
        Clones the multi-module Gradle template repository.
        """
        url: str = GitCloneManager._construct_repo_url(PathConf.gradle_multi_module_path)
        GitCloneManager._clone_repository(url, PathConf.gradle_multi_module_path)

    @staticmethod
    def repo_source_code() -> None:
        """
        Clones the source code repository for the project.
        """
        url: str = f"https://{GitlabAuthConf.CI_GITLAB_TOKEN_NAME}:{GitlabAuthConf.CI_GITLAB_TOKEN}@{GitlabEnvConf.CI_SERVER_HOST}/{GitlabEnvConf.CI_MAIN_GROUP}/{PathConf.code_path}/{GitlabEnvConf.CI_SUBGROUP_NAME}/{GitlabEnvConf.CI_PROJECT_NAME}.git"
        GitCloneManager._clone_repository_without_git(url, PathConf.code_path)

    @staticmethod
    def repo_helm_chart(project_name: str) -> None:
        """    
        Args:
        project_name (str): The name of the project for which the Helm chart repository is to be cloned.
        """
        url: str = f"https://{GitlabAuthConf.CI_GITLAB_TOKEN_NAME}:{GitlabAuthConf.CI_GITLAB_TOKEN}@{GitlabEnvConf.CI_SERVER_HOST}/{GitlabEnvConf.CI_MAIN_GROUP}/{PathConf.chart_path}/{GitlabEnvConf.CI_SUBGROUP_NAME}/{project_name}.git"
        GitCloneManager._clone_repository_without_git(url, PathConf.chart_path)
    
    @staticmethod
    def repo_project_provisioning() -> None:
        """
        Clones the DevOps project provisioning repository.
        """
        url = f"https://{GitlabAuthConf.CI_GITLAB_TOKEN_NAME}:{GitlabAuthConf.CI_GITLAB_TOKEN}@{GitlabEnvConf.CI_SERVER_HOST}/{GitlabEnvConf.CI_MAIN_GROUP_DEVOPS}/{PathConf.devops_project_provisioning}.git"
        GitCloneManager._clone_repository_without_git(url, PathConf.devops_project_provisioning)


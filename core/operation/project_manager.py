from gitlab import Gitlab, exceptions, REPORTER_ACCESS, DEVELOPER_ACCESS, MAINTAINER_ACCESS
from sys import exit
from core.authentication.auth_manager import GitlabAuth
from core.settings.config_variables import GitlabAuthConf, GitlabEnvConf, PathConf, ContainerExprPolicy, ConsulAuthConf
from core.utilities.command_executor import CommandManager
from core.integration.vault_integration import VaultManager
from core.integration.consul_integration import ConsulManager
from core.operation.template_handler import TemplateGenerator
from typing import Optional, List

class GitlabProjectManager:
    """
    Manages GitLab project configurations including subgroup creation, project initialization, 
    branch protection, user role assignments, and global CI/CD variable settings.
    """

    def __init__(self) -> None:
        """
        Initializes the GitlabProjectManager by establishing a connection to GitLab.
        """
        self.gl: Gitlab = GitlabAuth.connect(
            GitlabAuthConf.CI_GITLAB_SSL_VERIFY,
            GitlabAuthConf.CI_GITLAB_SERVER,
            GitlabAuthConf.CI_GITLAB_TOKEN,
            GitlabAuthConf.CI_GITLAB_API_VERSION
        )

    def _create_subgroup(self, group_id: int) -> Optional[int]:
        """
        Creates a GitLab subgroup within a specified group and returns its ID.

        Args:
            group_id (int): The ID of the parent group in which the subgroup will be created.

        Returns:
            Optional[int]: The ID of the created subgroup, or None if creation fails.
        """
        self.group_id = group_id

        try:
            creation_subgroup = self.gl.groups.create({
                "name": GitlabEnvConf.CI_SUBGROUP_NAME, 
                "path": GitlabEnvConf.CI_SUBGROUP_NAME, 
                'visibility': GitlabEnvConf.visibility, 
                "parent_id": self.group_id
            })
            return creation_subgroup.id
        except exceptions.GitlabCreateError as e:
            if 'has already been taken' in str(e):
                # Subgroup already exists, search for it within the parent group and return its ID
                parent_group = self.gl.groups.get(self.group_id)
                subgroups = parent_group.subgroups.list(all=True)
                for subgroup in subgroups:
                    if subgroup.path == GitlabEnvConf.CI_SUBGROUP_NAME:
                        print(f"Subgroup '{GitlabEnvConf.CI_SUBGROUP_NAME}' already exists.")
                        return subgroup.id
            else:
                print(f"Failed to create subgroup '{GitlabEnvConf.CI_SUBGROUP_NAME}': {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def create_project_code(self) -> None:
        """
        Creates a new project in the code subgroup and configures its settings, branches, and user roles.
        """
        code_subgroup_child_id  = self._create_subgroup(GitlabEnvConf.CI_CODE_GROUP_ID)
        try:
            # Attempt to create the project
            code_subgroup_project = self.gl.projects.create({
                                'name': GitlabEnvConf.CI_PROJECT_NAME, 
                                'visibility': GitlabEnvConf.visibility, 
                                'namespace_id': code_subgroup_child_id,
                                'initialize_with_readme': False,  # Don't initialize with a README
                                'container_expiration_policy_attributes':
                                            {"enabled": ContainerExprPolicy.ENABLED,
                                            "cadence": ContainerExprPolicy.TIME_CLEANUP,
                                            "keep_n": ContainerExprPolicy.TAGS_COUNT_KEEP,
                                            "name_regex_keep": ContainerExprPolicy.NAME_REGEX_KEEP,
                                            "older_than": ContainerExprPolicy.TIME_TAGS_DELETE,
                                            "name_regex": ContainerExprPolicy.NAME_REGEX_DELETE}
                                })
            print(f"Project '{GitlabEnvConf.CI_PROJECT_NAME}' created successfully.")

            # Create or update protected branches
            for branch_name in GitlabEnvConf.branches:

                # Create or recreate protected branch with the correct access levels
                code_subgroup_project.protectedbranches.create({
                    'name': branch_name,
                    'merge_access_level': DEVELOPER_ACCESS,
                    'push_access_level': MAINTAINER_ACCESS
                })

                ref = 'main' if branch_name == "develop" else 'develop'
                
                # Create the branch if it doesn't exist
                try:
                    code_subgroup_project.branches.create({'branch': branch_name, 'ref': ref})
                    print(f"Branch '{branch_name}' created from '{ref} in CODE group'.")
                except exceptions.GitlabCreateError as e:
                    print(f"Creation of branch on CODE group '{branch_name}': {e}")
        
        except exceptions.GitlabCreateError as e:
            if "has already been taken" in str(e):
                exit(f"Project '{GitlabEnvConf.CI_PROJECT_NAME}' already exists in CODE group. Skipping creation.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        # Assign users as maintainers and developers
        developers  = CommandManager.convert_string_to_list(GitlabEnvConf.CI_ACCESS_DEVELOPER)
        maintainers = CommandManager.convert_string_to_list(GitlabEnvConf.CI_ACCESS_MAINTAINER)

        for role, users in [('maintainer', maintainers), ('developer', developers)]:
            for username in users:
                try:
                    user = self.gl.users.list(username=username)[0]
                    code_subgroup_project.members.create({'user_id': user.id, 'access_level': REPORTER_ACCESS})
                    print(f"Added {role}: {username}")
                except IndexError:
                    print(f"{username} for {role} access is not available")

    def create_project_chart(self) -> None:
        """
        Creates a new project in the chart subgroup and configures its settings, branches, and user roles.
        """
        chart_subgroup_child_id = self._create_subgroup(GitlabEnvConf.CI_CHART_GROUP_ID)
        module = None
        
        if GitlabEnvConf.CI_PROJECT_MODE == "MULTI" and GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME != None:
            module = GitlabEnvConf.CI_PROJECT_MM_MODULE_NAME
        else:
            module = GitlabEnvConf.CI_PROJECT_NAME
        
        try:
            # Attempt to create the project
            chart_subgroup_project = self.gl.projects.create({
                                    'name': module, 
                                    'visibility': GitlabEnvConf.visibility, 
                                    'namespace_id': chart_subgroup_child_id,
                                    'initialize_with_readme': False,  # Don't initialize with a README
                                    })
            print(f"Project '{module}' created successfully.")

            # Create or update protected branches
            for branch_name in GitlabEnvConf.branches:

                # Create or recreate protected branch with the correct access levels
                chart_subgroup_project.protectedbranches.create({
                    'name': branch_name,
                    'merge_access_level': DEVELOPER_ACCESS,
                    'push_access_level': MAINTAINER_ACCESS
                })

                ref = 'main' if branch_name == "develop" else 'develop'
                
                # Create the branch if it doesn't exist
                try:
                    chart_subgroup_project.branches.create({'branch': branch_name, 'ref': ref})
                    print(f"Branch '{branch_name}' created from '{ref} in CHART group'.")
                except exceptions.GitlabCreateError as e:
                    print(f"Creation of branch on CHART group: '{branch_name}': {e}")
        
        except exceptions.GitlabCreateError as e:
            if "has already been taken" in str(e):
                exit(f"Project '{module}' already exists in CHART group. Skipping creation.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        # Assign users as maintainers and developers
        developers  = CommandManager.convert_string_to_list(GitlabEnvConf.CI_ACCESS_DEVELOPER)
        maintainers = CommandManager.convert_string_to_list(GitlabEnvConf.CI_ACCESS_MAINTAINER)
        
        for role, users in [('maintainer', maintainers), ('developer', developers)]:
            for username in users:
                try:
                    user = self.gl.users.list(username=username)[0]
                    chart_subgroup_project.members.create({'user_id': user.id, 'access_level': REPORTER_ACCESS})
                    print(f"Added {role}: {username}")
                except IndexError:
                    print(f"{username} for {role} access is not available")

        """
        Granting reporter access to the Images and CI-template subgroups under the DevOps group
        ------------------------------------------------------------------------------------------
        """

    def assign_reporter_access_to_projects(self) -> None:
        """
        Assigns reporter access to specified users for the CI Image Repository and CI Template Repository projects.
        """
        reporters = CommandManager.convert_string_to_list(GitlabEnvConf.CI_ACCESS_REPORTER)
        
        for reporter in reporters:
            try:
                user = self.gl.users.list(username=reporter)[0]

                # Assign reporter access to the CI Image Repository project
                image_repo_project = self.gl.projects.get(GitlabEnvConf.CI_IMAGE_REPO_ID, lazy=True)
                try:
                    image_repo_project.members.create({'user_id': user.id, 'access_level': REPORTER_ACCESS})
                    print(f"Reporter access granted to '{reporter}' in CI Image Repository project.")
                except exceptions.GitlabCreateError:
                    print(f"User '{reporter}' already has access in CI Image Repository project.")

                # Assign reporter access to the CI Template Repository project
                template_repo_project = self.gl.projects.get(GitlabEnvConf.CI_TEMPLATE_REPO_ID, lazy=True)
                try:
                    template_repo_project.members.create({'user_id': user.id, 'access_level': REPORTER_ACCESS})
                    print(f"Reporter access granted to '{reporter}' in CI Template Repository project.")
                except exceptions.GitlabCreateError:
                    print(f"User '{reporter}' already has access in CI Template Repository project.")

            except IndexError:
                print(f"{reporter} for reporter access is not available")

    def create_global_variable(self) -> None:
        """
        Creates global CI/CD variables in the DevOps project provisioning in GitLab.
        """
        project_name_devops_provisioning = f"{GitlabEnvConf.CI_MAIN_GROUP_DEVOPS}/{PathConf.devops_project_provisioning}"
        devops_project_provisioning = self.gl.projects.get(project_name_devops_provisioning)

        # Retrieve existing variables
        existing_variables = {var.key: var for var in devops_project_provisioning.variables.list(all=True)}

        for branch in GitlabEnvConf.envBranches:
            vault_secret_value  = None  
            consul_secret_value = None
            regcred_secret_value = None

            vault_manager = VaultManager()
            consul_manager = ConsulManager(ConsulAuthConf.CONSUL_URL, ConsulAuthConf.CONSUL_TOKEN, ConsulAuthConf.CONSUL_SSL_VERIFY)

            if converted_secret_key not in existing_variables:
                consul_secret_value = consul_manager.generate_consul_secret(GitlabEnvConf.CI_SUBGROUP_NAME, GitlabEnvConf.CD_HELM_NAMESPACE)
                if branch in ["dev", "devdmz"]:
                    vault_secret_value = vault_manager.generate_vault_secret(GitlabEnvConf.CI_SUBGROUP_NAME, "dev", GitlabEnvConf.CD_HELM_NAMESPACE)
                if branch in ["prod", "proddmz", "procdnz"]:
                    vault_secret_value = vault_manager.generate_vault_secret(GitlabEnvConf.CI_SUBGROUP_NAME, "prod", GitlabEnvConf.CD_HELM_NAMESPACE)
                regcred_secret_value = TemplateGenerator.generate_k8s_regcred(GitlabAuthConf.CI_GITLAB_SERVER, GitlabAuthConf.CI_GITLAB_USERNAME, GitlabAuthConf.CI_GITLAB_PASSWORD, GitlabEnvConf.CD_HELM_NAMESPACE)
                
                # Write the combined secret value to Vault (using version KV V1)
                vault_manager.write_secret_to_vault(mount_point='devops_kv', secret_path=f'{branch}/kubernetes/namespace', secret_key=CommandManager.convert_key_format(GitlabEnvConf.CD_HELM_NAMESPACE), secret_value=secret_value)        

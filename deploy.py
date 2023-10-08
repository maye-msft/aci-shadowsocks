import os, sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from log import *

import build_container as build_container
import os, json


from azure.identity import AzureCliCredential, AzureAuthorityHosts, ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.containerregistry import ContainerRegistryClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup, Container, ContainerPort, Port, IpAddress, ImageRegistryCredential,
                                                 ResourceRequirements, ResourceRequests, ContainerGroupNetworkProtocol, OperatingSystemTypes)

from azure.container_group import create_container_instance, ACI_RESTART_POLICY_NEVER, ACI_RESTART_POLICY_ALWAYS, ACI_RESTART_POLICY_ON_FAILURE
from azure.resource_group import setup_resource_group
from azure.container_registry import setup_container_registry, get_registry_info, get_registry_credentials, delete_container_registry




resource_client = None

def main():
    # load config.json
    with open('config.json') as f:
        config = json.load(f)
    
    with open('ss_config.json') as f:
        ss_config = json.load(f)

    port = ss_config['server_port']

    log_info(f"load config.json: {config}")
    # load settings
    for k, v in config.items():
        log_info(f"set environment variable {k}={v}")
        os.environ[k] = v



    res_grp_name=config['RESOURCE_GROUP_NAME']
    registry_name=config['CONTAINER_REGISTRY_NAME']
    location=config['LOCATION']

    app_name=config['APP_NAME']
    app_version=config['APP_VERSION']


    setup_resource_group(res_grp_name, location)
    log_info(f"setup resource group {res_grp_name} in {location}")
    setup_container_registry(res_grp_name, registry_name, location)
    log_info(f"setup container registry {registry_name} in {location}")

    registry = get_registry_info(res_grp_name, registry_name)
    registry_server = registry.login_server
    registry_username, registry_password = get_registry_credentials(res_grp_name, registry_name)


    current_path = os.path.dirname(__file__)

    build_container.build_local_docker_image(app_name, current_path, current_path)
    log_info(f"build docker image {app_name} from {current_path}")
    build_container.publish_to_acr(app_name, app_version, registry_server, registry_username, registry_password)
    log_info(f"publish docker image {app_name}:{app_version} to {registry_server}")

    SHADOWSOCKS_PASSWORD = os.environ['SHADOWSOCKS_PASSWORD']
    SHADOWSOCKS_PORT = os.environ['SHADOWSOCKS_PORT']

    create_container_instance(res_grp_name, registry_server, registry_username, registry_password, 
                    app_name, app_version, 
                    app_name,
                    location, 
                    environment_variables={"SHADOWSOCKS_PORT": SHADOWSOCKS_PORT}, 
                    secure_environment_variables={"SHADOWSOCKS_PASSWORD": SHADOWSOCKS_PASSWORD},
                    restart_policy=ACI_RESTART_POLICY_NEVER,
                    port=port)
    log_info(f"create container instance {app_name} in {res_grp_name}")

    
    delete_container_registry(res_grp_name, registry_name)
    log_info(f"delete container registry {registry_name} in {res_grp_name}")


if __name__ == '__main__':
    main()
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from log import *


import os
from dotenv import load_dotenv
load_dotenv() 


from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient

from azure.identity import AzureCliCredential, AzureAuthorityHosts, ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

def setup_container_registry(resgrp_name:str, registry_name:str, location:str):

    log_info(f"setup container registry {registry_name} in {location}")
    registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    registries = registry_client.registries.begin_create(
        resgrp_name,
        registry_name,
        {
          "location": location,
          "sku": {
            "name": "Basic"
          },
          "admin_user_enabled": True
        }
    ).result()
    log_info(f"Provisioned container registry {registries.name}")



def get_registry_info(resgrp_name:str, registry_name:str):
    registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    registry = registry_client.registries.get(resgrp_name, registry_name)
    log_info(f"Container registry info: {registry.login_server} {registry.admin_user_enabled}")
    return registry

def get_registry_credentials(resgrp_name:str, registry_name:str):
    registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    credentials = registry_client.registries.list_credentials(resgrp_name, registry_name)
    log_info(f"Container registry credentials: {credentials.username} {credentials.passwords[0].value}")
    return credentials.username, credentials.passwords[0].value


def get_authority(endpoint):
    if ".azurecr.io" in endpoint:
        return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    if ".azurecr.cn" in endpoint:
        return AzureAuthorityHosts.AZURE_CHINA
    if ".azurecr.us" in endpoint:
        return AzureAuthorityHosts.AZURE_GOVERNMENT
    raise ValueError(f"Endpoint ({endpoint}) could not be understood")

def get_credential(authority, **kwargs):
    is_async = kwargs.pop("is_async", False)
    if is_async:
        return AsyncClientSecretCredential(
            tenant_id=os.environ.get("AZURE_TENANT_ID"),
            client_id=os.environ.get("AZURE_CLIENT_ID"),
            client_secret=os.environ.get("AZURE_CLIENT_SECRET"),
            authority=authority
        )
    return ClientSecretCredential(
        tenant_id=os.environ.get("AZURE_TENANT_ID"),
        client_id=os.environ.get("AZURE_CLIENT_ID"),
        client_secret=os.environ.get("AZURE_CLIENT_SECRET"),
        authority=authority
    )

def delete_container_registry(resgrp_name:str, registry_name:str):
    registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    registry_client.registries.delete(resgrp_name, registry_name)
    log_info(f"Deleted container registry {registry_name}")
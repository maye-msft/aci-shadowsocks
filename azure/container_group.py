import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from log import *


import os
from dotenv import load_dotenv
load_dotenv() 

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

ACI_RESTART_POLICY_NEVER = 'Never'
ACI_RESTART_POLICY_ALWAYS = 'Always'
ACI_RESTART_POLICY_ON_FAILURE = 'OnFailure'

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

def create_container_instance(resgrp_name:str, 
                              registry_server:str, 
                              registry_username:str, 
                              registry_password:str, 
                              image_name:str, tag:str, 
                              container_name:str,
                              location:str, 
                              environment_variables:dict=None, 
                              secure_environment_variables:dict=None, 
                              volume_names:str=None,
                              volume_storage_account_name:str=None,
                              volume_storage_account_key:str=None,
                              volume_share_names:str=None,
                              restart_policy:str=ACI_RESTART_POLICY_NEVER,
                              command:list=None, 
                              cpu:float=1.0, memory:float=1.5,
                              port:int=5000):
    log_info(f"Creating container instance {image_name} with tag {tag} in resource group {resgrp_name} in location {location}")
    environment_variables_array = []
    if environment_variables is not None:
        for key, value in environment_variables.items():
            environment_variables_array.append({
                "name": key,
                "value": value
            })
            log_info(f"Added environment variable {key}={value} to container {image_name}")

    if secure_environment_variables is not None:
        for key, value in secure_environment_variables.items():
            environment_variables_array.append({
                "name": key,
                "secureValue": value
            })
            log_info(f"Added secure environment variable {key} to container {image_name}")

    volumes = []
    volume_mounts = []
    if volume_names is not  None:
        for i in range(len(volume_names)):
            if volume_names[i] is not None:
                volume_name = volume_names[i]
                volume_share_name = volume_share_names[i]
                volumes.append({
                    "azureFile": {
                        "shareName": volume_share_name,
                        "storageAccountKey": volume_storage_account_key,
                        "storageAccountName": volume_storage_account_name,
                    },
                    "name": volume_names[i],
                })
                log_info(f"Created volume {volume_name} for container {image_name}")
                volume_mounts.append(
                    {"mountPath": "/mnt/"+volume_name, "name": volume_name, "readOnly": False},
                )

    containerinstance_client = ContainerInstanceManagementClient(credential, subscription_id)


    response = containerinstance_client.container_groups.begin_create_or_update(
        resgrp_name,
        f"{container_name}_group",
        container_group={"location": location,
            "properties": {
                "containers": [
                    {
                        "name": container_name,
                        "properties": {
                            "command": command if command is not None else [],
                            "environmentVariables": environment_variables_array,
                            "image": registry_server+"/"+image_name+":"+tag,
                            "ports": [{"port": port}],
                            "resources": {"requests": {"cpu": cpu, "memoryInGB": memory}},
                            "volumeMounts": volume_mounts
                        },
                    }
                ],
                "imageRegistryCredentials": [{
                    "server": registry_server,
                    "username": registry_username,
                    "password": registry_password,
                }],
                "volumes": volumes,
                "restartPolicy": restart_policy,
                "ipAddress": {"ports": [{"port": 5000, "protocol": "TCP"}], "type": "Public"},
                "osType": "Linux",

            },
        },
    ).result()
    log_info(f"Created container instance {response.name}")


def delete_container_instance(resgrp_name:str, container_name:str):
    log_info(f"Deleting container instance {container_name} in resource group {resgrp_name}")
    containerinstance_client = ContainerInstanceManagementClient(credential, subscription_id)
    containerinstance_client.container_groups.begin_delete(resgrp_name, f"{container_name}_group").result()
    log_info(f"Deleted container instance {container_name}")

def pause_container_instance(resgrp_name:str, container_name:str):
    log_info(f"Pausing container instance {container_name} in resource group {resgrp_name}")
    containerinstance_client = ContainerInstanceManagementClient(credential, subscription_id)
    containerinstance_client.container_groups.stop(resgrp_name, f"{container_name}_group")
    log_info(f"Paused container instance {container_name}")
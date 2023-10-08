import os, sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from log import *
from dotenv import load_dotenv
load_dotenv() 

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

def setup_resource_group(resgrp_name:str, location:str):
    # Provision the resource group.
    rg_result = resource_client.resource_groups.create_or_update(
        resgrp_name, {"location": location}
    )

    log_info(
        f"Provisioned resource group {rg_result.name} in \
            the {rg_result.location} region"
    )
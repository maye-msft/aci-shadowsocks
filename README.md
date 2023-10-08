# Shadowsocks with Azure Container Instance and Azure Container Registry

This repo is to create a shadowsocks server with Azure Container Instance and Azure Container Registry.

## Prerequisites

1. Azure account - service principal
    - Subscription ID
    - Tenant ID
    - Client ID
    - Client Secret

    Modify the values above in the config_sample.json and rename it as config.json

2. Python 3.7 or above

    Setup Python from [Python](https://www.python.org/downloads/)

    create virtual environment

    Linux

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    Windows

    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. Docker

    Setup Docker from [Docker](https://docs.docker.com/get-docker/)

## Shadowsocks Server Setup

1. Setup python libraries

    ```bash
    pip install -r requirements.txt
    ```

1. Modify ss_config.json for your shadowsocks server configuration

1. Deploy Shadowsocks Server

    ```bash
    python deploy.py
    ```

## Shadowsocks Client Setup

Refer to this Shadowsocks Client Setup [Doc](https://centixkadon.github.io/b/app/shadowsocks/client/)
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import log
import datetime
def build_local_docker_image(image_name:str, dockerfile_path:str, app_path:str=None):
    if app_path is None:
        app_path = dockerfile_path
    cmd = f'docker build --platform=linux/amd64 -t {image_name} -f {dockerfile_path}/Dockerfile {app_path}'
    log.log_info(cmd)
    code = os.system(cmd)
    if code != 0:
        raise Exception(f'Failed to build docker image {image_name} from {dockerfile_path}')
    
def publish_to_acr(image_name:str, version:str, acr_name:str, acr_username:str, acr_password:str):
    # version = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    cmd = [ f'docker login {acr_name} -u {acr_username} -p {acr_password}',
           f'docker tag {image_name} {acr_name}/{image_name}:{version}',
           f'docker push {acr_name}/{image_name}:{version}'
    ]
    for c in cmd:
        log.log_info(c)
        code = os.system(c)
        if code != 0:
            raise Exception(f'Failed to publish docker image {image_name}:{version} to {acr_name}')
        
    return f'{acr_name}/{image_name}:{version}'


def run_local_docker_container(tag_name:str, container_port:int=5000, host_port:int=8000):
    cmd = f'docker run -p {host_port}:{container_port} {tag_name}'
    log.log_info(cmd)
    code = os.system(cmd)
    if code != 0:
        raise Exception(f'Failed to run docker container {tag_name} on port {host_port}')



def main():
    current_path = os.path.dirname(os.path.realpath(__file__))
    parent_path = os.path.dirname(current_path)
    build_local_docker_image(tag_name=api.APP_NAME, dockerfile_path=parent_path)
    # run_local_docker_container(tag_name=api.APP_NAME, container_port=5000, host_port=5000)
    publish_to_acr(tag_name=api.APP_NAME, acr_name='pylibtest01.azurecr.io', acr_username='pylibtest01', acr_password='xitteXNo7ztYcDMjOdMAyZa6enGtw5UzknUy6z2rXS+ACRBb/lHd')

if __name__ == '__main__':
    main()

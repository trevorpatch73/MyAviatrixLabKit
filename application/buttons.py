from . import db
from .data_models import EnvInputTable, EnvStateTable
import re
import requests
from time import sleep
from os import *
from pathlib import Path


def Launch_Environment():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    aws_key_id = user.db_aws_key_id
    aws_key_value = user.db_aws_key_value
    terraform_api_key = user.db_terraform_api_key
    terraform_org_name = user.db_terraform_org_name
    terraform_header = {
        'Authorization': 'Bearer ' + terraform_api_key,
        'Content-Type': 'application/vnd.api+json'
    }
    terraform_url = 'app.terraform.io/api/v2'

    # Step One: Create a workspace in TF Cloud
    jsonData = {
        "data": {
            "attributes": {
                "name": "MY_AVIATRIX_LAB_KIT_CONTROLLER_WORKSPACE",
                "description": "created via API",
                "auto-apply": True
            },
            "type": "workspaces"
        }
    }

    url = ('https://' + terraform_url + '/organizations/' +
           terraform_org_name + '/workspaces')

    response = requests.post(url, json=jsonData, headers=terraform_header)

    data_json = response.json()
    controller_workspace_id = data_json['data']['id']
    environment.db_controller_workspace_id = controller_workspace_id
    db.session.commit()

    url = ''
    jsonData = ''
    response = ''

    # Step Two: Inject Variables into created TF Cloud workspace
    url = ('https://' + terraform_url + '/vars')

    jsonData = {
        "data": {
            "type": "vars",
            "attributes": {
                "key": "aws_key_id",
                "value": aws_key_id,
                "description": "SENSITIVE AWS INFORMATION",
                "category": "terraform",
                # "sensitive": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": controller_workspace_id,
                        "type": "workspaces"
                    }
                }
            }
        }
    }
    sleep(1)

    response = requests.post(url, json=jsonData, headers=terraform_header)

    jsonData = ''
    response = ''

    jsonData = {
        "data": {
            "type": "vars",
            "attributes": {
                "key": "aws_key_value",
                "value": aws_key_value,
                "description": "SENSITIVE AWS INFORMATION",
                "category": "terraform",
                "sensitive": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": controller_workspace_id,
                        "type": "workspaces"
                    }
                }
            }
        }
    }
    sleep(1)

    response = requests.post(url, json=jsonData, headers=terraform_header)

    url = ''
    jsonData = ''
    response = ''

    # Step Three: Get a configuration upload URL for the workspace
    url = ('https://' + terraform_url + '/workspaces/' +
           controller_workspace_id + '/configuration-versions')

    jsonData = {
        "data": {
            "type": "configuration-versions",
            "attributes": {
                "auto-queue-runs": True
            }
        }
    }

    sleep(1)
    response = requests.post(url, json=jsonData, headers=terraform_header)
    data_json = response.json()

    # Parse out the upload URL
    upload_url = data_json['data']['attributes']['upload-url']

    # Parse and store configuration id to destory environment later.
    config_id = data_json['data']['id']
    environment.db_aviatrix_controller_tf_config_id = config_id
    db.session.commit()

    # Step Four: Upload AviatrixContoller.tar.gz to Terraform to deploy AWS elements & Aviatrix Controller within
    p = Path(__file__).with_name('launch_environment.tar.gz')
    with p.open('rb') as f:
        data = f.read()

    response = requests.put(upload_url, data=data,
                            headers={'Content-Type': 'application/octet-stream'})

    sleep(300)

    url = ''
    jsonData = ''
    response = ''

    # Step Five: Get the Terraform Coud Run-ID in order to get output file
    environment = EnvStateTable.query.first()
    tf_workspace_id = environment.db_controller_workspace_id

    url = ('https://' + terraform_api_key +
           '/workspaces/' + tf_workspace_id + '/runs')

    response = requests.get(url, headers=terraform_header)
    data_json = response.json()
    run_id = data_json['data'][0]['id']

    # Step Six: Get the log-read-url from the Run
    url = ('https://' + terraform_url + '/runs/' + run_id + '/apply')

    response = requests.get(url, headers=terraform_header)
    data_json = response.json()
    log_read_url = data_json['data']['attributes']['log-read-url']

    url = ''
    jsonData = ''
    response = ''

    # Step Seven: Get the text body back from the log read url to parse for controller IPs

    response = requests.get(log_read_url)

    raw_ips = re.findall(
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', response.text)

    public_ip = str(raw_ips[0])
    environment.db_aviatrix_sst_public_ip = public_ip
    db.session.commit()


def Destroy_Environment():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    terraform_api_key = user.db_terraform_api_key
    terraform_org_name = user.db_terraform_org_name
    terraform_header = {
        'Authorization': 'Bearer ' + terraform_api_key,
        'Content-Type': 'application/vnd.api+json'
    }
    terraform_url = 'app.terraform.io/api/v2'
    tf_workspace_id = environment.db_controller_workspace_id
    tf_config_id = environment.db_aviatrix_controller_tf_config_id

    # Step One: Backout / Destroy the plan that deployed the controller into AWS
    url = ('https://' + terraform_url + '/runs')

    jsonData = {
        "data": {
            "attributes": {
                "message": "Labkit Button, Destroy Environment",
                "is-destroy": True
            },
            "type": "runs",
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": tf_workspace_id
                    }
                },
                "configuration-version": {
                    "data": {
                        "type": "configuration-versions",
                        "id": tf_config_id
                    }
                }
            }
        }
    }

    response = requests.post(url, json=jsonData, headers=terraform_header)
    sleep(300)

    url = ''
    jsonData = ''
    response = ''

    # Step Two: Delete the TF Workspace

    url = ('https://' + terraform_url + "/organizations/" +
           terraform_org_name + "/workspaces/LABKIT_AVIATRIX_CONTROLLER_WORKSPACE")
    response = requests.delete(url, headers={
        'Authorization': 'Bearer ' + terraform_api_key, 'Content-Type': 'application/vnd.api+json'})

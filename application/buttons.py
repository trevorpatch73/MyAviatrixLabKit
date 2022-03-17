from . import db
from .data_models import EnvInputTable, EnvStateTable
import re
import requests
from time import sleep


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

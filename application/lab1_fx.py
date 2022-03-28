from urllib import response
from . import db
from .data_models import EnvInputTable, EnvStateTable
from time import sleep
import requests
import json
from json import JSONEncoder, JSONDecoder
import urllib3
import re
from os import *
from pathlib import Path
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def Launch_Lab1():
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
                "name": "MY_AVIATRIX_LAB_KIT_LAB1_WORKSPACE",
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



def Destroy_Lab1():
    pass

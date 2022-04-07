from . import db
from .data_models import EnvInputTable, EnvStateTable
import re
import requests
from time import sleep
from os import *
from pathlib import Path
import json
from json import JSONEncoder, JSONDecoder


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

    # Step Four: Upload AviatrixContoller.tar.gz to Terraform to deploy AWS elements &
    # Aviatrix Controller within
    p = Path(__file__).with_name('launch_environment.tar.gz')
    with p.open('rb') as f:
        data = f.read()

    response = requests.put(upload_url, data=data,
                            headers={'Content-Type': 'application/octet-stream'})

    sleep(200)

    url = ''
    jsonData = ''
    response = ''

    # Step Five: Get the Terraform Coud Run-ID in order to get output file
    environment = EnvStateTable.query.first()
    tf_workspace_id = environment.db_controller_workspace_id
    print(tf_workspace_id)

    url = ('https://' + terraform_url +
           '/workspaces/' + tf_workspace_id + '/runs')
    print(url)

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


def Launch_Lab1_Aviatrix():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    aws_acct_num = user.db_aws_acct_num
    aws_key_id = user.db_aws_key_id
    aws_key_value = user.db_aws_key_value
    controller_ip = environment.db_aviatrix_controller_public_ip
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
                "name": "MALK_LAB1_AVIATRIX_WORKSPACE",
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
    malk_lab1_aviatrix_workspace_id = data_json['data']['id']
    environment.db_malk_lab1_aviatrix_workspace_id = malk_lab1_aviatrix_workspace_id
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
                "description": "AWS API Key ID",
                "category": "terraform",
                # "sensitive": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_aviatrix_workspace_id,
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
                        "id": malk_lab1_aviatrix_workspace_id,
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
                "key": "aws_acct_num",
                "value": aws_acct_num,
                "description": "Account Number",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_aviatrix_workspace_id,
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
                "key": "controller_ip",
                "value": controller_ip,
                "description": "Aviatrix Controller IP",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_aviatrix_workspace_id,
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

    # Step Three: Get a configuration upload URL for the workspace
    url = ('https://' + terraform_url + '/workspaces/' +
           malk_lab1_aviatrix_workspace_id + '/configuration-versions')

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
    environment.db_malk_lab1_aviatrix_tf_config_id = config_id
    db.session.commit()

    # Step Four: Upload .tar.gz to Terraform to deploy AWS elements &
    p = Path(__file__).with_name('lab_1_aviatrix.tar.gz')
    with p.open('rb') as f:
        data = f.read()

    response = requests.put(upload_url, data=data,
                            headers={'Content-Type': 'application/octet-stream'})

    sleep(600)

    url = ''
    jsonData = ''
    response = ''

    # Step Five: Get the Terraform Coud Run-ID in order to get output file
    url = ('https://' + terraform_url +
           '/workspaces/' + malk_lab1_aviatrix_workspace_id + '/runs')

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

    # Step Seven: Get the text body back from the log read url to parse for subnet and vpc ids

    response = requests.get(log_read_url)

    data = response.text

    objects = data.split('\n')

    for object in objects:
        if '"@message":"Outputs:' in object:
            print('----------------------------')
            print('----------------------------')
            print('----------------------------')
            print(f'{object}')
            print('----------------------------')
            print('----------------------------')
            print('----------------------------')

            aws_us_e2_shr_svcs_subnet_id_pattern = re.findall(
                r'(\"AWS-US-E2-SHR-SVCS-SUBNET-ID\":{\"[\w]+\":[\w]+,\"[\w]+\":\"[\w]+\",\"[\w]+\":\"subnet-[\w]+\"})', object)
            aws_us_e2_shr_svcs_subnet_id = re.findall(
                r'(subnet-[\w]+)', aws_us_e2_shr_svcs_subnet_id_pattern[0])
            print(
                f'aws_us_e2_shr_svcs_subnet_id is {aws_us_e2_shr_svcs_subnet_id}')
            environment.db_aws_us_e2_shr_svcs_subnet_id = aws_us_e2_shr_svcs_subnet_id[0]
            db.session.commit()

            aws_us_e2_shr_svcs_vpc_id_pattern = re.findall(
                r'(\"AWS-US-E2-SHR-SVCS-VPC-ID\":{\"[\w]+\":[\w]+,\"[\w]+\":\"[\w]+\",\"[\w]+\":\"vpc-[\w]+\"})', object)
            print(f'{aws_us_e2_shr_svcs_vpc_id_pattern}')
            aws_us_e2_shr_svcs_vpc_id = re.findall(
                r'(vpc-[\w]+)', aws_us_e2_shr_svcs_vpc_id_pattern[0])
            print(f'aws_us_e2_shr_svcs_vpc_id is {aws_us_e2_shr_svcs_vpc_id}')
            environment.aws_us_e2_shr_svcs_vpc_id = aws_us_e2_shr_svcs_vpc_id[0]
            db.session.commit()

            aws_us_w2_bu1_mono_subnet_id_pattern = re.findall(
                r'(\"AWS-US-W2-BU1-MONO-SUBNET-ID\":{\"[\w]+\":[\w]+,\"[\w]+\":\"[\w]+\",\"[\w]+\":\"subnet-[\w]+\"})', object)
            aws_us_w2_bu1_mono_subnet_id = re.findall(
                r'(subnet-[\w]+)', aws_us_w2_bu1_mono_subnet_id_pattern[0])
            print(
                f'aws_us_w2_bu1_mono_subnet_id is {aws_us_w2_bu1_mono_subnet_id}')
            environment.aws_us_w2_bu1_mono_subnet_id = aws_us_w2_bu1_mono_subnet_id[0]
            db.session.commit()

            aws_us_w2_bu1_mono_vpc_id_pattern = re.findall(
                r'(\"AWS-US-W2-BU1-MONO-VPC-ID\":{\"[\w]+\":[\w]+,\"[\w]+\":\"[\w]+\",\"[\w]+\":\"vpc-[\w]+\"})', object)
            aws_us_w2_bu1_mono_vpc_id = re.findall(
                r'(vpc-[\w]+)', aws_us_w2_bu1_mono_vpc_id_pattern[0])
            print(f'aws_us_w2_bu1_mono_vpc_id is {aws_us_w2_bu1_mono_vpc_id}')
            environment.aws_us_w2_bu1_mono_vpc_id = aws_us_w2_bu1_mono_vpc_id[0]
            db.session.commit()


def Launch_Lab1_SHR_SVCS():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    aws_key_id = user.db_aws_key_id
    aws_key_value = user.db_aws_key_value
    terraform_api_key = user.db_terraform_api_key
    terraform_org_name = user.db_terraform_org_name
    aws_us_e2_shr_svcs_subnet_id = environment.db_aws_us_e2_shr_svcs_subnet_id
    aws_us_e2_shr_svcs_vpc_id = environment.aws_us_e2_shr_svcs_vpc_id
    terraform_header = {
        'Authorization': 'Bearer ' + terraform_api_key,
        'Content-Type': 'application/vnd.api+json'
    }
    terraform_url = 'app.terraform.io/api/v2'

    # Step One: Create a workspace in TF Cloud
    jsonData = {
        "data": {
            "attributes": {
                "name": "MALK_LAB1_SHR_SVCS_WORKSPACE",
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
    malk_lab1_shr_svcs_workspace_id = data_json['data']['id']
    environment.db_malk_lab1_shr_svcs_workspace_id = malk_lab1_shr_svcs_workspace_id
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
                "description": "AWS API Key ID",
                "category": "terraform",
                # "sensitive": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_shr_svcs_workspace_id,
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
                        "id": malk_lab1_shr_svcs_workspace_id,
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
                "key": "aws_us_e2_shr_svcs_subnet_id",
                "value": aws_us_e2_shr_svcs_subnet_id,
                "description": "AWS Subnet ID",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_shr_svcs_workspace_id,
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
                "key": "aws_us_e2_shr_svcs_vpc_id",
                "value": aws_us_e2_shr_svcs_vpc_id,
                "description": "AWS VPC ID",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_shr_svcs_workspace_id,
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

    # Step Three: Get a configuration upload URL for the workspace
    url = ('https://' + terraform_url + '/workspaces/' +
           malk_lab1_shr_svcs_workspace_id + '/configuration-versions')

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
    environment.db_malk_lab1_shr_svcs_tf_config_id = config_id
    db.session.commit()

    # Step Four: Upload tar.gz to Terraform to deploy AWS elements &
    p = Path(__file__).with_name('lab_1_shr_svcs.tar.gz')
    with p.open('rb') as f:
        data = f.read()

    response = requests.put(upload_url, data=data,
                            headers={'Content-Type': 'application/octet-stream'})

    sleep(120)

    url = ''
    jsonData = ''
    response = ''


def Launch_Lab1_BU1():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    aws_key_id = user.db_aws_key_id
    aws_key_value = user.db_aws_key_value
    terraform_api_key = user.db_terraform_api_key
    terraform_org_name = user.db_terraform_org_name
    aws_us_w2_bu1_mono_subnet_id = environment.db_aws_us_w2_bu1_mono_subnet_id
    aws_us_w2_bu1_mono_vpc_id = environment.aws_us_w2_bu1_mono_vpc_id
    terraform_header = {
        'Authorization': 'Bearer ' + terraform_api_key,
        'Content-Type': 'application/vnd.api+json'
    }
    terraform_url = 'app.terraform.io/api/v2'

    # Step One: Create a workspace in TF Cloud
    jsonData = {
        "data": {
            "attributes": {
                "name": "MALK_LAB1_BU1_WORKSPACE",
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
    malk_lab1_bu1_workspace_id = data_json['data']['id']
    environment.db_malk_lab1_bu1_workspace_id = malk_lab1_bu1_workspace_id
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
                "description": "AWS API Key ID",
                "category": "terraform",
                # "sensitive": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_bu1_workspace_id,
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
                        "id": malk_lab1_bu1_workspace_id,
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
                "key": "aws_us_w2_bu1_mono_subnet_id",
                "value": aws_us_w2_bu1_mono_subnet_id,
                "description": "AWS Subnet ID",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_bu1_workspace_id,
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
                "key": "aws_us_w2_bu1_mono_vpc_id",
                "value": aws_us_w2_bu1_mono_vpc_id,
                "description": "AWS VPC ID",
                "category": "terraform",
                "sensitive": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": malk_lab1_bu1_workspace_id,
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

    # Step Three: Get a configuration upload URL for the workspace
    url = ('https://' + terraform_url + '/workspaces/' +
           malk_lab1_bu1_workspace_id + '/configuration-versions')

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
    environment.db_malk_lab1_bu1_tf_config_id = config_id
    db.session.commit()

    # Step Four: Upload tar.gz to Terraform to deploy AWS elements &
    p = Path(__file__).with_name('lab_1_bu1.tar.gz')
    with p.open('rb') as f:
        data = f.read()

    response = requests.put(upload_url, data=data,
                            headers={'Content-Type': 'application/octet-stream'})

    sleep(120)

    url = ''
    jsonData = ''
    response = ''


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
    sleep(200)

    url = ''
    jsonData = ''
    response = ''

    # Step Two: Delete the TF Workspace

    url = ('https://' + terraform_url + "/organizations/" +
           terraform_org_name + "/workspaces/MY_AVIATRIX_LAB_KIT_CONTROLLER_WORKSPACE")

    response = requests.delete(url, headers={
        'Authorization': 'Bearer ' + terraform_api_key, 'Content-Type': 'application/vnd.api+json'})


def Destroy_Lab1():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    malk_lab1_aviatrix_workspace_id = environment.db_malk_lab1_aviatrix_workspace_id
    malk_lab1_aviatrix_tf_config_id = environment.db_malk_lab1_aviatrix_tf_config_id
    terraform_api_key = user.db_terraform_api_key
    terraform_org_name = user.db_terraform_org_name
    terraform_header = {
        'Authorization': 'Bearer ' + terraform_api_key,
        'Content-Type': 'application/vnd.api+json'
    }
    terraform_url = 'app.terraform.io/api/v2'

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
                        "id": malk_lab1_aviatrix_workspace_id
                    }
                },
                "configuration-version": {
                    "data": {
                        "type": "configuration-versions",
                        "id": malk_lab1_aviatrix_tf_config_id
                    }
                }
            }
        }
    }

    response = requests.post(url, json=jsonData, headers=terraform_header)
    sleep(200)

    url = ''
    jsonData = ''

    # Step Two: Delete the TF Workspace

    url = ('https://' + terraform_url + "/organizations/" +
           terraform_org_name + "/workspaces/MALK_LAB1_AVIATRIX_WORKSPACE")

    response = requests.delete(url, headers={
        'Authorization': 'Bearer ' + terraform_api_key, 'Content-Type': 'application/vnd.api+json'})

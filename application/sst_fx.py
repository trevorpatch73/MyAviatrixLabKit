from urllib import response
from . import db
from .data_models import EnvInputTable, EnvStateTable
from time import sleep
import requests
import json
from json import JSONEncoder, JSONDecoder
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def sst_mode_selection():
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/mode-selection')
    text = '{"is_advance":false}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(1)


def sst_aws_config():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip
    aws_key_id = user.db_aws_key_id
    aws_key_value = user.db_aws_key_value

    url = ('https://' + target + '/api/v1.0/aws-config')
    text = '{"key_id":"' + aws_key_id + \
        '","secret_key":"' + aws_key_value + '"}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(1)


def sst_launch_controller():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip
    recovery_email = user.db_recovery_email

    url = ('https://' + target + '/api/v1.0/launch-controller')
    text = '{"email":"' + recovery_email + '","recovery_email":"' + recovery_email + \
        '","password":"P@ssw0rd","confirm_password":"P@ssw0rd","controller_license_type":"meteredplatinum","controller_license":""}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(120)

    # Check For Success
    check_url = ('https://' + target + '/api/v1.0/get-statestatus')
    retry = 0
    while True:
        check = requests.get(check_url, verify=False)
        data = check.json()
        stateName = data['data']['stateName']
        status = data['data']['status']
        if stateName == 'launchController' and status == 'success':
            break
        else:
            if retry == 1200:
                break
            else:
                retry = retry + 1
                print('stateName: ' + str(stateName))
                print('status: ' + str(status))
                print('retry: ' + str(retry))
                sleep(5)


def sst_launch_transit_aws():
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/launch-transit-aws')
    text = '{"command":false}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(1)


def sst_launch_ec2_spokevpc():
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/launch-ec2-spokevpc')
    text = '{"command":false}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(1)


def sst_skip_transit_azure():
    environment = EnvStateTable.query.first()
    sst_headers = {'Content-Type': 'text/plain'}
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/skip-transit-azure')
    text = '{"command":true}'
    response = requests.post(url, data=text, headers=sst_headers, verify=False)
    sleep(1)


def sst_controller_ip():
    environment = EnvStateTable.query.first()
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/get-statestatus')
    response = requests.get(url, verify=False)

    raw_ips = re.findall(
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', response.text)

    public_ip = str(raw_ips[0])
    environment.db_aviatrix_controller_public_ip = public_ip
    db.session.commit()


def sst_delete_resources():
    environment = EnvStateTable.query.first()
    target = environment.db_aviatrix_sst_public_ip

    url = ('https://' + target + '/api/v1.0/delete-resources')
    response = requests.delete(url, verify=False)
    sleep(60)

    # Check For Success
    check_url = ('https://' + target + '/api/v1.0/get-statestatus')
    retry = 0
    while True:
        check = requests.get(check_url, verify=False)
        data = check.json()
        stateName = data['data']['stateName']
        status = data['data']['status']
        if stateName == 'deleteResources' and status == 'success':
            break
        else:
            if retry == 1200:
                break
            else:
                retry = retry + 1
                print('stateName: ' + str(stateName))
                print('status: ' + str(status))
                print('retry: ' + str(retry))
                sleep(5)

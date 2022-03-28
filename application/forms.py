from flask import *
from flask_wtf import *
from wtforms import *
from wtforms.validators import *


class EnvVarForm(FlaskForm):
    aws_acct_num = StringField('AWS Account Number: ')
    aws_key_id = StringField('AWS Key ID: ')
    aws_key_value = StringField('AWS Key Value: ')
    terraform_org_name = StringField('Terraform Organization Name: ')
    terraform_api_key = StringField('Terraform API Key for Organization: ')
    recovery_email = StringField('Enter a recovery email: ')
    submit = SubmitField('Submit')

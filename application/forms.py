from flask import *
from flask_wtf import *
from wtforms import *
from wtforms.validators import *


class EnvVarForm(FlaskForm):
    aws_key_id = StringField('AWS Key ID: ')
    aws_key_value = StringField('AWS Key Value: ')
    terraform_org_name = StringField('Terraform Organization Name: ')
    terraform_api_key = StringField('Terraform API Key for Organization: ')
    submit = SubmitField('Submit')

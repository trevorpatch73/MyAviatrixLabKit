from . import db
from flask_sqlalchemy import *
from sqlalchemy.sql import *


class EnvVarTable(db.Model):
    __tablename__ = 'Environmental Variables Table'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    environment_state = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_aws_key_id = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_aws_key_value = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_terraform_org_name = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_terraform_api_key = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )

from . import db
from flask_sqlalchemy import *
from sqlalchemy.sql import *


class EnvInputTable(db.Model):
    __tablename__ = 'Environmental Input Table'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    db_aws_acct_num = db.Column(
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
    db_recovery_email = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )


class EnvStateTable(db.Model):
    __tablename__ = 'Environmental State Table'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    db_environment_state = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_aviatrix_sst_public_ip = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_aviatrix_controller_public_ip = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )
    db_controller_workspace_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_aviatrix_controller_tf_config_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_malk_lab1_aviatrix_workspace_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_malk_lab1_aviatrix_tf_config_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_malk_lab1_shr_svcs_workspace_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_malk_lab1_shr_svcs_tf_config_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_aws_us_e2_shr_svcs_subnet_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_aws_us_e2_shr_svcs_vpc_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_aws_us_w2_bu1_mono_subnet_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )
    db_aws_us_w2_bu1_mono_vpc_id = db.Column(
        db.String(1000),
        nullable=True,
        unique=True
    )

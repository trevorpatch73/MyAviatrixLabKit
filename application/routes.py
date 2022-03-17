from hashlib import new
from flask import *
from .forms import EnvVarForm
from .data_models import EnvInputTable, EnvStateTable
from . import db

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET', 'POST'])
def default():
    return redirect(url_for('routes.homepage'))


@routes.route('/homepage', methods=['GET', 'POST'])
def homepage():
    user = EnvInputTable.query.first()
    environment = EnvStateTable.query.first()
    aws_key_id = None
    aws_key_value = None
    terraform_org_name = None
    terraform_api_key = None
    if request.method == 'POST':
        form = EnvVarForm()
        if form.validate_on_submit():
            aws_key_id = form.aws_key_id.data
            aws_key_value = form.aws_key_value.data
            terraform_org_name = form.terraform_org_name.data
            terraform_api_key = form.terraform_api_key.data
            if user is None:
                entry = EnvInputTable(
                    db_aws_key_id=aws_key_id,
                    db_aws_key_value=aws_key_value,
                    db_terraform_org_name=terraform_org_name,
                    db_terraform_api_key=terraform_api_key,
                )
                db.session.add(entry)
                db.session.commit()
                return redirect(url_for('routes.homepage'))
            else:
                if form.aws_key_id == '':
                    pass
                else:
                    user.db_aws_key_id = aws_key_id
                    db.session.commit()
                if form.aws_key_value == '':
                    pass
                else:
                    user.db_aws_key_value = aws_key_value
                    db.session.commit()
                if form.terraform_org_name == '':
                    pass
                else:
                    db.db_terraform_org_name = terraform_org_name
                    db.session.commit()
                if form.terraform_api_key == '':
                    pass
                else:
                    db.db_terraform_org_name = terraform_api_key
                    db.session.commit()
        else:
            pass
    else:
        form = EnvVarForm()
    if environment is None:
        state = 'new'
        entry = EnvStateTable(
            db_environment_state=state,
            db_aviatrix_sst_public_ip=state,
            db_aviatrix_controller_public_ip=state,
            db_intital_launch_tf_workspace_id=state,
            db_intital_launch_tf_config_id=state
        )
        db.session.add(entry)
        db.session.commit()
    elif user.db_aws_key_id is not None and user.db_aws_key_value is not None and user.db_terraform_org_name is not None and user.db_terraform_api_key is not None:
        state = 'provision_controller'
        environment.db_environment_state = state
        db.session.commit()
    else:
        state = environment.db_environment_state
    return render_template(
        'homepage.html',
        form=form,
        state=state,
        aws_key_id=aws_key_id,
        aws_key_value=aws_key_value,
        terraform_org_name=terraform_org_name,
        terraform_api_key=terraform_api_key
    )

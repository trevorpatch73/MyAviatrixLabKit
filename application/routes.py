from flask import *
from .forms import EnvVarForm
from .data_models import EnvVarTable
from . import db

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET', 'POST'])
def default():
    return redirect(url_for('routes.homepage'))


@routes.route('/homepage', methods=['GET', 'POST'])
def homepage():
    user = EnvVarTable.query.first()
    if request.method == 'POST':
        form = EnvVarForm()
        if form.validate_on_submit():
            if user is None:
                entry = EnvVarTable(
                    db_aws_key_id=form.aws_key_id,
                    db_aws_key_value=form.aws_key_value,
                    db_terraform_org_name=form.terraform_org_name,
                    db_terraform_api_key=form.terraform_api_key
                )
                db.session.add(entry)
                db.session.commit()
                return redirect(url_for('routes.homepage'))
            else:
                if form.aws_key_id == '':
                    pass
                else:
                    user.db_aws_key_id = form.aws_key_id
                    db.session.commit()
                if form.aws_key_value == '':
                    pass
                else:
                    user.db_aws_key_value = form.aws_key_value
                    db.session.commit()
                if form.terraform_org_name == '':
                    pass
                else:
                    db.db_terraform_org_name = form.terraform_org_name
                    db.session.commit()
                if form.terraform_api_key == '':
                    pass
                else:
                    db.db_terraform_org_name = form.terraform_api_key
                    db.session.commit()
        else:
            pass
    else:
        form = EnvVarForm()
    return render_template(
        'homepage.html',
        form=form
    )

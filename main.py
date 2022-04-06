###############################
### PY INSTALL REQUIREMENTS ###
###############################
# pip install flask
# pip install flask-login
# pip install flask-sqlalchemy
# pip install flask-wtf

from application import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

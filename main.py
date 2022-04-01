###############################
### PY INSTALL REQUIREMENTS ###
###############################
# pip install flask
# pip install flask-login
# pip install flask-sqlalchemy
# pip install flask-wtf


# bastion@bastion-host-01:~$ export CONTENT_DIRECTORY=./AviatrixController
# bastion@bastion-host-01:~$ export UPLOAD_FILE_NAME="./content-$(date +%s).tar.gz"
# bastion@bastion-host-01:~$ tar -zcvf "$UPLOAD_FILE_NAME" -C "$CONTENT_DIRECTORY" .

from application import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

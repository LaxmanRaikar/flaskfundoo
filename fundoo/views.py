import self as self
from app import app,mail
from app import db,bcrypt
from flask import jsonify, request, flash
from flask_mail import Message
from models import sign_up
from sqlalchemy import create_engine
from flask import url_for

from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.sql.functions import current_user

engine = create_engine('postgresql://laxman777:password@localhost/fundooproject', echo=True)
from wtforms import PasswordField, StringField, SubmitField, ValidationError



@app.route('/signup', methods = ['POST'])
def SignUp():
    """ This method is used to register the account """
    response = {
        'success': False,
        'message': 'Some went wrong',
        'data': []
    }
    try:
        username = request.form.get("username")  # getting the username from user
        email_id = request.form.get("email_id")  # getting the email_id from user
        mobile_no = request.form.get("mobile_no") # getting the mobile no from user
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        # getting password and confirm password to check the password match\
        if password != confirm_password:
            return "both passwords doesnot match"
        else:
            print("i am here", username, email_id, mobile_no, password, confirm_password)
        # adding data to db
            add = sign_up(username=username, email_id=email_id, mobile_no=mobile_no, password=password, confirm_password=confirm_password)
            data = [username, email_id, mobile_no, password, confirm_password]
            print("here", data)
            db.session.add(add)
            db.session.commit()

            response['success'] = True
            response['message'] = 'successfully account is created'
            response['data'] = data
            response = jsonify(response)
            return response

    except ValueError:

        response['message'] = 'fileds are not filled correctly'
        response = jsonify(response)
        response.status_code = 400

    except ConnectionError:

        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503

    except IOError:

        response['message'] = 'improper input'
        response = jsonify(response)
        response.status_code = 400

    except Exception as e:
        print(e)
        response = jsonify(response)
        response.status_code = 400

    return response


@app.route('/signin', methods=['GET', 'POST'])
def SignIn():
    """ this method is used to login """
    response = {
        'success': False,
        'message': 'Some went wrong',
        'data': []
    }
    try:
        email_id = request.form.get("email_id")
        password = request.form.get("password")
        # here doing query with db
        login = sign_up.query.filter_by(email_id=email_id, password=password).first()
        # if given data is not present in db it will return none
        data=[email_id, password]
        if login is not None:
            response['success'] = True
            response['message'] = 'succesfully logged in'
            response['data'] = data
            response = jsonify(response)
            return response
        response['data'] = data
        response['message']="invalid credentials"
        return response
    except ValueError:
        response['message'] = 'fileds are not filled correctly'
        response = jsonify(response)
        response.status_code = 400

    except ConnectionError:
        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503

    except Exception as e:
        print(e)
        response = jsonify(response)
        response.status_code = 400
    return response


def send_reset_email(user):
    """ this method is used to send mail"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='laxmanraikar777@gmail.com',
                  recipients=[user.email_id])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """ this method is used to reset the password """
    response = {
        'success': False,
        'message': 'something went wrong'
    }
    # getting the email id from user to which password should be changed
    email_id = request.form.get("email_id")
    # checking the user is is db
    user = sign_up.query.filter_by(email_id=email_id).first()
    if user:
        send_reset_email(user)  # calling the method to send mail
        response['success'] = True
        response['message'] = "A link has been sent to your email id to reset password please checkout"
        return response
    else:
        response['success'] = False
        response['message'] = "this user is not in our database "


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    response = {
        'success': False,
        'message': 'Some went wrong',
    }
    mypassword = request.form.get('password')
    confirm_password = request.form.get('confirm')
    user = sign_up.verify_reset_token(token)
    myuser = sign_up.query.filter_by(id=user.id).first()
    if mypassword == confirm_password:
        myuser.password = mypassword
        myuser.confirm_password = confirm_password
        db.session.commit()
        response['success']=True
        response['message']="successfully password has changed"
        return response
    else:
        response['success'] = False
        response['message'] = 'password does not match'
        return response













if __name__ == '__main__':
    app.run(debug=True)

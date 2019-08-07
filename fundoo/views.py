import self as self
from app import app,mail,su
from app import db,bcrypt
from flask import jsonify, request
from flask_mail import Message
from models import sign_up
from flask import url_for
import short_url
import jwt
from werkzeug.utils import redirect


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
        mobile_no = request.form.get("mobile_no")  # getting the mobile no from user
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
            db.session.add(add)
            db.session.commit()
            user = sign_up.query.filter_by(email_id=email_id).first()
            send_link_email(user)
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
        login = sign_up.query.filter_by(email_id=email_id, password=password, is_active=True).first()
        # if given data is not present in db it will return none
        data = [email_id, password]
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


def send_link_email(user):
    """ this method is used to activate the account"""
    token = user.get_reset_token()
    print("21121111", int(token))
    mytoken=short_url.encode(token)
    print('mytoken1234',mytoken)
    msg = Message('Activation link',
                  sender='laxmanraikar777@gmail.com',
                  recipients=[user.email_id])
    msg.body = f'''To activate the your account, visit the following link:
    {url_for('activation', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''

    mail.send(msg)  # here sending the message


def send_reset_email(user):
    """ this method is used to send mail to reset the password"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='laxmanraikar777@gmail.com',
                  recipients=[user.email_id])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_request', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)  # here sending the message


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
    """ this method is used to update the password"""
    response = {
        'success': False,
        'message': 'Some went wrong',
    }
    mypassword = request.form.get('password')  # getting the new password from user
    confirm_password = request.form.get('confirm')  # confirm the new password
    user = sign_up.verify_reset_token(token)    # calling the the verify token method to verify the token
    myuser = sign_up.query.filter_by(id=user.id).first()    # getting the user
    if mypassword == confirm_password:
        myuser.password = mypassword
        myuser.confirm_password = confirm_password
        db.session.commit()
        response['success'] = True
        response['message'] = "successfully password has changed"
        return response
    else:
        response['success'] = False
        response['message'] = 'password does not match'
        return response


@app.route('/activation/<token>', methods=['GET', 'POST'])
def activation(token):

    user = sign_up.verify_reset_token(token)
    user.is_active = True
    db.session.commit()
    return 'Your email is activated!!! Thank you!!!'


if __name__ == '__main__':
    app.run(debug=True)

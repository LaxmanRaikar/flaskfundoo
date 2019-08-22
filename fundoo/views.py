from app import app,mail,su
from app import db,bcrypt,es,rbac
from datetime import datetime
from flask import jsonify, request, render_template, url_for
from flask_dance.contrib.linkedin import linkedin
from models import sign_up,book,User, load_user, Role, User
from utility import send_link_email, send_reset_email
import logging
# from services.user import User
from flask import Blueprint
from flask_dance.contrib.github import github
from flask_dance.contrib.dropbox import dropbox
from flask_dance.contrib.twitter import twitter
from werkzeug.utils import redirect
# from flask_login import login_user,current_user, logout_user


mod = Blueprint('users', __name__)



@app.route('/signup', methods = ['POST'])
def register():
    """ Validations & returning data """
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
        # getting password and confirm password to check the password match
        if username is None or \
                email_id is None or\
                mobile_no is None or\
                password is None or \
                confirm_password is None:
            app.logger.warning('all fields are not valid')
            raise Exception('All fields are mandatory')
        if password != confirm_password:
            app.logger.warning('password does not matches')
            raise Exception
        else:
            register_user = sign_up(email_id=email_id, password=sign_up.generate_hash(password),
                                    confirm_password=sign_up.generate_hash(confirm_password),
                                    mobile_no=mobile_no,
                                    username=username)
            register_user.save_to_db()
            data = [username, email_id, mobile_no, password, confirm_password]
            user = sign_up.find_by_username(email_id)
            send_link_email(user)
            response['success'] = True
            response['message'] = 'successfully account is created'
            response['data'] = data
            response = jsonify(response)
            return response

    except ValueError as e:
        logging.error(jsonify(str(e)))
        response['message'] = 'fileds are not filled correctly'
        response = jsonify(response)
        response.status_code = 400

    except ConnectionError as e:
        logging.error(jsonify(str(e)))
        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503

    except IOError as e:
        logging.error(jsonify(str(e)))
        response['message'] = 'improper input'
        response = jsonify(response)
        response.status_code = 400

    except Exception as e:
        logging.error(jsonify(str(e)))
    return response


@app.route('/signin', methods=['GET', 'POST'])
def log_in():
    """ this method is used to login """
    response = {
        'success': False,
        'message': 'Some went wrong',
        'data': []
    }
    try:
        email_id = request.form.get("email_id")     # getting the email id from user
        password = request.form.get("password")     # getting the password from the user
        verify_email = sign_up.find_by_username(email_id)
        if verify_email is None:                    # query email id in db
            app.logger.warning('this user is not present in db ')
            response['message'] = "this user is not present"
            response['success'] = False

        get_data = sign_up.query.filter(email_id == email_id).first()   # getting the password of user from db
        # matching the passwords
        my_password = sign_up.verify_hash(password, get_data.password)
        if verify_email and my_password:
            response['success'] = True
            response['message'] = 'succesfully logged in'
            response['data'] = email_id
            response = jsonify(response)
            # login_user(get_data)

            return response
        else:
            response['message'] = 'password does not match'
            response['success'] = False
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
        response = jsonify(str(e))
        response.status_code = 400
    return response


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """ this method is used to reset the password """
    response = {
        'success': False,
        'message': 'something went wrong'
    }
    # getting the email id from user to which password should be changed
    email_id = request.form.get("email_id")
    my_user = User(email_id=email_id)
    user = my_user.forgotPassword()
    if user:
        send_reset_email(user)  # calling the method to send mail
        response['success'] = True
        response['message'] = "A link has been sent to your email id to reset password please checkout"
        return response
    else:
        app.logger.warning('user not found')
        response['success'] = False
        response['message'] = "this user is not in our database "


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """ this method is used to update the password"""
    response = {
        'success': False,
        'message': 'Some went wrong',
    }
    print('inside ',token)
    mypassword = request.form.get('password')  # getting the new password from user
    confirm_password = request.form.get('confirm_password')  # confirm the new password
    user = sign_up.verify_reset_token(token)    # calling the the verify token method to verify the token
    print('myid', user)
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
    """ this method is used to change the is_active db field to activate the given id"""
    response = {
        'success': False,
        'message': 'something went wrong'
    }
    try:
        user = sign_up.verify_reset_token(token)    # verifying the token
        user.is_active = True   # change the db field value
        db.session.commit()
        return 'Your email is activated!!! Thank you!!!'
    except ConnectionError:
        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503
    except Exception as e:
        print(e)
        response = jsonify(response)
        response.status_code = 400
    return response


@app.route('/resend_activation', methods=['GET', 'POST'])
def resend_activation():
    """ this method is used to resend the activation link to the user mail id"""
    response = {
        'success': False,
        'message': "something bad happend"
    }
    try:
        email_id = request.form.get('email_id')  # here getting the email id of the user
        user = sign_up.query.filter_by(email_id=email_id).first()   # query with db
        if user is None:    # if user is not in db it will return error response
            response['message'] = 'the given email id is not present in our db'
            return response
        else:
            if user.is_active is True:  # if user id is already activated it will return response
                response['message'] = 'the given email id is already activated'
                return response
            else:
                send_link_email(user)  # calling the link generator method
                response['success'] = True
                response['message'] = 'EMAIL HAS SENT SUCCESSFULLY'
                return response
    except ConnectionError:
        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503
    except Exception as e:
        print(e)
        response = jsonify(str(e))
        response.status_code = 400
    return response


@app.route('/pagination', methods=['POST', 'GET'])
def pagination():
    """ this method is used to the pagination """
    page = request.args.get('page', 1, type=int)
    posts = book.query.order_by(book.title.desc()).paginate(page=page, per_page=5)
    print(posts)
    return render_template('index.html', posts=posts)


@app.route('/github')
def github_login():
    """ this method is used to do social login in github """
    if not github.authorized:   # authorizing the git id
        return redirect(url_for('github.login'))
    account_info = github.get('/user')
    if account_info.ok:
        account_info_json = account_info.json()
        return '<h1>Your Github name is {}'.format(account_info_json['login'])
    return '<h1>Request failed!</h1>'


@app.route('/linkedin')
def linked_login():
    """ this method is used to do social login in linked in """
    if not linkedin.authorized:
        return redirect(url_for('linkedin.login'))
    account_info = linkedin.get('/user')
    if account_info.ok:
        account_info_json = account_info.json()
        return '<h1>Your linkedin name is {}'.format(account_info_json['login'])
    return '<h1>Request failed!</h1>'


@app.route('/dropboxlogin')
def dropbox_login():
    """ this method is used to do social login in dropbox """
    if not dropbox.authorized:
        return redirect(url_for('dropbox.login'))
    account_info = dropbox.get('/user')
    if account_info.ok:
        account_info_json = account_info.json()
        return '<h1>Your dropbox name  name is {}'.format(account_info_json['login'])
    return '<h1>Request failed!</h1>'


@app.route('/twitter_login')
def twitter_login():
    """ this method is used to do social login in twitter """
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/verify_credentials.json")
    assert resp.ok
    return "You are @{screen_name} on Twitter".format(screen_name=resp.json()["screen_name"])


@app.route('/insert_data', methods=['POST', 'GET'])
def insert_data():

    title = request.form.get('title')
    content = request.form.get('content')

    body = {
        'title': title,
        'content': content,
        'timestamp': datetime.now()
    }
    result = es.index(index='contents', doc_type='title',  body=body)
    return jsonify(result)


@app.route('/search', methods=['POST', 'GET'])
def search():
    keyword = request.form.get('keyword')

    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["content", "title"]
            }
        }
    }
    res = es.search(index="contents", body=body)
    return jsonify(res['hits']['hits'])


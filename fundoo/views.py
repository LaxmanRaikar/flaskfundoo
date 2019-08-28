from app import app, mail, su
from app import db, bcrypt, es
import nexmo
from datetime import datetime
from flask import jsonify, request, render_template, url_for
from flask_dance.contrib.linkedin import linkedin
from flask_login import login_user
from models import sign_up, book, load_user, Mydata, register, Notes, ok, Label
from self import self
import logging
from utility import send_reset_email, send_link_email
from services.redis import redis_methods
from services.note import Note

from flask import Blueprint
from flask_dance.contrib.github import github
from flask_dance.contrib.dropbox import dropbox
from flask_dance.contrib.twitter import twitter
from werkzeug.utils import redirect
import datetime
from lib.s3_upload import upload_to_s3

import imghdr
from flask_login import login_user, current_user, logout_user

mod = Blueprint('users', __name__)
client = nexmo.Client(key='169b4a9b', secret='R8BmO5JhiGzbFEyU')


@app.route('/signup', methods=['POST'])
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
                email_id is None or \
                mobile_no is None or \
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
            user = sign_up.find_by_email_id(email_id)
            send_link_email(user)
            payload = {'username': username, 'password': password}
            my_token = sign_up.generate_token(self, payload)
            redis_methods.set_method(self, "token", my_token)
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
        email_id = request.form.get("email_id")  # getting the email id from user
        password = request.form.get("password")  # getting the password from the user
        verify_email = sign_up.find_by_email_id(email_id)
        if verify_email is None:  # query email id in db
            app.logger.warning('this user is not present in db ')
            response['message'] = "this user is not present"
            response['success'] = False

        get_data = sign_up.query.filter(email_id == email_id).first()  # getting the password of user from db
        # matching the passwords
        my_password = sign_up.verify_hash(password, get_data.password)
        if verify_email and my_password:
            response['success'] = True
            response['message'] = 'succesfully logged in'
            response['data'] = email_id
            response = jsonify(response)
            login_user(get_data)

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
    my_user = sign_up(email_id=email_id)
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
    print('inside ', token)
    mypassword = request.form.get('password')  # getting the new password from user
    confirm_password = request.form.get('confirm_password')  # confirm the new password
    user = sign_up.verify_reset_token(token)  # calling the the verify token method to verify the token
    print('myid', user)
    myuser = sign_up.query.filter_by(id=user.id).first()  # getting the user
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
        user = sign_up.verify_reset_token(token)  # verifying the token
        user.is_active = True  # change the db field value
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
        user = sign_up.query.filter_by(email_id=email_id).first()  # query with db
        if user is None:  # if user is not in db it will return error response
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
    if not github.authorized:  # authorizing the git id
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
    result = es.index(index='contents', doc_type='title', body=body)
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


@app.route('/data', methods=['POST', 'GET'])
def add():
    print(redis_methods.get_method(self, 'token'))

    return 'a'


@app.route('/sendotp', methods=['POST', 'GET'])
def get():
    """ this method is used to send otp to the registered mobile no
    :param-mobile_no
    :return-request id"""
    response = {
        'success': False,
        'message': 'Some went wrong',
        'data': []
    }
    mobile_no = request.form.get('mobile_no')  # getting the mobile no from user
    if len(mobile_no) == 13:  # validating the mobile no
        data = sign_up.query.filter_by(mobile_no=mobile_no).first()  # query the mobile_no is registered
        if data is not None:
            # sending otp
            res = client.start_verification(
                number=mobile_no,
                brand='login otp',
                code_length='4')
            response['success'] = True
            response['message'] = 'otp sent'
            response['data'] = res['request_id']
        else:
            response['success'] = False
            response['message'] = 'mobile no not found'
    else:
        response['success'] = False
        response['message'] = 'THE GIVEN NUMBER MUST BE  TOTAL 13 DIGITS'
    return response


@app.route('/verify', methods=['POST', 'GET'])
def verify():
    response = {
        'success': False,
        'message': 'Some went wrong',
        'data': []
    }
    try:
        request_id = request.form.get('request_id')
        code = request.form.get('code')
        res = client.check_verification(request_id=request_id, code=code)
        if res["status"] == "0":
            response['success'] = True
            response['message'] = 'Verification successful'
            response = jsonify(response)
            response.status_code = 200
        else:
            raise ValueError
    except ValueError:
        response['message'] = response["error_text"]
        response = jsonify(response)
        response.status_code = 400
    except ConnectionError:
        response['message'] = 'check your internet connection'
        response = jsonify(response)
        response.status_code = 503
    except Exception:
        response = jsonify(response)
        response.status_code = 400
    return response


@app.route('/createnote', methods=['POST'])
def create():
    """ this merthod is used to add the note"""
    response = {
        'success': False,
        'message': 'something went wrong',
        'data': []
    }
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        color = request.form.get('color')
        image = request.files.get('image')
        is_archive = request.form.get('is_archive')
        is_pinned = request.form.get('is_pinned')
        remainder = request.form.get('remainder')
        if title and description is not None:
            note_data = Notes(title=title, description=description, color=color,image=image, is_archive=is_archive,
                             is_pinned=is_pinned,user_id=current_user.id,
                             remainder=remainder)
            note_data.save_to_db()
            response['message'] = 'note added'
            response['success'] = True
            response['data'] = {'title': title, 'description': description, 'color': color, 'is_archive': is_archive,
                                'is:pinned': is_pinned, 'remainder': remainder
                                }
        else:
            response['message'] = 'title and description mandatory'
            response['success'] = False
            raise Exception('title and description are mandatory')
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
        print(e)
    return response


@app.route('/get', methods=['POST', 'GET'])
def get_note():
    """ this method is used to get all notes of current user"""
    response = {
        'success': False,
        'message': 'something went wrong',
        'data': []
    }
    note_get = Notes.find_user_id(current_user.id)
    print('notes', note_get)
    response['success']=True
    response['message']='NOTES'
    print(note_get)
    return response


@app.route('/update/<int:id>', methods=['POST','GET'])
def updation(id):
    response = {
        'success': False,
        'message': 'something went wrong',
        'data': []
    }
    title = request.form.get('title')
    description = request.form.get('description')
    mynote = Note(title=title, description=description)
    update_status = mynote.updateTitleDescription(id)
    if update_status is True:
        response['message'] = 'note updated'
        response['success'] = True
    else:
        response['message'] = 'title or description cant be empty'
        response['success'] = True
    return response


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def deletion(id):
    response = {
        'success': False,
        'message': 'something went wrong',
        'data': []
    }
    delete_obj = Note()
    delete_obj.delete(id)
    delete_note = Notes.query.get(id)
    print(delete_obj)
    if delete_obj is True:
        response['message'] = 'note is deleted'
        response['success'] = True
    else:
        response['message'] ='error'
    return response


@app.route('/pin_unpin/<int:id>', methods=['POST', 'GET'])
def pin(id):
    """ this method is used to pin or unpin the note"""
    response = {
        'success': False,
        'message': 'something went wrong',
        'data': []
    }
    note = Notes.query.get(id)
    if note.is_pinned is True:
        note.is_pinned = False
    else:
        note.is_pinned = True
    Notes.update(self)
    response['success'] = True
    response['message'] = 'note is pinned'
    return response


@app.route('/upload', methods=['POST','GET'])
def s3_upload():
    """ this method is used to upload profile pic in s3 bucket and store the image url in db"""
    response = {
        'success': False,
        'message': 'something went wrong'
    }
    try:
        image = request.files.get('image')  # getting image from user
        image_file = imghdr.what(image)     # validating file
        if image_file is None:
            raise Exception('FILE MUST BE IMAGE')
        else:
            user_name = current_user.email_id      # getting the current user email_id so to store the file in that name
            status = upload_to_s3(image, user_name)    # calling the method to upload in s3 server
            get_user = current_user.id        # getting current user id
            get_user_data = sign_up.query.get(get_user)    # query the user in db
            get_user_data.profile_pic = status          # getting the url
            db.session.commit()                        # updating in db
            if status is not None:
                response['success'] = True
                response['message'] = 'image has uploaded'
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
    return response


@app.route('/addlabel/<int:id>', methods=['POST', 'GET'])
def label(id):
    """ this method is used to add the label """
    response = {
        'success': False,
        'message': 'something went wrong'
    }
    try:
        label = request.form.get('label')   # getting label from user
        print(label, '-----------------')
        if label:
            data = Label(label=label, user_id=current_user.id)   # saving data
            data.save_to_label()
            note = Notes.query.get(id)  # getting  note
            data.labels.append(note)    # adding data to label field
            data.save_to_label()      # saving the data
            response['success'] = True
            response['message'] = 'LABEL ADDED'
        else:
            raise Exception('label should not be empty')

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
    return response


@app.route('/getlabel/<int:id>',  methods=['POST', 'GET'])
def get_label(id):
    data = Label.query.filter_by(user_id=str(current_user.id))
    for label in data:
        for nt in label.labels:
            if nt.id == id:
                print(label.label, '----->>>')
    return label.label

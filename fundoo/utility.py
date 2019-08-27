from flask_mail import Message
from flask import url_for
from app import mail


def send_link_email(user):
    """ this method is used to activate the account
    :param: user email_id """
    token = user.get_reset_token()
    msg = Message('Activation link',
                  sender='laxmanraikar777@gmail.com',
                  recipients=[user.email_id])
    msg.body = f'''To activate the your account, visit the following link:
    {url_for('activation', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)  # here sending the message


def send_reset_email(user):
    """ this method is used to send mail to reset the password
    :param:user email_id """
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='laxmanraikar777@gmail.com',
                  recipients=[user.email_id])
    msg.body = f'''To activate the your account, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)
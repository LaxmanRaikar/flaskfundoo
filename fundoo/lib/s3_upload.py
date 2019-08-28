import boto3


def upload_to_s3(image, user_name):
    """ this method is used to upload the file in s3 server
        :return-file path
    """
    if image and user_name:
        s3 = boto3.client('s3') # calling the server
        s3.upload_fileobj(image, 'fundooapp777', str(user_name))    # sending the object
        url = '{}/{}/{}'.format(s3.meta.endpoint_url, 'fundooapp777', user_name)  # getting the file path
        return url

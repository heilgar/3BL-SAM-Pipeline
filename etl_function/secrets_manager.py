import os
import boto3
import json
from botocore.exceptions import ClientError


def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            raise ValueError("Secret not found in expected format")


def get_urlbox_credentials():
    secret_name = os.environ['URL_BOX_SECRET_NAME']
    secret = get_secret(secret_name)
    return secret['api_key'], secret['api_secret']


def get_db_credentials():
    secret_name = os.environ['DB_SECRET_NAME']
    db_creds = get_secret(secret_name)
    return {
        'username': db_creds['username'],
        'password': db_creds['password'],
        'host': os.environ['DB_HOST'],
        'dbname': os.environ['DB_NAME']
    }

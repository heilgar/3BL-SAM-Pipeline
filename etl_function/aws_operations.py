import boto3
import json
import os
from datetime import datetime

s3 = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET_NAME']

def is_debug_mode():
    return os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

def write_locally(content, filename):
    os.makedirs('debug_output', exist_ok=True)
    filepath = os.path.join('debug_output', filename)

    if isinstance(content, str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    elif isinstance(content, bytes):
        with open(filepath, 'wb') as f:
            f.write(content)
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)

    print(f"Debug: File written locally to {filepath}")

def upload_json(json_data, s3_key):
    if is_debug_mode():
        filename = os.path.basename(s3_key)  # Extract filename from s3_key
        write_locally(json_data, filename)
    else:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(json_data),
            ContentType='application/json'
        )

def upload_file(content, s3_key):
    if is_debug_mode():
        filename = os.path.basename(s3_key)  # Extract filename from s3_key
        write_locally(content, filename)
    else:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=content,
            ContentType='image/png'
        )

def read_max_date():
    if is_debug_mode():
        try:
            with open('debug_output/max_date.json', 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['max_date'])
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None
    else:
        try:
            response = s3.get_object(Bucket=S3_BUCKET, Key='max_date.json')
            data = json.loads(response['Body'].read().decode('utf-8'))
            return datetime.fromisoformat(data['max_date'])
        except s3.exceptions.NoSuchKey:
            return None

def write_max_date(max_date):
    data = {'max_date': max_date.isoformat()}
    if is_debug_mode():
        os.makedirs('debug_output', exist_ok=True)
        with open('debug_output/max_date.json', 'w') as f:
            json.dump(data, f)
    else:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key='max_date.json',
            Body=json.dumps(data),
            ContentType='application/json'
        )

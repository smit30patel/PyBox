import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY")
)

def upload_to_r2(file_stream, s3_key):
    s3.upload_fileobj(file_stream, os.getenv("S3_BUCKET"), s3_key)

def generate_download_url(s3_key, expiry=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={"Bucket": os.getenv("S3_BUCKET"), "Key": s3_key},
        ExpiresIn=expiry
    )

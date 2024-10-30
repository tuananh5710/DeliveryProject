import boto3
import base64
import imghdr
import io
import json
import traceback
from dependency_injector import containers, providers
import os


class S3Service:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def get_object(self, bucket: str, key: str):
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read()
            return json.loads(data)
        except Exception as e:
            print("Exception in get_object:", e)
            return None

    def upload_base64_file(self, bucket_name, base64_file, path_name, file_name):
        file, _file_name = self.decode_base64_file(base64_file, file_name)
        key_name = f"{path_name}/{file_name}"
        self.s3_client.upload_fileobj(file, bucket_name, key_name)
        url = f"https://{bucket_name}.s3-ap-southeast-1.amazonaws.com/{key_name}"
        return url

    def decode_base64_file(self, data, file_name):
        if isinstance(data, str) and 'data:' in data and ';base64,' in data:
            header, data = data.split(';base64,')
        decoded_file = base64.b64decode(data) if isinstance(data, str) else b''
        file_extension = self.get_file_extension(file_name, decoded_file)
        file_name = f"{file_name}.{file_extension}"
        return io.BytesIO(decoded_file), file_name

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        return "jpg" if extension == "jpeg" else extension

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    session = providers.Resource(
        boto3.Session,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )

    s3_client = providers.Resource(
        providers.MethodCaller(session.provided.client, service_name='s3')
    )

    s3_service = providers.Factory(S3Service, s3_client=s3_client)

def get_s3_service():
    container_s3 = Container()
    container_s3.config.aws_access_key_id.override(os.getenv("AWS_ACCESS_KEY_ID"))
    container_s3.config.aws_secret_access_key.override(os.getenv("AWS_SECRET_ACCESS_KEY"))
    container_s3.init_resources()
    return container_s3.s3_service()

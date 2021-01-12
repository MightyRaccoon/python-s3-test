import logging
import uuid
import configparser
import os
import random

import boto3

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(message)s",
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level='INFO'
)


def main():
    logger.info('Start')

    logger.info('Read S3 credentials')
    config = configparser.ConfigParser()
    config.read('s3_credentials.ini')

    logger.info('Create S3 client')
    s3 = boto3.client(
        's3',
        region_name="fakes3",
        use_ssl=False,
        aws_access_key_id=config['DEFAULT']['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['DEFAULT']['AWS_SECRET_ACCESS_KEY'],
        endpoint_url="http://172.17.0.1:8000"
    )

    logger.info('Create bucket')
    bucket_name = str(uuid.uuid4())
    s3.create_bucket(Bucket=bucket_name)

    logger.info('Check that bucket created')
    for bucket in s3.list_buckets()['Buckets']:
        logger.info(bucket['Name'])

    logger.info('Let\'s add put some pict to S3')
    pics_dir = 'data'
    for pic in os.listdir(pics_dir):
        pic_path = '/'.join([pics_dir, pic])
        with open(pic_path, 'rb') as f:
            logger.info('Upload %s to S3', pic_path)
            s3.upload_fileobj(Fileobj=f, Bucket=bucket_name, Key=pic)

    logger.info('Let\'s download pics from S3')
    abs_path = os.path.abspath(os.getcwd())
    path_1 = '/'.join([abs_path,'data_download_1'])
    os.mkdir(path_1)
    s3_object = s3.list_objects(Bucket=bucket_name)
    for s3_object_content in s3_object['Contents']:
        object_key = s3_object_content['Key']
        logger.info('Download %s', object_key)
        with open('/'.join([path_1, object_key]), 'wb') as f:
            s3.download_fileobj(Bucket=bucket_name, Key=object_key, Fileobj=f)

    logger.info('Let\'s do the same but before it delete 1 object')
    index = int(random.random() * 10) % 3
    keys = list(map(lambda obj: obj['Key'], s3_object['Contents']))
    key_for_delete = keys[index]
    logger.info('Delete object with key %s', key_for_delete)
    respone = s3.delete_object(Bucket=bucket_name, Key=key_for_delete)
    logger.info(respone)

    path_2 = '/'.join([abs_path,'data_download_2'])
    os.mkdir(path_2)
    s3_object = s3.list_objects(Bucket=bucket_name)
    for s3_object_content in s3_object['Contents']:
        object_key = s3_object_content['Key']
        logger.info('Download %s', object_key)
        with open('/'.join([path_2, object_key]), 'wb') as f:
            s3.download_fileobj(Bucket=bucket_name, Key=object_key, Fileobj=f)

    print('Is pics count the same: %b', len(os.listdir(path_2)) == len(os.listdir(path_1)))


if __name__ == '__main__':
    main()

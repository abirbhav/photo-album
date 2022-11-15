import json
import boto3
import logging
import requests
import os


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def detect_labels(bucket_name, img_name):
    logger.info(f'Detecting labels for bucket: {bucket_name} and img: {img_name}')
    rekognition = boto3.client('rekognition')
    response = rekognition.detect_labels(
    Image={
        'S3Object': {
            'Bucket': bucket_name,
            'Name': img_name
        }
    }
    )
    logger.info(f'Response from rekognition: {response}')
    labels = []
    labalesArr = response['Labels']
    for labelObj in labalesArr:
        labels.append(labelObj['Name'])
    return labels

def gets3MetaData(bucket_name, img_name):
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=bucket_name, Key=img_name)
    logger.info(f'Response from s3: {response}')
    httpHeadersObj = response['ResponseMetadata']['HTTPHeaders']
    cutomLabelsMeta = []
    if 'x-amz-meta-customLabels' in httpHeadersObj:
        #TODO Test this
        cutomLabelsMeta = httpHeadersObj['x-amz-meta-customLabels'].split(",")
    return cutomLabelsMeta
    
def createJson(bucket_name, img_name, labels, time_stamp):
    return {
        "objectKey": img_name,
        "bucket": bucket_name,
        "createdTimestamp": time_stamp,
        "labels": [label.lower() for label in labels]
    }
    
def upload_to_opensearch(jsonObj):
    logger.debug(f'Entering opensearch ')
    
    OPEN_SEARCH_URL = os.environ['OPEN_SEARCH_URL']
    OPEN_SEARCH_INDEX = os.environ['OPEN_SEARCH_INDEX']
    OPEN_SEARCH_USERNAME = os.environ['OPEN_SEARCH_USERNAME']
    OPEN_SEARCH_PASSWORD = os.environ['OPEN_SEARCH_PASSWORD']
    
    url = OPEN_SEARCH_URL + '/' + OPEN_SEARCH_INDEX + '/_doc/1/'
    
    response = requests.post(url, auth=(OPEN_SEARCH_USERNAME, OPEN_SEARCH_PASSWORD), json = jsonObj)
    logger.info(f'Response from opensearch: {response.text}')
    
def lambda_handler(event, context):
    logger.info(f'event is {event}')
    record = event['Records'][0]
    
    bucket_name = record['s3']['bucket']['name']
    img_name = record['s3']['object']['key']
    event_time = record['eventTime']
    
    labels_rekognition = detect_labels(bucket_name, img_name)
    logger.info(f'labels extracted are: {labels_rekognition}')
    
    labels_s3 = gets3MetaData(bucket_name, img_name)
    
    jsonObj = createJson(bucket_name, img_name, labels_rekognition + labels_s3, event_time)
    print(f'jsonObj is {jsonObj}')
    upload_to_opensearch(jsonObj)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

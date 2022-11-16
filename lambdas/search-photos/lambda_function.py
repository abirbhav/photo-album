import json
import logging
import os
import boto3
import requests
import inflect

p = inflect.engine()


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


BOT_NAME = os.environ['BOT_NAME']
BOT_ALIAS = os.environ['BOT_ALIAS']
USER_ID = os.environ['USER_ID']
OPEN_SEARCH_URL = os.environ['OPEN_SEARCH_URL']
OPEN_SEARCH_INDEX = os.environ['OPEN_SEARCH_INDEX']
OPEN_SEARCH_USERNAME = os.environ['OPEN_SEARCH_USERNAME']
OPEN_SEARCH_PASSWORD = os.environ['OPEN_SEARCH_PASSWORD']

def disambiguate(search_query):
    logger.info(f'search query is {search_query}')
    lex = boto3.client('lex-runtime')
    
    # sending request to lex
    response = lex.post_text(
        botName = BOT_NAME,
        botAlias = BOT_ALIAS,
        userId = USER_ID,
        inputText = search_query)
    logger.info(f'response from lex is {response}')
    slots = []
    if 'slots' in response:
        if 'slotOne' in response['slots'] and response['slots']['slotOne'] is not None:
            slots.append(response['slots']['slotOne'])
        if 'slotTwo' in response['slots'] and response['slots']['slotTwo'] is not None:
            slots.append(response['slots']['slotTwo'])
    
    return slots

def handlePlurals(slots):
    for i in range(len(slots)):
        try:
            slots[i] = (p.singular_noun(slots[i])).lower()
        except Exception:
            pass
    
def search_in_open_search(slots):
    photos = []
    #In this case, since there are multiple keywords
    #We will use boolean query to combine queries
    search_query = {
        "query": {
            "bool": {
                "should": [{"match": {"labels": s}} for s in slots],
                "minimum_should_match": 1
            }
        }
    }
    
    logger.info(f'Open search request = {search_query}')
    
    url = OPEN_SEARCH_URL + '/' + OPEN_SEARCH_INDEX + '/_search/'
    
    search_response = requests.get(url, auth = (OPEN_SEARCH_USERNAME, OPEN_SEARCH_PASSWORD), json = search_query)
    
    logger.info(f'Open search url = {url}, request = {search_query} and response = {search_response.text}')

    open_search_data = {}
    open_search_data = json.loads(search_response.content.decode('utf-8'))['hits']['hits']
    
    
    for data in open_search_data:
        photo_name = data["_source"]["objectKey"]
        bucket_name = data["_source"]["bucket"]
        photos.append(f'https://{bucket_name}.s3.amazonaws.com/{photo_name}')
      
    return photos
    
    
def lambda_handler(event, context):
    logger.info(f'event is {event}')
    
    query_string = event['queryStringParameters']['q']
    logger.info(f'query string is {query_string}')
    
 
    #Step 1: Disambiguate the query
    slots = disambiguate(query_string)
    
    #Step 2: Handle plurals
    handlePlurals(slots)
    
    #Step 3: Search keywords in elastic search
    photos = search_in_open_search(slots) if len(slots) > 0 else []
    
    #Step 4: Return
    #print(photos)
    #photos = ['https://b2cloudbucket.s3.amazonaws.com/person.jpeg']
   
    

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(photos)
        }
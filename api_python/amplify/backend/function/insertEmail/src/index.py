import os
import boto3
import uuid
import json
import hashlib
from boto3.dynamodb.conditions import Key
from http import HTTPStatus

def handler(event, context):
  response = {
      'statusCode': HTTPStatus.OK,
      'body': ''
    }
  
  try:
    try:
      body = json.loads(event['body'])
    except:
      body = event['body']
    
    email = body.get('email')
    if not email:
      response['statusCode'] = HTTPStatus.BAD_REQUEST
      response['body'] = 'Email is required'
      return response
    
    user_table_name = os.environ.get('STORAGE_USERS_NAME')
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    table = dynamodb.Table(user_table_name)

    print(f"Querying for email: {email}")
    res = table.query(
      IndexName='emails',
      KeyConditionExpression=Key('email').eq(email)
    )

    user_items = res.get('Items')
    print(f"Query result: {user_items}")

    if not user_items:
      user_id = str(uuid.uuid4())
      token_input = f"{user_id}{email}"
      token = hashlib.sha256(token_input.encode()).hexdigest()
      new_user = {
        'id': user_id,
        'email': email,
        'token': token
      }
      table.put_item(Item=new_user)
      response['statusCode'] = HTTPStatus.CREATED
      response['body'] = json.dumps({'token': new_user['token']})
    else:
      if not user_items[0].get('token'):
        user_id = user_items[0]['id']
        token_input = f"{user_id}{email}"
        token = hashlib.sha256(token_input.encode()).hexdigest()
        table.update_item(
          Key={'id': user_id},
          UpdateExpression='SET #t = :t',
          ExpressionAttributeNames={'#t': 'token'},
          ExpressionAttributeValues={':t': token}
        )
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps({'token': token})
      else:
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps({'token': user_items[0]['token']})

    print(f"Response: {response}")
    return response

  except Exception as e:
    print(f"Error: {str(e)}")
    response['statusCode'] = HTTPStatus.INTERNAL_SERVER_ERROR
    response['body'] = str(e)
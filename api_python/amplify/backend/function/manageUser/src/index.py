import os
import boto3
from requests import HTTPError
from http import HTTPStatus
from functools import wraps
from boto3.dynamodb.conditions import Key, Attr

def exception_handler(func):
	@wraps(func)
	def wrapper(event,context):
		print(event['headers'])
		response = {}
		try: 
			if not event['headers'].get('user_token'):
				raise PermissionError('Invalid API key')
			
			res = func(event, context)
			if res:
				response['body'] = res
			response['statusCode'] = HTTPStatus.OK
		except HTTPError as error:
			response['statusCode'] = error.response.status_code
		except PermissionError as error:
			response['body'] = str(error)
			response['statusCode'] = HTTPStatus.FORBIDDEN
		except Exception as error:
			response['body'] = str(error)
			response['statusCode'] = HTTPStatus.INTERNAL_SERVER_ERROR
		return response
	return wrapper


@exception_handler
def handler(event, context):
	user_table_name = os.environ.get('STORAGE_USERS_NAME')
	dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
	table = dynamodb.Table(user_table_name)

	user_token = event['headers'].get('user_token')
	if not user_token:
		raise ValueError('User ID is required')

	res = table.scan(
		FilterExpression=Attr('token').eq(user_token)
	)
	data = res['Items']
	
	if not data:
		raise ValueError('User not found')
  
	user_data = data[0]
	
	return user_data['email']

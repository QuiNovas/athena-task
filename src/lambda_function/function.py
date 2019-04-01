import boto3
import logging.config
import os

from pyathena import connect
from pyathena.async_cursor import AsyncCursor

connection = connect(cursor_class=AsyncCursor,
				 region_name=os.environ.get('AWS_ATHENA_REGION_NAME', boto3.session.Session().region_name),
				 s3_staging_dir=os.environ['AWS_ATHENA_S3_STAGING_DIR'],
				 schema_name=os.environ.get('AWS_ATHENA_SCHEMA_NAME', 'default'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
max_concurrent_queries = int(os.environ.get('MAX_CONCURRENT_QUERIES', 5))


def handler(event, context):
	try:
		logger.info('Event :{}'.format(event))
		if type(event) is dict:
			with connection.cursor(max_workers=1) as cursor:
				query_id, future = cursor.execute(event['query'], event.get('params'))
				result_set = future.result()
				response = process_result(result_set, event.get('single_result', False))
		else:
			response = []
			max_workers = min(len(event), max_concurrent_queries)
			with connection.cursor(max_workers=max_workers) as cursor:
				futures = []
				for item in event:
					futures.append(cursor.execute(item['query'], item.get('params'))[1])
				for count in range(0, len(futures)):
					response.append(process_result(futures[count].result(), False))
		return response
	except Exception as error:
		logger.info('Error : {}'.format(error))
		return error

		
def process_result(result_set, single_result):
	results = []
	description = result_set.description
	for row in result_set:
		if single_result and len(results) == 1:
			logger.info('Expected single row but returned more than one row in results for the query : {}'.format(result_set.query))
		results.append(map_result(description, row))
	return results if not single_result else results[0] if len(results) else {}

	
def map_result(description, row):
    result = {}
    for column in range(0, len(description)):
        result[description[column][0]] = row[column]
    return result
	
	

		


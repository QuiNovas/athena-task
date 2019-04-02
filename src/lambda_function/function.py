import boto3
import logging.config
import os

from pyathena import connect

POLL_INTERVAL = float(os.environ.get('POLL_INTERVAL', 1.0))
REGION_NAME = os.environ.get('AWS_ATHENA_REGION_NAME', boto3.session.Session().region_name)
S3_STAGING_DIR = os.environ['AWS_ATHENA_S3_STAGING_DIR']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
	logger.info('Event :{}'.format(event))
	with _connect(event).cursor() as cursor:
		return _process_results(
			cursor.execute(event['Operation'], event.get('Parameters')), 
			event.get('SingleResult', True)
		)

def _connect(event):
	return connect(
		encryption_option=event.get('EncryptionOption'),
		kms_key=event.get('KmsKey'),
		poll_interval=POLL_INTERVAL,
		region_name=REGION_NAME,
		s3_staging_dir=S3_STAGING_DIR,
		schema_name=event.get('SchemaName', 'default'),
		work_group=event.get('WorkGroup')
	)
		
def _process_results(cursor, single_result):
	results = []
	description = cursor.description
	for row in cursor:
		if single_result and len(results) == 1:
			logger.info('Expected single row but returned more than one row in results for the query : {}'.format(cursor.query))
		results.append(_map_result(description, row))
	return results if not single_result else results[0] if results else {}
	
def _map_result(description, row):
    result = {}
    for column in range(0, len(description)):
        result[description[column][0]] = row[column]
    return result

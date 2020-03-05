from athena_type_converter import convert_result_set, TYPE_CONVERTERS
from backoff import on_predicate, fibo
from base64 import b64encode
from boto3 import client
from json import dumps as jsondumps
from logging import getLogger, INFO
from os import environ


getLogger().setLevel(INFO)
__ATHENA = client('athena')
__DATABASE = environ.get('DATABASE', 'default')
__WORKGROUP = environ.get('WORKGROUP', 'primary')
__timestamp = TYPE_CONVERTERS['timestamp']
TYPE_CONVERTERS['timestamp'] = lambda x: __timestamp(x).isoformat()
__date = TYPE_CONVERTERS['date']
TYPE_CONVERTERS['date'] = lambda x: __date(x).isoformat()
__time = TYPE_CONVERTERS['time']
TYPE_CONVERTERS['time'] = lambda x: __time(x).isoformat()
__varbinary = TYPE_CONVERTERS['varbinary']
TYPE_CONVERTERS['varbinary'] = lambda x: b64encode(__varbinary(x))
TYPE_CONVERTERS['decimal'] = lambda x: float(x) if x else None


def handler(event, context):
	getLogger().info('Processing event {}'.format(jsondumps(event)))
	query_execution_id = __ATHENA.start_query_execution(
		QueryString=__format_operation(event['Operation'], event.get('Parameters', {})),
		QueryExecutionContext={
			'Database': event.get('Database', __DATABASE)
		},
		WorkGroup=event.get('WorkGroup', __WORKGROUP)
	)
	query_status = __poll_query_status(query_execution_id)
	if query_status != 'SUCCEEDED':
			if query_status in ('FAILED', 'CANCELLED'):
					raise Exception('Operation execution failed with status {}'.format(query_status))
			else:
					raise Exception('Operation timed out with status {}'.format(query_status))
	results = __get_results(query_execution_id)
	return results if not event.get('SingleResult', True) else results[0] if len(results) else {}


def __format_operation(operation, parameters):
	result = ' '.join(operation) \
		if isinstance(operation, (list, tuple)) \
			else operation
	result = result.format(**parameters)
	getLogger().debug('Operation: {}'.format(result))
	return result


@on_predicate(fibo, lambda x: x not in ('SUCCEEDED', 'FAILED', 'CANCELLED'), max_time=899)
def __poll_query_status(query_execution_id):
    response = __ATHENA.get_query_execution(
        QueryExecutionId=query_execution_id
    )
    return response['QueryExecution']['Status']['State']


def __get_results(query_execution_id, next_token=None):
    params = {
        'QueryExecutionId': query_execution_id,
        'MaxResults': 1000
    }
    if next_token:
        params['NextToken'] = next_token
    response = __ATHENA.get_query_results(**params)
    results = convert_result_set(response['ResultSet'])
    return results if 'NextToken' not in response else results + __get_results(query_execution_id, response['NextToken'])

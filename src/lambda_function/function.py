from backoff import on_predicate, fibo
from binascii import a2b_hex
from boto3 import client
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from decimal import Decimal
from distutils.util import strtobool
from json import dumps as jsondumps, loads as jsonloads
from logging import getLogger, INFO
from os import environ


getLogger().setLevel(INFO)
__ATHENA = client('athena')
__ATHENA_TYPE_CONVERTERS = {
    'boolean': lambda x: bool(strtobool(x)) if x else None,
    'tinyint': lambda x: int(x) if x else None,
    'smallint': lambda x: int(x) if x else None,
    'integer': lambda x: int(x) if x else None,
    'bigint': lambda x: int(x) if x else None,
    'float': lambda x: float(x) if x else None,
    'real': lambda x: float(x) if x else None,
    'double': lambda x: float(x) if x else None,
    'char': lambda x: x,
    'varchar': lambda x: x,
    'string': lambda x: x,
    'timestamp': lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').isoformat() if x else None,
    'date': lambda x: datetime.strptime(x, '%Y-%m-%d').date().isoformat() if x else None,
    'time': lambda x: datetime.strptime(x, '%H:%M:%S.%f').time().isoformat() if x else None,
    'varbinary': lambda x: a2b_hex(''.join(x.split(' '))) if x else None,
    'array': lambda x: x,
    'map': lambda x: x,
    'row': lambda x: x,
    'decimal': lambda x: Decimal(x) if x else None,
    'json': lambda x: jsonloads(x) if x else None,
}
__DATABASE = environ.get('DATABASE', 'default')
__WORKGROUP = environ.get('WORKGROUP', 'primary')


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


def __map_meta_data(meta_data):
    mapped_meta_data = []
    for column in meta_data:
        mapped_meta_data.append((column['Name'], __ATHENA_TYPE_CONVERTERS[column['Type']]))
    return mapped_meta_data


def __map_result(meta_data, data):
    result = {}
    for n in range(len(data)):
        result[meta_data[n][0]] = meta_data[n][1](data[n].get('VarCharValue', None))
    return result


def __get_results(query_execution_id, next_token=None):
    params = {
        'QueryExecutionId': query_execution_id,
        'MaxResults': 1000
    }
    if next_token:
        params['NextToken'] = next_token
    response = __ATHENA.get_query_results(**params)
    meta_data = __map_meta_data(response['ResultSet']['ResultSetMetadata']['ColumnInfo'])
    results = []
    rows = response['ResultSet']['Rows']
    for n in range(1, len(rows)):
        results.append(__map_result(meta_data, rows[n]['Data']))
    return results if 'NextToken' not in response else results + __get_results(query_execution_id, response['NextToken'])

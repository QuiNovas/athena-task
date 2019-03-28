# athena-task
This is a generic Lambda function that can execute athena queries. This function will take the input information, call Athena, and respond to StepFunctions with the results of the SQL call.

# Environment Variables:
- **AWS_ATHENA_REGION_NAME** OPTIONAL - The AWS region for Athena that this function should use. Defaults to the region that the function is executing in.
- **AWS_ATHENA_S3_STAGING_DIR** REQUIRED - This is the S3 location that Athena will store the query results in. It must be in the format `s3://YOUR_S3_BUCKET/path/to/`.
- **AWS_ATHENA_SCHEMA_NAME** OPTIONAL - The schema/database name that you wish to query. Defaults to the _default_ schema/database.
- **MAX_CONCURRENT_QUERIES** OPTIONAL - The maximum number of concurrent queries to run in Athena. Defaults to `5`.
- **POLL_INTERVAL** OPTIONAL - The rate at which to poll Athena for a response, in seconds. Defaults to `1.0`.

# AWS Permissions Required:
You will need Athena and Glue (if you create your schema with Glue) permissions:
```
"athena:StopQueryExecution",
"athena:StartQueryExecution",
"athena:RunQuery",
"athena:ListQueryExecutions",
"athena:GetTables",
"athena:GetTable",
"athena:GetQueryResultsStream",
"athena:GetQueryResults",
"athena:GetQueryExecutions",
"athena:GetQueryExecution",
"athena:GetNamespaces",
"athena:GetNamespace",
"athena:GetExecutionEngines",
"athena:GetExecutionEngine",
"athena:GetCatalogs",
"athena:CancelQueryExecution",
"athena:BatchGetQueryExecution",
"glue:GetTable",
"glue:GetPartitions"
```
You will also require read access to the underlying Athena datasource, read and write access to the Athena result S3 bucket, and access to any KMS keys used in either of those.

# Handler Method
function.handler

# Request syntax
```
{
    "query": "string",
    "params": map | list(map),
    "single_result": boolean (OPTIONAL - defaults to false)
}
```
- **query** _(string)_ -- **[REQUIRED]**
 This is the query string to be executed. It may be parameterized with `PyFormat`, only supporting [named placeholders](https://pyformat.info/#named_placeholders) with the old `%` operator style. If `%` character is contained in your query, it must be escaped with `%%`. 
- **params** _(map)_ | _(list(map))_ -- **[REQUIRED]** 
 If your _query_ is parameterized. In the case of a multiple queries, this will be a `list` of `maps`.
- - **single_result** _(boolean)_ -- 
 Defaults to false. True for a single result

 
# Lambda package location
https://s3.amazonaws.com/lambdalambdalambda-repo/quinovas/athena-task/athena-task-0.0.1.zip



athena-task
===========

.. _APL2: http://www.apache.org/licenses/LICENSE-2.0.txt
.. _named placeholders: https://pyformat.info/#named_placeholders
.. _AWS StepFunctions: https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
.. _AWS Athena: https://docs.aws.amazon.com/athena/latest/ug/what-is.html
.. _PyFormat: https://pyformat.info/

This is a generic Lambda task function that can execute athena queries. It
is intended to be used in `AWS StepFunctions`_.
This function will take the input information, call `AWS Athena`_, and respond
to StepFunctions with the results of the SQL call.

Environment Variables
---------------------
**AWS_ATHENA_REGION_NAME**: OPTIONAL
  The AWS region for Athena that this function should use. Defaults to the
  region that the function is executing in.
**AWS_ATHENA_S3_STAGING_DIR**: REQUIRED
  This is the S3 location that `AWS Athena`_ will store the query results in.
  It must be in the format `s3://YOUR_S3_BUCKET/path/to/`.
**POLL_INTERVAL**: OPTIONAL
  The rate at which to poll `AWS Athena`_ for a response, in seconds. Defaults
  to `1.0`.

AWS Permissions Required
------------------------
- athena:StopQueryExecution
- athena:StartQueryExecution
- athena:RunQuery
- athena:ListQueryExecutions
- athena:GetTables
- athena:GetTable
- athena:GetQueryResultsStream
- athena:GetQueryResults
- athena:GetQueryExecutions
- athena:GetQueryExecution
- athena:GetNamespaces
- athena:GetNamespace
- athena:GetExecutionEngines
- athena:GetExecutionEngine
- athena:GetCatalogs
- athena:CancelQueryExecution
- athena:BatchGetQueryExecution
- glue:GetTable
- glue:GetPartitions

You will also require read access to the underlying `AWS Athena`_ datasource,
read and write access to the Athena result S3 bucket, and access to any KMS
keys used in either of those.

Handler Method
--------------
.. code::

  function.handler

Request Syntax
--------------
.. code-block:: JSON

  {
    "Operation": "string",
    "SchemaName": "string",
    "Parameters": {},
    "SingleResult": boolean,
    "EncryptionOption": "string",
    "KmsKey": "string",
    "WorkGroup": "string"
  }

**Operation**: REQUIRED
  This is the query string to be executed. It may be parameterized with
  `PyFormat`_, only supporting `named placeholders`_ with the old `%` operator
  style. If `%` character is contained in your query, it must be escaped
  with `%%`.
**SchemaName**: OPTIONAL
  This is the `AWS Athena`_ schema to run the `Operation` against. Defaults to
  `default`.
**Parameters**: OPTIONAL
  Required if your `Operation` is parameterized.
**SingleResult**: OPTIONAL
  Defaults to `true`. Set to `false` to allow a multiple results. If
  set to `true` and `Operation` returns multiple results, an error
  will be thrown.
**EncryptionOption**: OPTIONAL
  If set, must be one of `SSE_S3 | SSE_KMS | CSE_KMS`.
**KmsKey**: OPTIONAL
  Required if `EncryptionOption` is `SSE_KMS | CSE_KMS`. This is the KMS key
  ARN or ID.
**WorkGroup**: OPTIONAL
  The name of the workgroup in which the query is being started. If not present
  the default workgroup will be used.

Lambda Package Location
-----------------------
https://s3.amazonaws.com/lambdalambdalambda-repo/quinovas/athena-task/athena-task-0.0.1.zip

License: `APL2`_

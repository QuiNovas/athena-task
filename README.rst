athena-task
===========

.. _APL2: http://www.apache.org/licenses/LICENSE-2.0.txt
.. _named placeholders: https://pyformat.info/#named_placeholders
.. _AWS StepFunctions: https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
.. _AWS Athena: https://docs.aws.amazon.com/athena/latest/ug/what-is.html
.. _PyFormat: https://pyformat.info/

**VERSION 0.1.0 IS A BREAKING CHANGE FROM PREVIOUS VERSIONS.
PLEASE PAY PARTICULAR ATTENTION TO THE INFORMATION BELOW.**

This is a generic Lambda task function that can execute athena queries. It
is intended to be used in `AWS StepFunctions`_.
This function will take the input information, call `AWS Athena`_, and respond
to StepFunctions with the results of the SQL call.

Environment Variables
---------------------
:DATABASE: The `AWS Athena`_ Database to query.
  May be overridden in the ``query`` request. Defaults to ``default``
:WORKGROUP: The `AWS Athena`_ Workgroup to use during queries.
  May be overridden in the ``query`` request. Defaults to ``primary``.

AWS Permissions Required
------------------------
* **AmazonAthenaFullAccess** arn:aws:iam::aws:policy/AmazonAthenaFullAccess

You will also require read access to the underlying `AWS Athena`_ datasource
and access to any KMS keys used.

Handler Method
--------------
.. code::

  function.handler

Request Syntax
--------------
Request::

  {
    "Operation": "string" | ["string"],
    "Parameters": {},
    "Database": "string",
    "SingleResult": boolean,
    "WorkGroup": "string"
  }

**Operation**: REQUIRED
  This is the query string to be executed. It may be parameterized with
  `PyFormat`_, using the new format `{}` named placeholders method.
**Parameters**: OPTIONAL
  Required if your `Operation` is parameterized. The keys in this map should
  correspond to the format names in your operation string or array.
**Database**: OPTIONAL
  The schema/database name that you wish to query. Overrides
  **DATABASE** if present.
**SingleResult**: OPTIONAL
  Defaults to `true`. Set to `false` to allow a list of results.
**WorkGroup**: OPTIONAL
  The `AWS Athena`_ Workgroup to use during. Overrides
  **WORKGROUP** if present.

Response:

  If `SingleResult` is `true`::

    {
      "Key": Value,
      (Keys and values are generated from the query results.
      Keys are the column names, values are converted to their
      specified types.)
    }

  If `SingleResult` is `false`::

    [
      {
        "Key": Value,
        (Keys and values are generated from the query results.
        Keys are the column names, values are converted to their
        specified types.)
      }
    ]

Lambda Package Location
-----------------------
https://s3.amazonaws.com/lambdalambdalambda-repo/quinovas/athena-task/athena-task-0.1.0.zip

License: `APL2`_

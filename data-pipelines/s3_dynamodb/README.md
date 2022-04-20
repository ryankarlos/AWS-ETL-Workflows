# Copy data from S3 to dynamodb


<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/s3_to_dynamodb_workflow.png">


Zip the lambda function script and required modules into package by running the following commands

```
$ zip batch_write_dynamodb.zip lambda_function.py
  
  adding: lambda_function.py (deflated 54%)
   
$ zip batch_write_dynamodb.zip ddb_io.py

  adding: ddb_io.py (deflated 61%)
  
$ zip batch_write_dynamodb.zip schema.py 

  adding: schema.py (deflated 68%)
 
```

Create two lambda functions 'ddb_input_transform' and "batch_write_s3_dynamodb"  with the following configurations from console or cli

* "Timeout": 40,
* "MemorySize": 1024
* "Runtime": "python3.9",

```
 aws lambda create-function --function-name "${1}" --runtime python3.9 --zip-file fileb://<path-to-source-code-zip> \
    --role arn:aws:iam::376337229415:role/service-role/batch_write_s3_dynamodb-role-ms0y29fp \
    --timeout 40 --memory-size 1024 --handler lambda_function.lambda_handler
```

create role and modify with permissions for accessing S3 and dynamodb as in roles/batch_write_s3_dynamodb/
Note: for simplicity, Ive added all read options for S3 and all write options for dynamo but you could further limit this to adhere to least privilege principle.


if you update the source code, you will need to update the lambda function with new zip 

```
$ aws lambda update-function-code --function-name batch_write_s3_dynamodb --zip-file fileb://batch_write_dynamodb.zip


{
    "FunctionName": "batch_write_s3_dynamodb",
    "FunctionArn": "<arn>:function:batch_write_s3_dynamodb",
    "Runtime": "python3.9",
    "Role": "<arn>/batch_write_s3_dynamodb-role-ms0y29fp",
    "Handler": "lambda_function.lambda_handler",
    "CodeSize": 3057,
    "Description": "",
    "Timeout": 300,
    "MemorySize": 1024,
    "LastModified": "2022-04-19T03:25:33.000+0000",
    "CodeSha256": "1rZsGrHJCjLIYKOu+7sXlIyAV0MBO9F5ZeE447EieL4=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "da80b102-e870-439c-8d77-942a5d0e110f",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",
    "PackageType": "Zip"
}
```
### Running end to end with bash script


To run all the above and also put json object into S3 to trigger lambda function, run the 
bash script below with the params : raw data path, lambda function name, S3 bucket name, object key
e.g. 

```
$ chmod +x data-pipelines/s3_dynamodb/bash_scripts/update_lambda_and_trigger.sh
$ sh data-pipelines/s3_dynamodb/bash_scripts/update_lambda_and_trigger.sh \
datasets/moviedata.json \
batch_write_s3_dynamodb \
movies-data-json \
transformed/moviedata.json 
```

or without any params defaults to the param values above

```
$ sh data-pipelines/s3_dynamodb/bash_scripts/update_lambda_and_trigger.sh 

 Running s3 to dynamo batch write script
Zipping lambda package for ddb_input_transform
updating: __init__.py (stored 0%)
updating: lambda_function.py (deflated 44%)
updating: transform.py (deflated 59%)

Zipping lambda package for batch_write_s3_dynamodb
updating: __init__.py (stored 0%)
updating: ddb_io.py (deflated 57%)
updating: lambda_function.py (deflated 52%)
updating: schema.py (deflated 68%)

 ddb_input_transform function already exists so updating with zip source code 
{
    "FunctionName": "ddb_input_transform",
    "FunctionArn": "<arn>,
    "Runtime": "python3.9",
    "Role": "<arn-prefix>/batch_write_s3_dynamodb-role-ms0y29fp",
    "Handler": "lambda_function.lambda_handler",
    "CodeSize": 1366,
    "Description": "",
    "Timeout": 40,
    "MemorySize": 1024,
    "LastModified": "2022-04-20T16:28:46.000+0000",
    "CodeSha256": "OG5C4MsQ0QJAIJmx5WJr5VWXDM6B+6FdF2BP4g9WoQQ=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "4f10d7d1-a02c-4968-bc6a-a2028a22d32c",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",

 batch_write_s3_dynamodb function already exists so updating with zip source code 
{
    "FunctionName": "batch_write_s3_dynamodb",
    "FunctionArn": "<arn>",
    "Runtime": "python3.9",
    "Role": "<arn-prefix>/batch_write_s3_dynamodb-role-ms0y29fp",
    "Handler": "lambda_function.lambda_handler",
    "CodeSize": 2807,
    "Description": "",
    "Timeout": 300,
    "MemorySize": 1024,
    "LastModified": "2022-04-20T16:28:51.000+0000",
    "CodeSha256": "pK79sDp290GhQK9xj26bMQ1XxaUZc24HdkG7Urk2kSg=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "6ad57a6c-a456-4f74-b92b-4bb3615a0d78",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",

 put object in S3 to trigger lambda execution 
{
    "ETag": "\"d80d1246eb741b95bdef7e99fb4db5c6\""
}
```


## Cloudwatch Execution logs 
In the cloudwatch console you can see the lamda function execution logs

* /aws/lambda/ddb_input_transform log group

first Lambda function performs data transformations and triggered by raw data load into S3

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/ddb_lambda_function1_logs.png">

* /aws/lambda/batch_write_s3_dynamodb log group

Second lambda function triggered by S3 put event and batch writing data to DynamoDB and publish to SNS

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/ddb_lambda_function2_logs.png">

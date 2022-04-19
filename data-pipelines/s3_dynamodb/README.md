# Copy data from S3 to dynamodb


<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/s3_to_dynamodb.png">


Create a lambda function with the following configurations from console or cli

* "FunctionName": "batch_write_s3_dynamodb",
* "Timeout": 40,
* "MemorySize": 1024
* "Runtime": "python3.9",

create role and modify with permissions for accessing S3 and dynamodb as in roles/batch_write_s3_dynamodb/
Note: for simplicity, Ive added all read options for S3 and all write options for dynamo but you could further limit this to adhere to least privilege principle.

Zip the lambda function script and required modules into package by running the following commands

```
$ zip batch_write_dynamodb.zip lambda_function.py
  
  adding: lambda_function.py (deflated 54%)
   
$ zip batch_write_dynamodb.zip ddb_io.py

  adding: ddb_io.py (deflated 61%)
  
$ zip batch_write_dynamodb.zip schema.py 

  adding: schema.py (deflated 68%)
 
```

Update function with code 

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

To run both the above and also put json object into S3 to trigger lambda function, run the 
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
```

In the cloudwatch console you can see the lamda function execution logs 

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/cloudwatch_lambda_ddb1.png">
<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/cloudwatch_lambda_ddb2.png">

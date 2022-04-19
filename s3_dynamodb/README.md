# Copy data from S3 to dynamodb


<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/s3_to_dynamodb.png">


Zip the lambda function script and required modules into package


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

To run both the above and also trigger lambda but oput object into S3 run the 
bash script below

```
$ chmod +x bash_scripts/update_lambda_and_trigger.sh
$ sh bash_scripts/update_lambda_and_trigger.sh
```

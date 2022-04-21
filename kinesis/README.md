
# Streaming tweets using AWS kinesis data streams and firehose

<img width="1000" alt="kinesis_workflow" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/kinesis_workflow.png">

In this workflow, we will invoke lambda function created from container image with the twitter streaming application code built in https://github.com/ryankarlos/codepipeline to publish records into kinesis stream. Kinesis Firehose will acts as a consumer to read the records from shards, transform the records (including call AWS Comprehend api to retrieve sentiment results) and ingest them into S3 bucket. 


## Producer


if instructions in https://github.com/ryankarlos/codepipeline are followed, the Lamda function should already be avaiolable with the latest image attached.
If the source code is rebuilt again and published to ECR, the existing lambda function would need to be updated with the URI of the latest image tag

```
$ aws lambda update-function-code --function-name LambdaTwitter --image-uri <image-uri>
```

image tag would need to be updated in

## Kinesis stream and firehose

Creating new kinesis source stream and delivery stream. The script fetches the 
parameters based on the config settings in kinesis/config/firehose_description.json and 
kinesis/config/kinesis_stream.json. 

```
python kinesis/create_kinesis_streams.py 

Creating new stream kinesis-twitter-stream: 

{
    "ResponseMetadata": {
        "HTTPHeaders": {
            "content-length": "0",
            "content-type": "application/x-amz-json-1.1",
            "date": "Mon, 18 Apr 2022 05:38:38 GMT",
            "x-amz-id-2": "ov9VHw3LaG4YkdBWuaU/BHlo5uO65pxj8puuwHeNahxSzExgUy1vc7Q6RwEWjTDXIPiHiUIeAYFbmJ7elqQZum8qCfv9FuQL",
            "x-amzn-requestid": "dfd8012b-7173-b91c-850e-fab5dca7fad6"
        },
        "HTTPStatusCode": 200,
        "RequestId": "dfd8012b-7173-b91c-850e-fab5dca7fad6",
        "RetryAttempts": 0
    }
}

 Stream already exists so deleting...
creating new delivery stream Firehose-S3-twitter 

{
    "DeliveryStreamARN": "arn:aws:firehose:us-east-1:376337229415:deliverystream/Firehose-S3-twitter",
    "ResponseMetadata": {
        "HTTPHeaders": {
            "content-length": "98",
            "content-type": "application/x-amz-json-1.1",
            "date": "Mon, 18 Apr 2022 05:38:59 GMT",
            "x-amz-id-2": "2NspWGLk0GRGKQclQFDr+DWFQf9cuBeyd/wtWh06k5vA0KiP6EtR0PsJuFATjhavA/pqwwQZRVijZz14WNFAno3t87OyODy3",
            "x-amzn-requestid": "e496bebf-2344-a5f1-be40-450c3392504c"
        },
        "HTTPStatusCode": 200,
        "RequestId": "e496bebf-2344-a5f1-be40-450c3392504c",
        "RetryAttempts": 0
    }
}

```
Make sure configuration contain the right firehose role arn. 
To get existing roles and then get role-arn for role name

```
aws iam list-roles --query 'Roles[*].RoleName'
aws iam get-role --role-name <arn>
```

## Lambda transform function for firehose

we will create a lambda function to decode the binary data to text, retrieve sentiment and add as new key value for each record (via calls to Comprehend API), add a new line at the end of each data record (as by default firehose dumps the json records into S3 in one line) and then return a list of base64 encoded records.

The package that needs to be deployed is kinesis/transform-firehose and has the following structure.

```
transform-firehose$
| lambda_function.py
```

No additional dependencies need to be installed before deployment, so we can run the following command to add the python script to root of the zip package

```
$ zip transform-firehose.zip lambda_function.py
```
and then update the function with the zip file 

```
$ aws lambda update-function-code --function-name transform-firehose --zip-file fileb://transform-firehose.zip
```


Run entire pipeline end to end. The example below runs the pipeline to create new
kinesis and firehose resources and update the lambda transform function used in
firehose. If the `--create_kinesis` arg is excluded, then existing kinesis resources
are used. If the lambda container image used by the lambda function producing the tweets
needs to be updated, then pass `--image_uri` with the new docker image uri to update
the function with.

```
$ poetry shell                                                   
Virtual environment already activated: /Users/rk1103/Library/Caches/pypoetry/virtualenvs/aws-etl-fV9WWBi4-py3.9

$ export LAMBDA_ROLE=<lambda-arn>
$ sh kinesis/run_stream_workflow.sh --role $LAMBDA_ROLE --create_kinesis

 Running Twitter stream to Kinesis and S3 
--image_uri not passed so skipping container image update
--create_kinesis set to true so creating kinesis stream and firehose

 Stream already exists so deleting...
Creating new stream kinesis-twitter-stream: 

{
    "ResponseMetadata": {
        "HTTPHeaders": {
            "content-length": "0",
            "content-type": "application/x-amz-json-1.1",
            "date": "Thu, 21 Apr 2022 22:52:37 GMT",
            "x-amz-id-2": "RIjwfBudY7kNSyM+q2EFJRhCTfWqIVPAAkexx8em4Dy3nlgNatnSH+6Q9ti8Kwqnle73yZCVMR48QNy8VxRWHdHeDG5eEwTF",
            "x-amzn-requestid": "d9f59bd7-8c8a-efbc-832e-79a2d2f22137"
        },
        "HTTPStatusCode": 200,
        "RequestId": "d9f59bd7-8c8a-efbc-832e-79a2d2f22137",
        "RetryAttempts": 0
    }
}
Creating new delivery stream Firehose-S3-twitter with kinesis source 

{
    "DeliveryStreamARN": "arn:aws:firehose:us-east-1:376337229415:deliverystream/Firehose-S3-twitter",
    "ResponseMetadata": {
        "HTTPHeaders": {
            "content-length": "98",
            "content-type": "application/x-amz-json-1.1",
            "date": "Thu, 21 Apr 2022 22:52:47 GMT",
            "x-amz-id-2": "PqVnfLz5WZmIbH7KWTpf7cgpaNFBdMrvJzk1OkwHLRgj7q8beQW8MBUmJcsSuvWIyL21FF8TCRgDWEUhk7kCQJS8L3VkysFi",
            "x-amzn-requestid": "c9a038b0-525c-c28c-937b-da3025799862"
        },
        "HTTPStatusCode": 200,
        "RequestId": "c9a038b0-525c-c28c-937b-da3025799862",
        "RetryAttempts": 0
    }
}

Zipping lambda package for transform-firehouse-b64-json

updating: __init__.py (stored 0%)
updating: lambda-function.py (deflated 54%)

 transform-firehouse-b64-json function already exists so updating with zip source code 
{
    "FunctionName": "transform-firehouse-b64-json",
    "FunctionArn": "arn:aws:lambda:us-east-1:376337229415:function:transform-firehouse-b64-json",
    "Runtime": "python3.9",
    "Role": "arn:aws:iam::376337229415:role/service-role/transform-firehouse-b64-json-role-0uoif8f9",
    "Handler": "lambda_function.lambda_handler",
    "CodeSize": 687,
    "Description": "",
    "Timeout": 300,
    "MemorySize": 1024,
    "LastModified": "2022-04-21T22:53:01.000+0000",
    "CodeSha256": "98Xn/r3nhKhwFBqzUotg8NQUvyehj3RCQrHrRB+LoFE=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "4d78f43f-bc76-487a-8ac2-8ac347183d43",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",
    "PackageType": "Zip"
}

```

to get description of parameters for script use the -h argument

```
sh kinesis/run_stream_workflow.sh -h                           

Description: script for running twitter stream pipeline with kinesis streams    and firehose. 

Syntax: scriptTemplate [--image_uri|--role|--create_kinesis|-h]
options:
role      ARN role for lambda function used in firehose (required)
image_uri  Lambda container image (optional) 
create_kinesis  Creates new kinesis stream and firehose and deletes exiting (optional) 
h          Print this Help.

```

# Streaming tweets using AWS kinesis data streams and firehose

<img width="1000" alt="kinesis_workflow" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/kinesis_workflow.png">

In this workflow, we will create a lambda container image `lambda_packages/tweets-image` which contains twitter 
streaming application code. When invoked, it will publish records into kinesis stream. Kinesis Firehose 
will acts as a consumer to read the records from shards, transform the records (including call AWS Comprehend api to 
retrieve sentiment results) and ingest them into S3 bucket. 

## Create or Updating the Lambda Container Image

This AWS doc https://docs.aws.amazon.com/lambda/latest/dg/images-create.html provides good instructions
on building a container image for a new Lambda function, tagging the image and 
pushing to AWS ECR Registry. 

The bash script `kinesis/create_lambda_container_image.sh` takes in IMAGE_REPO_NAME, FUNCTION_NAME, 
AWS_ACCOUNT_ID and ROLE_NAME as required positional args, with the option of also creating a new ECR repo and 
function by setting an extra two final args to true (see below)

```
$ sh kinesis/create_lambda_container_image.sh test-ecr-repo test-lambda <AWS-ACCOUNT-ID> ImageLambdaTwitter true true 

Docker build path set as /Users/rk1103/Documents/AWS-ETL-Workflows/lambda_packages/tweets-image
Authenticating the Docker CLI to Amazon ECR registry
Login Succeeded

Creating repository in Amazon ECR
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-1:376337229415:repository/test-ecr-repo",
        "registryId": "376337229415",
        "repositoryName": "test-ecr-repo",
        "repositoryUri": "376337229415.dkr.ecr.us-east-1.amazonaws.com/test-ecr-repo",
        "createdAt": "2022-05-31T04:19:43+01:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": true
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}

Building Docker image
[+] Building 0.6s (11/11) FINISHED                                                                                                                       
 => [internal] load build definition from Dockerfile                                                                                                0.0s
 => => transferring dockerfile: 37B                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                   0.0s
 => => transferring context: 2B                                                                                                                     0.0s
 => [internal] load metadata for public.ecr.aws/lambda/python:3.9.2022.03.23.16                                                                     0.5s
 => [internal] load build context                                                                                                                   0.0s
 => => transferring context: 135B                                                                                                                   0.0s
 => [1/6] FROM public.ecr.aws/lambda/python:3.9.2022.03.23.16@sha256:30f4b8ccdd8321fb9b22f0f32e688c225044497b1a4e82b53d3554efd452bab3               0.0s
 => CACHED [2/6] COPY main_twitter.py /var/task                                                                                                     0.0s
 => CACHED [3/6] COPY secrets.py /var/task                                                                                                          0.0s
 => CACHED [4/6] COPY tweets_api.py /var/task                                                                                                       0.0s
 => CACHED [5/6] COPY requirements.txt  .                                                                                                           0.0s
 => CACHED [6/6] RUN  pip3 install -r requirements.txt --target "/var/task"                                                                         0.0s
 => exporting to image                                                                                                                              0.0s
 => => exporting layers                                                                                                                             0.0s
 => => writing image sha256:40e0215af63ea56c21fa05a4836f16901afe1c6862979ca3c94867a941a5b0ba                                                        0.0s
 => => naming to docker.io/library/test-ecr-repo:latest                                                                                             0.0s

Tagging image to match repository name, and deploying the image to Amazon ECR using the docker push command.
The push refers to repository [376337229415.dkr.ecr.us-east-1.amazonaws.com/test-ecr-repo]
adeb7b4ffed9: Pushed 
89ab807769df: Pushed 
888c565dab7f: Pushed 
ed552c17c0fa: Pushed 
ef6568bd8948: Pushed 
0a2ffc791a55: Pushed 
af2bca515e37: Pushed 
5f96311c404e: Pushed 
87bc6f0d5aac: Pushed 
f2ae3f427fe6: Pushed 
c662e800f5c9: Pushed 
latest: digest: sha256:92c11da0a590877c354790aea322c41f1917cf9f3f1a7bb249859f4d7df56737 size: 2621


Creating lambda image with ECR URI
{
    "FunctionName": "test-image",
    "FunctionArn": "arn:aws:lambda:us-east-1:376337229415:function:test-image",
    "Role": "arn:aws:iam::376337229415:role/ImageLambdaTwitter",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 300,
    "MemorySize": 1024,
    "LastModified": "2022-05-31T04:17:47.747+0000",
    "CodeSha256": "92c11da0a590877c354790aea322c41f1917cf9f3f1a7bb249859f4d7df56737",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "ef3b5cd3-533e-4708-87af-8e0adf85beac",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Image",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    }
}

```

If only the 4 mandatory args are passed, this will assume we already have an existing
lambda function and ECR repo already created and we just want to update them. 
Excluding the last two (optional) boolean arguments will use their default values (false ) 
and skip the steps for creating lambda and ecr repo resources.  The image will then just be 
built and pushed to existing ECR repo and existing lambda function URI updated to latest tag.

```
sh kinesis/create_lambda_container_image.sh test-ecr-repo test-lambda <AWS-ACCOUNT-ID> ImageLambdaTwitter
```

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

An example of operation of the transform is shown in notebooks/lambda-firehose-test.ipynb
The function carries out the following tasks:

* decode the binary data to text 
* translate the text (AWS Translate)
* analyse sentiment  and detect entities (AWS Comprehend) 
  and add as new key value for each 
* Add a new line at the end of each data record. By default firehose dumps the json records into S3 in one line
* base64 encode the records
* return the data in the format required by Firehose

The lambda_packages/transform-firehouse-b64-json package with the modules then need to be added in a 
zip. No additional dependencies need to be installed before deployment as the modules use basic python packages,
so we can run the following command to create a new zip and add all modules to it

```
$ cd lambda_packages/transform-firehouse-b64-json
$ zip ../transform-firehouse-b64-json.zip *
```

Create the lambda function using the following command passing in the path to
the newly created zip, lambda role arn and adapt configurations (timeout, memory etc)
as required

```
$ aws lambda create-function --function-name transform-firehouse-b64-json --runtime python3.9 \ 
--zip-file fileb://../transform-firehouse-b64-json.zip \
--role <lambda-role-arn> --timeout 40 --memory-size 1024 --handler lambda_function.lambda_handler
```


or if the lambda function is already created, then update it with the following:

```
$ aws lambda update-function-code --function-name transform-firehose --zip-file fileb://../transform-firehouse-b64-json.zip
```

## Run entire pipeline end to end. 

The example below executes a bash script to run most of the steps described above; create new kinesis and firehose resources 
and update the lambda transform function used in  firehose. If the `--create_kinesis` arg is excluded, then existing kinesis resources
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


## Producer 

We can now start streaming tweets using the application code in a lambda which is 
described in more detail in https://github.com/ryankarlos/codepipeline. 


We can invoke the function using the command below to produce tweets which can be 
streamed into kinesis data stream created above and then subsequently ingested by firehose

```
$ aws lambda invoke --function-name LambdaTwitter --payload '{ "keyword": "CNN+", "delivery": "realtime", "duration": 200 , "kinesis_stream_name":"kinesis-twitter-stream"}' --cli-binary-format 'raw-in-base64-out'  datasets/outputs/raw_tweets/outfile.json 
 

{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}

```

If the source code in https://github.com/ryankarlos/codepipeline is rebuilt again and published to ECR, 
the existing lambda function would need to be updated with the URI of the latest image tag.


```
$ aws lambda update-function-code --function-name LambdaTwitter --image-uri <image-uri>
```

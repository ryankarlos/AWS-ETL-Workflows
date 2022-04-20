
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
kinesis/config/kinesis_stream.json

```
python kinesis/config/create_kinesis_streams.py 

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


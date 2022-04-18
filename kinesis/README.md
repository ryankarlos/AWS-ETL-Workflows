## Configuring kinesis streams

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




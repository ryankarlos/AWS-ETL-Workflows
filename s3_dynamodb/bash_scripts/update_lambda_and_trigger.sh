#!/bin/bash

cd ~/Documents/aws_etl/s3_dynamodb
echo ''
echo "updating zip file with updated handler"
zip batch_write_dynamodb.zip ddb_io.py lambda_function.py schema.py
echo ''
echo "update function code with updated zip source code"
aws lambda update-function-code --function-name batch_write_s3_dynamodb --zip-file fileb://batch_write_dynamodb.zip
echo ''
echo "put object in S3 to trigger lambda execution"
aws s3api put-object --bucket movies-data-json --key transformed/moviedata.json --body ../datasets/moviedata.json
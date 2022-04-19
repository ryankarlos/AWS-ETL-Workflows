#!/bin/bash
printf '\n Running s3 to dynamo batch write script'

DATA=${1-datasets/moviedata.json}
FUNCTION_NAME=${2-batch_write_s3_dynamodb}
S3_BUCKET=${3-movies-data-json}
OBJECT_KEY=${4-transformed/moviedata.json}
# use default values if not passed in via command args
ZIP_PATH=data-pipelines/s3_dynamodb/lambdas/batch_write_dynamodb.zip
DYNAMO_LAMBDA_PATH=lambda_packages/batch_write_dynamodb
CMD_ZIP="zip $ZIP_PATH ${DYNAMO_LAMBDA_PATH}/ddb_io.py ${DYNAMO_LAMBDA_PATH}/lambda_function.py ${DYNAMO_LAMBDA_PATH}/schema.py"
CMD_UPDATE_LAMBDA="aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb://${ZIP_PATH}"
CMD_S3_PUT="aws s3api put-object --bucket ${S3_BUCKET} --key ${OBJECT_KEY} --body ${DATA}"

if [[ $PWD = */aws_etl ]]; then
  printf  '\n updating zip file with updated handler'
  echo "running command....:"
  echo " ${CMD_ZIP}"
  eval "$CMD_ZIP"
else
  echo "current dir in ${PWD}, you need to cd into root of aws_etl repo"
  exit 1
fi;

if [[ -$? -eq 0 ]];then
  printf '\n update function code with updated zip source code \n'
  eval "$CMD_UPDATE_LAMBDA"
fi;

if [[ -$? -eq 0 ]]; then
  printf '\n put object in S3 to trigger lambda execution \n'
  eval "$CMD_S3_PUT"
fi;

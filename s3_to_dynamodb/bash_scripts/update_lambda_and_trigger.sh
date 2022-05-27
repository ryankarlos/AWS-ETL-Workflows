#!/bin/bash

printf '\n Running s3 to dynamo batch write script'

# use default values if not passed in via command args
FIRST_FUNCTION_NAME=${1-ddb_input_transform}
SECOND_FUNCTION_NAME=${2-batch_write_s3_dynamodb}
DATA=${3-datasets/moviedata.json}
LAMBDA_SOURCE_CODE=lambda_packages
S3_BUCKET=movies-data-json
OBJECT_KEY=raw/moviedata.json
CMD_S3_PUT="aws s3api put-object --bucket ${S3_BUCKET} --key ${OBJECT_KEY} --body ${DATA}"

create_update_lambda() {
  (
  set -e
  if aws lambda list-functions --query 'Functions[*].[FunctionName]'| grep "${1}" > /dev/null; then
    printf "\n %s function already exists so updating with zip source code \n" "${1}"
    aws lambda update-function-code --function-name "${1}" --zip-file fileb://"${2}"
  else
    printf '\n Creating new function %s with zip \n' "${1}"
    aws lambda create-function --function-name "${1}" --runtime python3.9 --zip-file fileb://"${2}" \
    --role arn:aws:iam::376337229415:role/service-role/batch_write_s3_dynamodb-role-ms0y29fp \
    --timeout 40 --memory-size 1024 --handler lambda_function.lambda_handler
  fi;
  )
}

if [[ $PWD = */aws_etl ]]; then
  echo ""
  echo "Zipping lambda package for ${FIRST_FUNCTION_NAME}"
  cd ${LAMBDA_SOURCE_CODE}/${FIRST_FUNCTION_NAME}
  zip ../${FIRST_FUNCTION_NAME}.zip *
  echo ""
  echo "Zipping lambda package for ${SECOND_FUNCTION_NAME}"
  cd ../${SECOND_FUNCTION_NAME}/
  zip ../${SECOND_FUNCTION_NAME}.zip *
  cd ../..
else
  echo "current dir in ${PWD}, you need to cd into root of aws_etl repo"
  exit 1
fi;

if [[ -$? -eq 0 ]];then
  create_update_lambda "${FIRST_FUNCTION_NAME}" ${LAMBDA_SOURCE_CODE}/${FIRST_FUNCTION_NAME}.zip
  create_update_lambda "${SECOND_FUNCTION_NAME}" ${LAMBDA_SOURCE_CODE}/${SECOND_FUNCTION_NAME}.zip
fi;

if [[ -$? -eq 0 ]]; then
  printf '\n put object in S3 to trigger lambda execution \n'
  eval "$CMD_S3_PUT"
fi;

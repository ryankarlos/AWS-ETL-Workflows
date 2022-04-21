#!/bin/bash
set -e # auto exit script if error

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
  echo
   echo "Description: script for running twitter stream pipeline with kinesis streams \
   and firehose. "
   echo
   echo "Syntax: scriptTemplate [--image_uri|--role|--create_kinesis|-h]"
   echo "options:"
   echo "role       ARN role for lambda function used in firehose (required)"
   echo "image_uri  Lambda container image (optional) "
  echo "create_kinesis  Creates new kinesis stream and firehose and deletes exiting (optional) "
   echo "h          Print this Help."
   echo
}


# Get the options

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
   esac
done


IMAGE_URI=""
FIREHOSE_LAMBDA=transform-firehouse-b64-json
LAMBDA_SOURCE_CODE=lambda_packages

while [[ "$#" -gt 0 ]]
do case $1 in
    --image_uri) IMAGE_URI="$2"
    shift;;
    --role) LAMBDA_ROLE="$2"
    shift;;
    --create_kinesis) CREATE_KINESIS_STREAM=true ;;
    *) echo "Unknown parameter passed: $1"
    exit 1;;
esac
shift
done

if [[ -z $LAMBDA_ROLE ]];
then
  echo "--role argument for lambda firehose arn role needs to be passed"
  exit 1
fi;


printf '\n Running Twitter stream to Kinesis and S3 \n'



update_twitter_stream_lambda_container_image(){
   if [[ ! -z $IMAGE_URI ]];
   then
     echo "Updating container image for ${1}"
     aws lambda update-function-code --function-name "${1}" --image-uri "${2}"
  else
    echo "--image_uri not passed so skipping container image update"
  fi;
}


create_update_firehose_lambda_zip() {
  (
  echo
  echo "Zipping lambda package for ${FIREHOSE_LAMBDA}"
  echo
  cd ${LAMBDA_SOURCE_CODE}/${FIREHOSE_LAMBDA} || exit
  # shellcheck disable=SC2035
  zip ../${FIREHOSE_LAMBDA}.zip *
    if [[ -$? -eq 0 ]];then
      if aws lambda list-functions --query 'Functions[*].[FunctionName]'| grep "${1}" > /dev/null; then
        printf "\n %s function already exists so updating with zip source code \n" "${1}"
        aws lambda update-function-code --function-name "${1}" --zip-file fileb://../"${1}.zip"
      else
        printf '\n Creating new function %s with zip \n' "${1}"
        aws lambda create-function --function-name "${1}" --runtime python3.9 --zip-file fileb://../"${1}.zip" \
        --role "$LAMBDA_ROLE" --timeout 40 --memory-size 1024 --handler lambda_function.lambda_handler
      fi;
  fi;
  )
}

update_twitter_stream_lambda_container_image "${FIREHOSE_LAMBDA}" "${IMAGE_URI}";


if [[ "${CREATE_KINESIS_STREAM}" = true ]];
then
  echo "--create_kinesis set to true so creating kinesis stream and firehose"
  python kinesis/create_kinesis_streams.py
  sleep 10
fi;


if [[ -$? -eq 0 ]];
 then
   create_update_firehose_lambda_zip "${FIREHOSE_LAMBDA}" ${LAMBDA_SOURCE_CODE}/${FIREHOSE_LAMBDA}.zip
fi;






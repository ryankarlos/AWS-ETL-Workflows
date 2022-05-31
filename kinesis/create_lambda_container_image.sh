
IMAGE_REPO_NAME=${1}
FUNCTION_NAME=${2}
AWS_ACCOUNT_ID=${3}
ROLE_NAME=${4}
CREATE_LAMBDA=${5:-false}
CREATE_ECR_REPO=${6:-false}
AWS_DEFAULT_REGION=us-east-1
IMAGE_TAG=latest
REPO_ROOT=$( cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")" )" || exit ; pwd -P )
DOCKER_BUILD_PATH=$REPO_ROOT/lambda_packages/tweets-image || exit
ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

echo""
echo "Docker build path set as $DOCKER_BUILD_PATH"
echo "Authenticating the Docker CLI to Amazon ECR registry"
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS \
      --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com


if [[ "${CREATE_ECR_REPO}" = true ]];then
  echo ""
  echo "Creating repository in Amazon ECR"
  aws ecr create-repository --repository-name $IMAGE_REPO_NAME --image-scanning-configuration scanOnPush=true \
      --image-tag-mutability MUTABLE \

fi;

if [[ $? -eq 0 ]];then
  echo ""
  echo "Building Docker image"
  docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG $DOCKER_BUILD_PATH
fi;

if [[ $? -eq 0 ]];then
  echo ""
  echo "Tagging image to match repository name, and deploying the image to Amazon ECR using the docker push command."
  docker tag "$IMAGE_REPO_NAME":$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  docker push $ECR_URI
fi;

if [[ $? -eq 0 ]];then
  if [[ "${CREATE_LAMBDA}" = true ]];then
     echo ""
      echo "Creating lambda image with ECR URI"
      aws lambda create-function --function-name test-image --package-type Image --code ImageUri=$ECR_URI \
      --timeout 300 --memory-size 1024 --role $ROLE_ARN
  else
      echo ""
      echo "Updating lambda image"
      aws lambda update-function-code --function-name test-image --image-uri $ECR_URI
  fi;
fi;





FROM public.ecr.aws/lambda/python:3.9.2022.03.23.16

# Copy function code
COPY main_twitter.py ${LAMBDA_TASK_ROOT}
COPY secrets.py ${LAMBDA_TASK_ROOT}
COPY tweets_api.py ${LAMBDA_TASK_ROOT}

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler
CMD [ "main_twitter.handler" ]
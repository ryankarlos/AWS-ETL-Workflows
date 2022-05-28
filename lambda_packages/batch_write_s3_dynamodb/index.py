import json
import boto3
from schema import Movies
from ddb_io import batch_write_items_to_dynamo
from sns_publish import publish_sns_message
import urllib.parse


def lambda_handler(event, context):

    s3 = boto3.client("s3")
    ddb = boto3.client("dynamodb")
    sns = boto3.client("sns")
    movies = Movies(ddb)
    table_name = "movies"
    print(f"Received event: {event}")
    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    response = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(response["Body"].read().decode())["movies"]
    print(f"Data read from S3 {bucket}/{key}: {data}")
    try:
        movies.create_table(table_name)
        print(f"Created new table {table_name} imn DynamoDB")
    except Exception as e:
        if e.__class__.__name__ == "ResourceInUseException":
            description = ddb.describe_table(TableName=table_name)
            print(
                f"Table {table_name} already exists with table definition: {description}"
            )
    finally:
        print("Starting batch write to dynamo")
        batch_write_items_to_dynamo(table_name=table_name, data_dict=data)
        topic_list = sns.list_topics()["Topics"]
        topic_arn: str = [
            topic["TopicArn"]
            for topic in topic_list
            if topic["TopicArn"].split(":")[-1] == "etl"
        ][0]
        subject = "s3 to dynamodb etl"
        default_message = (
            f"Successfully written {len(data)} items to dynamo db {table_name}"
        )
        publish_sns_message(sns, subject, default_message, topic_arn)

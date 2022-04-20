import json
import boto3
from schema import Movies
from ddb_io import batch_write_items_to_dynamo
import urllib.parse


def lambda_handler(event, context):

    s3 = boto3.client("s3")
    client = boto3.client("dynamodb")
    movies = Movies(client)
    table_name = "movies"
    print(f"Received event: {event}")
    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    response = s3.get_object(Bucket=bucket, Key=key)
    print(response)
    data = json.loads(response["Body"].read().decode())
    print(data)
    try:
        movies.create_table(table_name)
    except Exception as e:
        if e.__class__.__name__ == "ResourceInUseException":
            description = client.describe_table(TableName=table_name)
            print(f"Table definition for {table_name}: {description}")
    finally:
        print(f"Data has {len(data)} items")
        batch_write_items_to_dynamo(table_name=table_name, data_dict=data)
    return {"records": data}

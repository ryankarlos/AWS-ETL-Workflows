import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from schema import Movies
from ddb_io import format_json_for_dynamo_db, write_to_json, batch_write_items_to_dynamo


def scan_dynamo_table(table_name, expression: boto3.dynamodb.conditions.Attr):
    """
    scans dynamo table and returns filtered items based on expression
    e.g expression require boto3.dynamodb.conditions.Attr class
    when the condition is related to an attribute of the item
    e.g expression = Attr('title').begins_with('R') & Attr('rating').gt(7)
    """
    # Get the service resource.
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(table_name)

    response = table.scan(FilterExpression=expression)
    items = response["Items"]
    print(items)


def main(table_name):

    client = boto3.client("dynamodb")

    movies = Movies(client)
    try:
        movies.create_table(table_name)
    except ClientError as e:
        if str(e).endswith(f"Table already exists: {table_name}"):
            response = client.describe_table(TableName=table_name)
            result = json.dumps(response, indent=4, sort_keys=True, default=str)
            print(result)
    # finally:
    #     movies.delete_table(table_name)
    json_dict = format_json_for_dynamo_db()
    write_to_json(json_dict)
    batch_write_items_to_dynamo(table_name=table_name)


if __name__ == "__main__":
    main(table_name="movies")

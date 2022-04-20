import json
import boto3
import logging
from decimal import Decimal

logger = logging.getLogger("io")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def batch_write_items_to_dynamo(table_name, data_dict):
    # Get the service resource.
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    # Get the ddb client for calling describe table method
    client = boto3.client("dynamodb")
    response = client.describe_table(TableName=table_name)
    print(f" Dynamo table {table_name} description: {response}")
    with table.batch_writer() as batch:
        for item in data_dict:
            item_to_put: dict = json.loads(json.dumps(item), parse_float=Decimal)
            batch.put_item(Item=item_to_put)
            print(f"Writing {item} to Dynamo db table {table}")

    print(f"Finished writing {len(data_dict)} items")


def scan_dynamo_table(table_name, expression):
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

import json
import boto3
import logging

logger = logging.getLogger("io")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def format_json_for_dynamo_db(data):
    json_dict = {"movies": []}
    for i in range(len(data)):
        json_dict["movies"].append(
            {  # must not specify the type of key attributes otherwise throws validation errors when
                # batch writing to table
                "year": data[i]["year"],
                "title": data[i]["title"],
                "genres": [genre for genre in data[i]["info"]["genres"]],
                "directors": [
                    director for director in data[i]["info"]["directors"]
                ],
                "actors": [actor for actor in data[i]["info"]["actors"]],
                "rank": data[i]["info"]["rank"],
                "running_time_secs": data[i]["info"].get("running_time_secs", -1),
                "plot": data[i]["info"].get("plot", "Unknown"),
            }
        )
    return json_dict


def write_to_json(json_dict, s3_path):
    with open(s3_path, "w") as f:
        # indent for visual
        result = json.dumps(json_dict, indent=4)
        f.write(result)


def batch_write_items_to_dynamo(
    table_name, data_dict
):
    # Get the service resource.
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    # Get the ddb client for calling describe table method
    client= boto3.client("dynamodb")
    response = client.describe_table(
        TableName=table_name
    )
    print(f" Dynamo table {table_name} description: {response}")
    with table.batch_writer() as batch:
        for item in data_dict["movies"]:
            item_to_put: dict = json.loads(json.dumps(item))
            batch.put_item(Item=item_to_put)
            print(f"Writing {item} to Dynamo db table {table}")

    print(f"Finished writing {len(data_dict['movies'])} items")


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


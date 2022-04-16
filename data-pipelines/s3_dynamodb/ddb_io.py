import json
import boto3
import logging

logger = logging.getLogger("io")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def format_json_for_dynamo_db(file_path="datasets/moviedata.json"):
    with open(file_path) as f:
        data = json.load(f)
        json_dict = {"movies": []}
        for i in range(len(data)):
            json_dict["movies"].append(
                {  # must not specify the type of key attributes otherwise throws validation errors when
                    # batch writing to table
                    "year": data[i]["year"],
                    "title": data[i]["title"],
                    "genres": {
                        "L": [{"S": genre} for genre in data[i]["info"]["genres"]]
                    },
                    "directors": {
                        "L": [
                            {"S": director} for director in data[i]["info"]["directors"]
                        ]
                    },
                    "actors": {
                        "L": [{"S": actor} for actor in data[i]["info"]["actors"]]
                    },
                    "rank": {"N": data[i]["info"]["rank"]},
                    "running_time_secs": {
                        "N": data[i]["info"].get("running_time_secs", -1)
                    },
                    "plot": {"S": data[i]["info"].get("plot", "Unknown")},
                }
            )
        return json_dict


def write_to_json(json_dict, file_path="datasets/movies_input_dynamodb.json"):
    with open(file_path, "w") as f:
        # indent for visual
        result = json.dumps(json_dict, indent=4)
        f.write(result)


def batch_write_items_to_dynamo(
    table_name, file_path="datasets/movies_input_dynamodb.json"
):
    # Get the service resource.
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    with open(file_path) as f:
        data_dict = json.load(f)

    with table.batch_writer() as batch:
        for item in data_dict["movies"]:
            item_to_put: dict = json.loads(json.dumps(item))
            batch.put_item(Item=item_to_put)

    logger.info(f"Finished writing {len(data_dict['movies'])} items")

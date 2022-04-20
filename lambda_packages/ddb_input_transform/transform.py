import json
import boto3
import logging
import urllib

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
                "directors": [director for director in data[i]["info"]["directors"]],
                "actors": [actor for actor in data[i]["info"]["actors"]],
                "rank": data[i]["info"]["rank"],
                "running_time_secs": data[i]["info"].get("running_time_secs", -1),
                "plot": data[i]["info"].get("plot", "Unknown"),
            }
        )
    return json_dict


def get_s3_object(event):
    s3 = boto3.client("s3")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    response = s3.get_object(Bucket=bucket, Key=key)
    print(response)
    data = json.loads(response["Body"].read().decode())
    print(f"Raw data in S3 {bucket}/{key} has {len(data)} items: {data}")
    return data, bucket


def write_to_s3(data, bucket, file_name):
    s3 = boto3.client("s3")
    s3.put_object(Body=data, Bucket=bucket, Key=f"transformed/{file_name}")

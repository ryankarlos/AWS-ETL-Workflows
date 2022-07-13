import json
import boto3
import time
from pathlib import Path
import os

firehose = boto3.client("firehose")
kinesis = boto3.client("kinesis")
path = Path(os.path.realpath(__file__))


def create_kinesis_stream(file_name="kinesis_stream.json"):
    config_path = os.path.join(path.parent, "config", file_name)
    with open(config_path) as f:
        request = json.load(f)
        stream_name = request["StreamName"]
    if stream_name in kinesis.list_streams()["StreamNames"]:
        print("\n Stream already exists so deleting...")
        kinesis.delete_stream(StreamName=stream_name)
        time.sleep(10)

    print(f"Creating new stream {stream_name}: \n")
    if request["StreamModeDetails"]["StreamMode"] == "ON_DEMAND":
        request.pop(
            "ShardCount"
        )  # if on demand param passed, shard count will throw error
    response = kinesis.create_stream(**request)
    res_str = json.dumps(response, sort_keys=True, indent=4)
    print(res_str)
    return response


def create_firehose_delivery_stream(file_name="firehose_description.json"):
    """
    Creates firehose delivery stream. If this already exists, then deletes and
    creates new one with same name. Needs json config file, with stream name specified
    """
    config_path = os.path.join(path.parent, "config", file_name)
    with open(config_path) as f:
        request = json.load(f)
        stream_name = request["DeliveryStreamName"]
    if stream_name in firehose.list_delivery_streams()["DeliveryStreamNames"]:
        print("\n Firehose delivery stream already exists so deleting...")
        firehose.delete_delivery_stream(DeliveryStreamName=stream_name)
        # do this as print(client.waiter_names) returns [] so assuming no waiters for this client
        time.sleep(10)

    print(f"Creating new delivery stream {stream_name} with kinesis source \n")
    response = firehose.create_delivery_stream(**request)
    res_str = json.dumps(response, sort_keys=True, indent=4)
    print(res_str)
    return response


if __name__ == "__main__":
    create_kinesis_stream()
    time.sleep(10)
    create_firehose_delivery_stream()

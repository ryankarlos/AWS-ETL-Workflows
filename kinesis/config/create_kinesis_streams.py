import json
import boto3
import time

client = boto3.client("firehose")
kinesis = boto3.client("kinesis")


def create_firehose_delivery_stream(config_path="firehose_description.json"):
    """
    Creates firehose delivery stream. If this already exists, then deletes and
    creates new one with same name. Needs json config file, with stream name specified
    """
    with open(config_path) as f:
        request = json.load(f)
        stream_name = request["DeliveryStreamName"]
    if stream_name in client.list_delivery_streams()["DeliveryStreamNames"]:
        print("\n Stream already exists so deleting...")
        client.delete_delivery_stream(DeliveryStreamName=stream_name)
        # do this as print(client.waiter_names) returns [] so assuming no waiters for this client
        time.sleep(1)

    print(f"creating new delivery stream {stream_name} \n")
    response = client.create_delivery_stream(**request)
    res_str = json.dumps(response, sort_keys=True, indent=4)
    print(res_str)
    return response


if __name__ == "__main__":
    create_firehose_delivery_stream()

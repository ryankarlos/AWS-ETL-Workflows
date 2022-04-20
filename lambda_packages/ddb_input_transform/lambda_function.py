from transform import format_json_for_dynamo_db, write_to_s3, get_s3_object
import json


def lambda_handler(event, context):
    data, bucket = get_s3_object(event)
    data_transformed = format_json_for_dynamo_db(data)
    result = json.dumps(data, indent=4)
    write_to_s3(result, bucket, "movies_transformed.json")
    return {"records": result}

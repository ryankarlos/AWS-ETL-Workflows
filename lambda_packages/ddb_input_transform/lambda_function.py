from transform import format_json_for_dynamo_db, write_to_s3, get_s3_object
import json


def lambda_handler(event, context):
    data, bucket = get_s3_object(event)
    data_transformed = format_json_for_dynamo_db(data)
    print(f'Transformed data: {data_transformed}')
    result = json.dumps(data_transformed, indent=4)
    file_name = "movies_transformed.json"
    write_to_s3(result, bucket, file_name)
    print(f'Written to S3 {bucket}/transformed/{file_name}')
import boto3

client = boto3.client('data-migration')


def lambda_handler(event, context):
    response = client.describe_db_instances(DBInstanceIdentifier=event['rds_instance_id'])
    current_state = response['DBInstances'][0]['DBInstanceStatus']
    print(f"db instance current status: {current_state}")
    if event['rds_required_state'] == "available":
        if current_state == "stopped":
            print(f"Starting DB instance: {event['rds_instance_id']}")
            response = client.start_db_instance(DBInstanceIdentifier=event['rds_instance_id'])
            print(response)
    elif event["rds_required_state"] == "stopped":
        if current_state == "available":
            print(f"Stopping DB instance: {event['rds_instance_id']}")
            response = client.stop_db_instance(DBInstanceIdentifier=event['rds_instance_id'])
            print(response)


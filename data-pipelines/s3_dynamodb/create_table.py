import logging
from botocore.exceptions import ClientError
import boto3
import json

logger = logging.getLogger("create_table")
logger.setLevel(logging.ERROR)

client = boto3.client("dynamodb")


class Movies:
    """
    Example from https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.CreateTable.html"""

    def __init__(self, client):
        self.dyn_resource = client

    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that uses the  year of
        the movie as the partition key and the title as the sort key.

        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            response = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "year", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "title", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "year", "AttributeType": "N"},
                    {"AttributeName": "title", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            result = json.dumps(response, indent=4, sort_keys=True, default=str)
            print(result)
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def delete_table(self, table_name):
        """
        Deletes existing dynamodb table
        """

        try:
            client.delete_table(TableName=table_name)
        except ClientError as err:
            logger.error(
                "Couldn't delete table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )


if __name__ == "__main__":
    table_name = "movies"
    movies = Movies(client)
    try:
        movies.create_table(table_name)
    except ClientError as e:
        if str(e).endswith(f"Table already exists: {table_name}"):
            response = client.describe_table(TableName="movies")
            result = json.dumps(response, indent=4,sort_keys=True, default=str)
            print(result)





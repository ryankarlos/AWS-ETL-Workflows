import logging
from botocore.exceptions import ClientError
import json

logger = logging.getLogger("schema")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


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
                    {"AttributeName": "year", "KeyType": "HASH",},  # Partition key
                    {"AttributeName": "title", "KeyType": "RANGE",},  # SORT key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "title", "AttributeType": "S"},
                    {"AttributeName": "year", "AttributeType": "N"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            result = json.dumps(response, indent=4, sort_keys=True, default=str)
            logger.info("Creating Table: \n")
            print(result)
            ddb_waiter(self.dyn_resource, "table_exists", table_name)
        except ClientError as err:
            logger.info(
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
            logger.info(f"Deleting table {table_name}")
            self.dyn_resource.delete_table(TableName=table_name)
            ddb_waiter(self.dyn_resource, "table_not_exists", table_name)
        except ClientError as err:
            logger.info(
                "Couldn't delete table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )


def ddb_waiter(resource, waiter, table_name):
    """
    Retrieve waiter instance that will wait till a specified
    # S3 bucket exists
    :param resource: dynamo db resource
    :param waiter: name of waiter e.g. "table_exists", "table_not_exists"
    :param table_name: table to wait for
    :return:
    """
    # obtain waiter for table exists
    table_waiter = resource.get_waiter(waiter)
    # Begin waiting for the table creation
    logger.info(f"Waiting for Table waiter {waiter} .....")
    table_waiter.wait(TableName=table_name)

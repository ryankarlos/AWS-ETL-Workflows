import logging
import json
from botocore.exceptions import ClientError

logger = logging.getLogger("sns")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def publish_sns_message(sns_client, subject, default_message, topic_arn):
    try:
        message = {
            "default": default_message,
        }
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=subject,
            MessageStructure="json",
        )
        message_id = response["MessageId"]
        logger.info("Published message to topic %s.", topic_arn)
    except ClientError:
        logger.exception("Couldn't publish message to topic %s.", topic_arn)
        raise
    else:
        return message_id

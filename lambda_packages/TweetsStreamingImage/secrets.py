import configparser
import boto3
import json


def get_secrets(
    mode="aws",
    path="/Users/rk1103/Documents/secrets/twitter_conf.ini",
    filter="Twitter",
):
    if mode == "aws":
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager",)
        response = client.list_secrets(
            Filters=[{"Key": "description", "Values": [filter]}],
        )
        arn = response["SecretList"][0]["ARN"]
        print(f"\n using arn: {arn} as description has value '{filter}' passed")
        get_secret_value_response = client.get_secret_value(SecretId=arn)
        secret = get_secret_value_response["SecretString"]
        secret = json.loads(secret)
        print(f"Successfully retrieved {mode} secrets !")
    elif mode == "local":
        config = configparser.ConfigParser(interpolation=None)
        config.read(path)
        secret = {
            "consumer_key": config["DEFAULT"]["APIKey"],
            "consumer_secret": config["DEFAULT"]["APIKeySecret"],
            "access_token": config["DEFAULT"]["AccessToken"],
            "access_token_secret": config["DEFAULT"]["AccessTokenSecret"],
            "bearer_token": config["DEFAULT"]["BearerToken"],
        }
        print(f"\n Successfully retrieved {mode} secrets from {path}")
    else:
        raise ValueError(f"'mode' needs to be either 'local' or 'aws'")

    return secret

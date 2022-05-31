import tweepy
import time
import json
import boto3


class MyStreamListener(tweepy.Stream):
    def __init__(
        self, event, consumer_key, consumer_secret, access_token, access_token_secret
    ):
        self.start_time = time.time()
        self.time_limit = event["duration"]
        if event.get("kinesis_stream_name"):
            self.stream_name = event["kinesis_stream_name"]
        else:
            self.stream_name = None
        super().__init__(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

    def on_data(self, data):

        tweet = json.loads(data)
        if time.time() - self.start_time > self.time_limit:
            print(f"{self.time_limit} seconds time limit for streaming reached")
            print("Success !")
            self.disconnect()
        else:
            if tweet:
                try:
                    if tweet['truncated']:
                        # if tweet is truncated, then Status object will contain an extended_tweet attribute
                        text = tweet['extended_tweet']['full_text']
                    else:
                        text = tweet["text"]
                    if not text.startswith("RT"):
                        payload = {
                            "created_at": tweet["created_at"],
                            "handle": tweet["user"]["screen_name"],
                            "text": text,
                            "favourite_count": tweet["user"]["favourites_count"],
                            "retweet_count": tweet["retweet_count"],
                            "retweeted": tweet["retweeted"],
                            "followers_count": tweet["user"]["followers_count"],
                            "friends_count": tweet["user"]["friends_count"],
                            "location": tweet["user"]["location"],
                            "lang": tweet["user"]["lang"],
                        }
                        print(f"{payload}")
                        if self.stream_name is not None:
                            response = put_kinesis(payload, self.stream_name)
                            print(f"{response} \n")
                except KeyError:
                    # getting empty json in between stream so ignore these
                    pass

    def on_closed(self, response):
        """
        override this method to print rather than log error
        """
        print("Stream connection closed ")


def tweepy_search_api(
    event, consumer_key, consumer_secret, access_token, access_secret
):

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_secret
    )
    start_time = time.time()
    time_limit = event["duration"]
    api = tweepy.API(auth, wait_on_rate_limit=True)
    counter = 0
    for tweet in tweepy.Cursor(
        api.search_tweets, event.get("keyword"), count=100, tweet_mode="extended"
    ).items():
        if time.time() - start_time > time_limit:
            api.session.close()
            print(f"\n {time_limit} seconds time limit reached, so disconneting stream")
            print(f" {counter} tweets streamed ! \n")
            return
        else:
            if not tweet.full_text.startswith("RT"):
                counter += 1
                dt = tweet.created_at
                payload = {
                    "day": dt.day,
                    "month": dt.month,
                    "year": dt.year,
                    "time": dt.time().strftime("%H:%M:%S"),
                    "handle": tweet.user.screen_name,
                    "text": tweet.full_text,
                    "favourite_count": tweet.user.favourites_count,
                    "retweet_count": tweet.retweet_count,
                    "retweeted": tweet.retweeted,
                    "followers_count": tweet.user.followers_count,
                    "friends_count": tweet.user.friends_count,
                    "location": tweet.user.location,
                    "lang": tweet.user.lang,
                }
                print(f"{payload}")
                if event.get("kinesis_stream_name"):
                    response, message_bytes = put_kinesis(
                        payload, event["kinesis_stream_name"]
                    )
                    print(
                        f"Data utf-8 encoded {message_bytes} and put into kinesis stream "
                        f"with response:\n {response} \n"
                    )


def put_kinesis(data, stream_name):
    """
    Put records into kinesis stream. Kinesis by default base64 encodes data entering stream so
    we do not need to base64encode beforehand. Data is however, utf-8 encoded and message passed
    to data parameter in kinesis client put_record method.
    """
    client = boto3.client("kinesis")
    # base64 encode
    message_bytes = json.dumps(data).encode("utf-8")
    response = client.put_record(
        StreamName=stream_name, Data=message_bytes, PartitionKey="month"
    )
    return response, message_bytes

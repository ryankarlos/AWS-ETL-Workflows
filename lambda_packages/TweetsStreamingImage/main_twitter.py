def handler(event, context):
    from tweets_api import tweepy_search_api, MyStreamListener
    from secrets import get_secrets
    import itertools

    response = get_secrets(mode="aws")
    api_keys = list(itertools.islice(response.values(), 4))

    if event["delivery"] == "realtime":
        print(
            "Filtering and streaming realtime Tweets with Twitter Streaming API v1.1: \n"
        )
        stream = MyStreamListener(event, *api_keys)
        stream.filter(track=[event.get("keyword")])

    elif event["delivery"] == "search":
        print("Starting search stream using tweepy Twitter API v1.1 Client: \n")

        tweepy_search_api(event, *api_keys)
    else:
        raise ValueError(
            f"'Delivery value in event payload must be either 'search' or 'realtime '.... "
            f"you passed {event['delivery']}."
        )

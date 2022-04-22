import boto3

comprehend = boto3.client(service_name="comprehend", region_name="us-east-1")
translate = boto3.client(service_name="translate")


def aws_translate(data, source_lang="auto", target_lang="en"):
    response = translate.translate_text(
        Text=data, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang
    )
    response.pop("ResponseMetadata")
    return response


def sentiment_analysis(data):
    sentiment = comprehend.detect_sentiment(Text=data, LanguageCode="en")
    sentiment.pop("ResponseMetadata")
    sentiment["SentimentScore"] = sentiment.get("SentimentScore")
    return sentiment


def entity_detection(data):
    entities = comprehend.detect_entities(Text=data, LanguageCode="en")
    entity_dict = {
        "Entities": [{item["Text"]: item["Type"]} for item in entities["Entities"]]
    }
    return entity_dict

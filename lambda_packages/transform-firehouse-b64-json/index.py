import base64
import json
import itertools
from comprehend_translate_api import aws_translate, sentiment_analysis, entity_detection


def lambda_handler(event, context):
    output = []
    for record in event["records"]:
        payload = base64.b64decode(record["data"]).decode("utf-8")

        data = json.loads(payload)
        translate_response = aws_translate(data["text"])
        sentiment_response = sentiment_analysis(translate_response["TranslatedText"])
        entity_response = entity_detection(translate_response["TranslatedText"])
        # add all the ML response dict key,value pairs to original text payload
        data_adapted = dict(
            list(
                itertools.chain(
                    data.items(),
                    translate_response.items(),
                    sentiment_response.items(),
                    entity_response.items(),
                )
            )
        )
        # convert back to json str for adding new line break between each payload
        # so readable in final txt output in S3
        payload_adapted = json.dumps(data_adapted)
        row_w_newline = payload_adapted + "\n"
        row_w_newline = base64.b64encode(row_w_newline.encode("utf-8"))

        output_record = {
            "recordId": record["recordId"],
            "result": "Ok",
            "data": row_w_newline,
        }

        output.append(output_record)

    print("Processed {} records.".format(len(event["records"])))
    print(output)

    return {"records": output}

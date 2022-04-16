import json


with open("../../datasets/moviedata.json") as f:
    a = json.load(f)
    b = {"movies": []}
    for i in range(len(a)):
        b["movies"].append(
            {
                "year": {"n": a[i]["year"]},
                "title": {"s": a[i]["title"]},
                "genres": {"L": [{"s": genre} for genre in a[i]["info"]["genres"]]},
                "directors": {
                    "L": [{"s": director} for director in a[i]["info"]["directors"]]
                },
                "actors": {"L": [{"s": actor} for actor in a[i]["info"]["actors"]]},
                "rank": {"n": a[i]["info"]["rank"]},
                "rating": {"n": a[i]["info"].get("rating", -1)},
                "running_time_secs": {"n": a[i]["info"].get("running_time_secs", -1)},
                "plot": {"s": a[i]["info"].get("plot", "Unknown")},
            }
        )


with open("../../datasets/movies_input_dynamodb.json", "w") as f:
    # indent for visual
    result = json.dumps(b, indent=4)
    f.write(result)

import requests
import os
import time
import json
from dotenv import load_dotenv
load_dotenv()

headers = {"Authorization": "Bearer " + os.getenv("BEARER")}
# %23 is '#'
url = "https://api.twitter.com/2/tweets/search/recent?query=%23art has:images -is:reply -is:quote -is:retweet&expansions=attachments.media_keys&tweet.fields=referenced_tweets,public_metrics&media.fields=media_key,type,url&max_results=10"

while True:
    r = requests.get(url, headers=headers)
    res = r.json()

    tweets = res["data"]
    media = res["includes"]["media"]
    meta = res["meta"]

    stweet = sorted(tweets, key=lambda t: t["public_metrics"]["like_count"], reverse=True)

    media_keys = [twit["attachments"]["media_keys"][0] for twit in stweet[:5]]

    imgs = list(filter(lambda x: x["media_key"] in media_keys, media))

    data = {"images": imgs}

    res = requests.put('https://giant-fridge-92b65-default-rtdb.firebaseio.com/data.json', json.dumps(data))

    print(res.status_code)
    print('Sleeping for 15 seconds...')
    time.sleep(15)
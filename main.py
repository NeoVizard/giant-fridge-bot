import requests
import os
import time
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
# from keep_alive import keep_alive

load_dotenv()

retry_count = 2
headers = {"Authorization": "Bearer " + os.getenv("BEARER")}
to_date = datetime.utcnow() - timedelta(days=1)
to_date = to_date.replace(microsecond=0)

# %23 is '#'
url = f"https://api.twitter.com/2/tweets/search/recent?query=%23art %23sega has:images -is:reply -is:quote -is:retweet&end_time={to_date.isoformat()}Z&expansions=attachments.media_keys&tweet.fields=referenced_tweets,public_metrics&media.fields=media_key,type,url&max_results=100"
tweet_count = 100

# keep_alive()
while True:
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        res = r.json()

        meta = res["meta"]

        if (meta["result_count"] > 0):
            tweets = res["data"]
            media = res["includes"]["media"]

            while "next_token" in meta:
                new_url = f"{url}&next_token={meta['next_token']}"
                r = requests.get(new_url, headers=headers)
                if(r.status_code == 200):
                    tweet_count+=100
                    print(f"Fetched {tweet_count} tweets...")
                    res = r.json()
                    meta = res["meta"]
                    if meta["result_count"] > 0:
                        tweets += res["data"]
                        media += res["includes"]["media"]
                else:
                    print("Failed to fetch the next page")
                    meta = {}

            print(f"Successfully fetched {len(tweets)} tweets")
            sorted_tweets = sorted(
                tweets, key=lambda t: t["public_metrics"]["like_count"], reverse=True
            )

            media_keys = [t["attachments"]["media_keys"][0] for t in sorted_tweets[:5]]

            imgs = list(filter(lambda x: x["media_key"] in media_keys, media))

            data = {"images": imgs}

            r = requests.put(
                "https://giant-fridge-92b65-default-rtdb.firebaseio.com/data.json",
                json.dumps(data),
            )

            if(r.status_code == 200):
                print("Successfully posted data to firebase")
            else:
                print("Failed to post data to firebase")
    else:
        print("Could not fetch tweets")
        print(r.json())
        if retry_count > 0:
            retry_count -= 1
            continue
        else:
            retry_count = 2
    print("Sleeping for 2 hours...")
    time.sleep(7200)

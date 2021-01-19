'''
    extract viral tweet.
    usage: zcat [tweet data path] | python extract_viral_tweet.py > [path you want to save data]
'''
import sys
import json
import argparse
import logzero
from logzero import logger
import logging
import re

logger.setLevel(logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude_verified",  default=False,
                        action='store_true', help="")
    parser.add_argument("--friend_ratio", type=int, help="")
    parser.add_argument("--favorite_count", type=int, help="")
    parser.add_argument("--retweet_count", type=int, help="")
    parser.add_argument("--exclude_urls",  default=False,
                        action='store_true', help="")
    args = parser.parse_args()
    return args


def is_include_url(text):
    pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    if re.search(pattern, text, re.DOTALL):
        return True
    else:
        return False


def main(fi):
    args = parse_args()
    logger.info(args)
    for line in fi:
        data = json.loads(line)
        # 公式アカウントを除外
        if args.exclude_verified:
            if data["user"]["verified"] is True:
                continue
        # followerがfolloingのx倍いる人のツイートを除外
        if args.friend_ratio * data["user"]["friends_count"] < data["user"]["followers_count"]:
            continue
        # いいねがx以下のツイートを除外
        if data["favorite_count"] < args.favorite_count:
            continue
        # リツイートがx以下のツイートを除外
        if data["retweet_count"] < args.retweet_count:
            continue
        # urlが貼られているツイートは除外
        if args.exclude_urls:
            if is_include_url(data["text"]):
                continue
        #     if data["entities"]["urls"]["url"]:
        #         continue

        print(json.dumps(data))
    return


if __name__ == "__main__":
    main(sys.stdin)

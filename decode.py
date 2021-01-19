'''
extract_viral_tweet.pyで収集したツイッターデータを閲覧するコード
usage : cat [tweet data path] |python decode.py |less
'''
import sys
import json


def main(fi):
    for line in fi:
        data = json.loads(line)
        print(data["text"])
        print("-----------")
    return


if __name__ == "__main__":
    main(sys.stdin)

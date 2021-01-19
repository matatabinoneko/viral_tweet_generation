'''
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

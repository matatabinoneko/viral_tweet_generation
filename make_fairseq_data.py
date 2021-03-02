'''
説明
'''
import argparse
import logzero
from logzero import logger
import logging
from os import path
from typing import List
import random
import json

logger.setLevel(logging.DEBUG)

SEP = "[SEP]"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', type=path.abspath, help='input file path')
    parser.add_argument(
        '-o', '--output', type=path.abspath, help='output file path')
    parser.add_argument(
        '--seed',  type=int, default=1, help='seed')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    logger.info(args)

    # シードを固定
    random.seed(args.seed)

    with open(args.input, 'r') as fin,  open(f"{args.output}", 'w') as fout:
        for line in fin:
            line = json.loads(line)
            # 使用するキーワードを選択
            key_nums = min(random.randint(1, 5), len(line["keywords"]))
            keywords = f" {SEP} ".join(
                random.sample(line["keywords"], key_nums))

            print(f"{keywords}\t{line['tweet']}", file=fout)
    return


if __name__ == '__main__':
    main()

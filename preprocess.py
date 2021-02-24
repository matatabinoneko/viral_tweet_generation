'''
ツイートの前処理を行う
'''

import argparse
import logzero
from logzero import logger
import logging
from os import path
from typing import List
from filtering_type import Filter
import json
import MeCab

logger.setLevel(logging.DEBUG)


mecabTagger = MeCab.Tagger("-Ochasen")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', type=path.abspath, help='input file path')
    parser.add_argument(
        '-o', '--output', type=path.abspath, help='output file path')
    parser.add_argument(
        "--tokenizer", type=str, default="char", help="tokenizer. Select mecab if you want to use mecab"
    )
    args = parser.parse_args()
    return args


def get_keywords(text: str, tokenizer) -> List[str]:
    """
    ツイートからキーワードを抽出

    Parameters
    ----------
    text : str
        ツイート
    tokenizer : トークナイザ

    Returns
    -------
    keywords : List[str]
        キーワードのリスト
    """
    keywords = []
    node = mecabTagger.parseToNode(text)
    while node:
        word = node.surface
        hinshi = node.feature.split(",")[0]
        if hinshi == "名詞":
            keywords.append(tokenizer(word))
        node = node.next
    keywords = list(set(keywords))
    return keywords


def main():
    args = parse_args()
    logger.info(args)

    def tokenizer(text): return self.mecab.parse(text).split(
    ) if args.tokenizer == 'mecab' else ' '.join(list(text))

    filter = Filter()
    with open(args.input, 'r') as fin, open(args.output, 'w') as fout:
        for line in fin:
            try:
                line = json.loads(line)
                text = filter(line["text"])
                keywords = get_keywords(text, tokenizer)
                text = tokenizer(text)

                print(json.dumps(
                    {"keywords": keywords, "tweet": text}, ensure_ascii=False), file=fout)
            except:
                logger.error(f"this data is skipped {line}")


if __name__ == '__main__':
    main()

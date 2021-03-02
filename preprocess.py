'''
ツイートの前処理を行う
'''

import argparse
import logzero
from logzero import logger
import logging
from os import path
from typing import List
from filtering_type import EmoticonFilter
import json
import MeCab
from collections import defaultdict
import re

logger.setLevel(logging.INFO)


mecabTagger = MeCab.Tagger("-Ochasen")

hiragana = re.compile('[ぁ-ゟ]+')


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


def full_width2half_width(text: str) -> str:
    '''
    全角文字を半角文字に変換
    '''
    # 変換
    text = text.translate(str.maketrans(
        {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    return text


def test_full_width2half_width():
    text = "！＂＃＄％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀>？＠ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～"
    trans_text = full_width2half_width(text)
    answer = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`>?@abcdefghijklmnopqrstuvwxyz{|}~'
    assert trans_text == answer, f"{trans_text}\n{answer}"


def is_char_length(text: str, max_length=140) -> bool:
    '''
    max_length以上のツイートの場合はFalseを返す
    '''
    return len(text) <= 140


def test_is_char_length():
    text_list = ["", ''.join(['a' for _ in range(139)]), ''.join(
        ['a' for _ in range(140)]), ''.join(['a' for _ in range(141)])]
    answer_list = [True, True, True, False]
    for text, answer in zip(text_list, answer_list):
        assert is_char_length(text) == answer


def get_keywords(text: str) -> List[str]:
    """
    ツイートからキーワードを抽出

    Parameters
    ----------
    text : str
        ツイート

    Returns
    -------
    keywords : List[str]
        キーワードのリスト
    """
    keywords = []
    node = mecabTagger.parseToNode(text)
    while node:
        word = node.surface
        hinshi = node.feature.split(",")
        if hinshi[0] == "名詞" and hinshi[1] != "代名詞" and not hiragana.fullmatch(word):
            keywords.append(word)
        node = node.next
    keywords = list(set(keywords))
    return keywords


def test_get_keywords():
    queries = ["私のご飯", 'あれとこれ', 'ももとすもも']
    answers = [["ご飯"], [], []]
    for q, a in zip(queries, answers):
        q = get_keywords(q)
        assert set(q) == set(a), f"{q},{a}"


def main():
    args = parse_args()
    logger.info(args)

    def tokenizer(text): return self.mecab.parse(text).split(
    ) if args.tokenizer == 'mecab' else ' '.join(list(text))

    filter = EmoticonFilter()
    cnt_dic = defaultdict(int)
    with open(args.input, 'r') as fin, open(args.output, 'w') as fout:
        for line in fin:
            try:
                line = json.loads(line)
                text = line["text"]
                # 顔文字を含むツイートは除外
                if filter._has_emoticon(text):
                    cnt_dic['emoji'] += 1
                    continue
                if not is_char_length(text):
                    logger.debug(f"this tweet is exceed 140 chars. \n{text}")
                    cnt_dic["more_than_140"] += 1
                    continue
                # user nameを削除
                text = filter._username_filter(text)
                # スペースなどを置換
                text = filter._normalization(text)

                keywords = list(map(tokenizer, get_keywords(text)))
                text = tokenizer(text)

                print(json.dumps(
                    {"keywords": keywords, "tweet": text}, ensure_ascii=False), file=fout)
            except:
                cnt_dic['error'] += 1
                logger.error(f"this data is skipped {line}")
    logger.info(
        f"emoji tweet: {cnt_dic['emoji']}\nmore than 140 tweet:{cnt_dic['more_than_140']}\nerror:{cnt_dic['error']}")


if __name__ == '__main__':
    main()

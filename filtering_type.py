import re
import string
import unicodedata

import MeCab


class Filter:
    def __init__(self):
        # self.mecab = MeCab.Tagger("-Owakati")
        # self.tokenizer = lambda text: self.mecab.parse(text).split()

        # regular expression
        self._normalization_reg = re.compile(r"([wWＷｗ。．.、，,・･…〜~\-！？!?])\1+")
        self._hashtag_ref = re.compile(f"#\S*")
        # test
        # self._filtering_test()

    def __call__(self, text: str) -> str:
        """Returns True if the condition is met, False otherwise"""
        text = self._normalization(text)
        text = self._filtering(text)
        return text

    def _normalization(self, text):
        text = self._normalization_reg.sub(r"\1", text)
        text = text.replace("　", " ")
        text = text.replace("\t", " ")
        text = text.replace("\n", " ")

        return text

    def _filtering(self, text):
        # hashtagを削除
        text = self._hashtag_ref.sub("", text)
        return text

    def _filtering_test(self):
        text1 = "ちょっと！！！？？？　なにやってんのＷＷＷ\tびっくりしたわ、、、、"
        queries = [text1]
        answers = ["ちょっと！？ なにやってんのＷ びっくりしたわ、"]
        for query, answer in zip(queries, answers):
            query = self._normalization(query)
            assert query == answer, f"{query}\n{answer}"


class EmoticonFilter(Filter):
    """顔文字を除去"""

    def __init__(self, normalization=True, max_hold=1000, joint=False):
        comment = "記号やアルファベットが3文字以上続く&2つ以上の種類から構成されるものは除去"
        super(EmoticonFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self._candidate_reg = re.compile(r"[\W_a-zA-Z]+")
        self._punctuation_reg = re.compile(r"[\W_]+")
        self._repeat = re.compile(r"([。．.、，,・･…〜~\-！？!?])\1+")
        self._alphabet = string.ascii_lowercase + string.ascii_uppercase
        self._parentheses = re.compile(r"\(.+?\)|（.+?）")
        self._japanese_names = ["CJK UNIFIED",
                                "HIRAGANA LETTER", "KATAKANA LETTER"]
        self._face_letter = ["T", "o", "O", "ロ", "口",
                             "ロ", "ﾛ", "つ", "っ", "灬", "ノ", "ﾉ", "c", "C"]
        self.filtering_test()

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for text in text_chain:
            if self._has_emoticon(text):
                return False
        return True

    def _has_emoticon(self, text):
        for m in self._candidate_reg.findall(text):
            m = m.strip(self._alphabet)
            m = m.strip()
            m = self._repeat.sub(r"\1", m)
            if self._punctuation_reg.search(m):
                if len(m) >= 3:
                    return True
        for m in self._parentheses.findall(text):
            if not self._has_japanese_char(m):
                return True

    def _has_japanese_char(self, text):
        for ch in text:
            try:
                name = unicodedata.name(ch)
                if any(n in name for n in self._japanese_names) and not any(c == ch for c in self._face_letter):
                    return True
            except:
                pass

    def filtering_test(self):
        text1 = "Twitterやってる？"
        text2 = "え〜〜〜！！！！！"
        text3 = "「LINEのIDとtwitterのアカウントが知りたい...」"
        text4 = "そういうことか．．．！"
        text5 = "^o^b"
        text6 = "おいしい( ′～‵)ŧ‹”ŧ‹”ŧ‹”ŧ‹” "
        text7 = "やったね(๑˃̵ᴗ˂̵)و "
        text8 = "(￣v￣)"
        text9 = "伯爵に食べられる前に逃げないと(ﾟдﾟ)！"
        text10 = "メレンゲ、いいですよ！きゅんとします（＾Ｏ＾）"
        text11 = "一緒に行こうよ٩('ω')و"
        text12 = "全然だよー(꒪ཀ꒪)"
        text13 = "PVの方は見たけど(๑꒪ㅁ꒪๑)"
        text14 = "そ、そんな！！(⁰▱⁰)"
        text15 = "(灬ºωº灬)"
        text16 = "^ ^"
        text17 = "(゜ロ゜)"
        text18 = "(ノД｀)"
        for text in [text1, text2, text3, text4]:
            assert not self._has_emoticon(text)
        for text in [text5, text6, text7, text8, text9, text10, text11, text12, text13, text14, text15, text16, text17,
                     text18]:
            assert self._has_emoticon(text)



import re
import string
import unicodedata

import MeCab


class ChainFilter(object):
    def __init__(self, comment=None, normalization=True, max_hold=1000, joint=False):
        # value
        self.comment = comment
        self.filtered_chains = []
        self._max_hold = max_hold
        self.mecab = MeCab.Tagger("-Owakati")
        self.tokenizer = lambda text: self.mecab.parse(text).split()

        # option
        self._can_normalize = normalization
        self._is_joint = joint

        # regular expression
        self._userid_reg = re.compile(r"@[a-zA-Z0-9_]{1,15}")
        self._head_userid_reg = re.compile(
            r"^@[a-zA-Z0-9_]{1,15} (.*?)$", re.DOTALL)
        self._url_reg = re.compile(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+")
        self._normalization_reg = re.compile(r"([wWＷｗ。．.、，,・･…〜~\-！？!?])\1+")

        # test
        self._filtering_test()

    def __call__(self, text_chain: [str]) -> [str]:
        """Returns True if the condition is met, False otherwise"""
        if self._is_joint:
            if self.is_pass(text_chain):
                return text_chain
        else:
            text_chain = [self._username_filter(text) for text in text_chain]
            if self.is_pass(text_chain):
                if self._can_normalize:
                    text_chain = [self._normalization(
                        text).strip("\n") for text in text_chain]
                else:
                    text_chain = [text.strip("\n") for text in text_chain]

                return text_chain

    def is_pass(self, text_chain: [str]) -> bool:
        """"Returns True if the condition is met, False otherwise"""
        raise NotImplementedError

    def _username_filter(self, text):
        m = self._head_userid_reg.search(text)
        if m:
            return self._username_filter(m.group(1))
        else:
            return text

    def _normalization(self, text):
        text = self._url_reg.sub("<URL>", text)
        text = self._normalization_reg.sub(r"\1", text)
        text = text.replace(" ", "")
        text = text.replace("　", "")
        text = text.replace("\t", "")
        text = text.replace("\n", "。")
        return text

    def _filtering_test(self):
        text1 = "@Test_2019NLP @amaretto01 @chair_69_BREAK フィルタリング成功した? https://github.com/"
        text2 = "@Reply \n猫かわいい\nhttp://kalkan.jp/catguide/img/article/09_img_main.jpg\n来世は猫になる"
        text3 = "@Reply_user2 明日の天気は？\n@Yahoo_weather"
        text4 = "@Reply_user3 ちょっと！！！？？？　なにやってんのＷＷＷ\tびっくりしたわ、、、、"
        queries = [text1, text2, text3, text4]
        answers = ["フィルタリング成功した?<URL>",
                   "。猫かわいい。<URL>。来世は猫になる",
                   "明日の天気は？。@Yahoo_weather",
                   "ちょっと！？なにやってんのＷびっくりしたわ、"]
        for query, answer in zip(queries, answers):
            query = self._username_filter(query)
            query = self._normalization(query)
            assert query == answer, f"{query}\n{answer}"


class NoFilter(ChainFilter):
    """No filter"""

    def __init__(self):
        comment = "No filter"
        super(NoFilter, self).__init__(comment)

    def is_pass(self, text_chain):
        return True


class CharLengthFilter(ChainFilter):
    """Filtering based on character length."""

    def __init__(self, max_len=30, min_len=5, normalization=True, max_hold=1000, joint=False):
        comment = "Filter for using only {} to {} letter reply chains".format(
            min_len, max_len)
        super(CharLengthFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self.max_len = max_len
        self.min_len = min_len

    def is_pass(self, text_chain):
        """"Returns True if the condition is met, False otherwise"""
        for text in text_chain:
            if self.max_len < len(text) or len(text) < self.min_len:
                return False
        return True


class InabaFilter(ChainFilter):
    """'14, 稲葉通将+, Twitterを用いた非タスク指向型対話システムのための発話候補文獲得"""

    def __init__(self, normalization=True, max_hold=1000, joint=False):
        comment = "1. URLを含むものは除去\n2. 単語が6~29\n3. ユーザ名を含まないもの"
        super(InabaFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self.max_len = 29
        self.min_len = 6
        self.filtering_test()

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for text in text_chain:
            len_token = len(self.tokenizer(text))
            if len_token > self.max_len or len_token < self.min_len:
                return False
            if self._has_url(text):
                return False
            if self._has_user_name(text):
                return False
        return True

    def _has_url(self, text):
        if self._url_reg.search(text):
            return True

    def _has_user_name(self, text):
        if self._userid_reg.search(text):
            return True

    def filtering_test(self):
        text1 = "明日は@test_USER2019と約束している"
        text2 = "この写真すごくいいよ http://kalkan.jp/catguide/img/article/09_img_main.jpg"
        text3 = "pythonとpytorchが大好き"
        text4 = "pythonとpytorchが大好きだ"
        text5 = "Twitterのユーザー名を選択しようとするとエラーメッセージが表示されるが、誰もそのユーザー名を使っていない場合。"
        text6 = "Twitterのユーザー名を選択しようとするとエラーメッセージが表示されるが、誰もそのユーザー名を使っていない場合"
        true_chain = [[text4], [text6], [text4, text6]]
        false_chain = [[text1], [text2], [text3], [
            text5], [text4, text2], [text6, text4, text1]]
        for chain in true_chain:
            assert self.is_pass(chain)
        for chain in false_chain:
            assert not self.is_pass(chain)


class BasicFilter(ChainFilter):
    """基本的なものを除去"""

    def __init__(self, normalization=True, max_hold=1000, joint=False):
        comment = """ <基本的なフィルタリング>
        1. URLを含むものは除去
        2. ユーザ名を含むものは除去
        3. # を含むものは除外
        4. 日本語を含まないものは除外
        """
        super(BasicFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self._japanese_names = ["CJK UNIFIED", "HIRAGANA", "KATAKANA"]
        self.filtering_test()

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for text in text_chain:
            if self._has_tag(text):
                return False
            if self._has_url(text):
                return False
            if self._has_user_name(text):
                return False
            if not self._is_japanese(text):
                return False
        return True

    @staticmethod
    def _has_tag(text):
        if "#" in text:
            return True

    def _is_japanese(self, text):
        for ch in text:
            try:
                name = unicodedata.name(ch)
                if any(n in name for n in self._japanese_names):
                    return True
            except:
                pass

    def _has_url(self, text):
        if self._url_reg.search(text):
            return True

    def _has_user_name(self, text):
        if self._userid_reg.search(text):
            return True

    def filtering_test(self):
        text1 = "Twitterのユーザー"
        text2 = "この写真すごくいいよ http://kalkan.jp/catguide/img/article/09_img_main.jpg"
        text3 = "明日は@test_USER2019と約束している"
        text4 = "温泉最高だった！\n# 熱海温泉"
        text5 = "I want to do a massive implementation."
        text6 = "めっちゃ暑いな @タイ"
        true_chain = [[text1], [text6], [text1, text6]]
        false_chain = [[text2], [text3], [text4], [text5], [
            text1, text2], [text6, text3], [text1, text6, text4]]
        for chain in true_chain:
            if not self.is_pass(chain):
                import ipdb
                ipdb.set_trace()
        for chain in false_chain:
            assert not self.is_pass(chain)


class WordLenFilter(ChainFilter):
    """単語の文字数でフィルタリング"""

    def __init__(self, min_len=6, max_len=29, normalization=True, max_hold=1000, joint=False):
        comment = "単語が{}~{}".format(min_len, max_len)
        super(WordLenFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self.min_len = min_len
        self.max_len = max_len
        self.filtering_test()

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for text in text_chain:
            len_token = len(self.tokenizer(text))
            if len_token > self.max_len or len_token < self.min_len:
                return False
        return True

    def filtering_test(self):
        text3 = "pythonとpytorchが大好き"
        text4 = "pythonとpytorchが大好きだ"
        text5 = "Twitterのユーザー名を選択しようとするとエラーメッセージが表示されるが、誰もそのユーザー名を使っていない場合。"
        text6 = "Twitterのユーザー名を選択しようとするとエラーメッセージが表示されるが、誰もそのユーザー名を使っていない場合"
        true_chain = [[text4, text6], [text4], [text6]]
        false_chain = [[text3], [text5], [text3, text4],
                       [text4, text5], [text4, text5, text6]]
        for chain in true_chain:
            assert self.is_pass(chain)
        for chain in false_chain:
            assert not self.is_pass(chain)


class EmoticonFilter(ChainFilter):
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


class JaccardFilter(ChainFilter):
    """Jaccard similarityを元にフィルタリング"""

    def __init__(self, threshold=0.5, normalization=True, max_hold=1000, joint=False):
        comment = "1. Jaccard similarity が 閾値 {} を超えたら除外\n" \
                  "2. len(set(words)) / len(words) が 0.5を下回ったら除外".format(str(threshold))
        super(JaccardFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self.threshold = threshold

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for i in range(len(text_chain)):
            words = self.tokenizer(text_chain[i])
            if len(set(words)) / len(words) < 0.5:
                return False
            if i != 0:
                set1 = set(self.tokenizer(text_chain[i - 1]))
                set2 = set(words)
                score = len(set1 & set2) / len(set1 | set2)
                if score >= self.threshold:
                    return False
        return True


class HeuristicFilter(ChainFilter):
    """Heuristic filter"""

    def __init__(self, normalization=True, max_hold=1000, joint=False):
        comment = "BasicFilter, EmoticonFilter, WordLenFilter, JaccardFilterを行うFiltering"
        super(HeuristicFilter, self).__init__(
            comment, normalization, max_hold, joint)
        self.basic = BasicFilter(joint=True)
        self.emoticon = EmoticonFilter(joint=True)
        self.wordlen = WordLenFilter(joint=True)
        self.jaccard = JaccardFilter(joint=True)
        self.filters = [self.basic, self.emoticon, self.wordlen, self.jaccard]

    def is_pass(self, text_chain: [str]):
        """"Returns True if the condition is met, False otherwise"""
        for filtering in self.filters:
            text_chain = filtering(text_chain)
            if not text_chain:
                if len(self.filtered_chains) < self._max_hold:
                    self.filtered_chains.append(
                        [filtering.__class__.__name__, text_chain])
                break
        if text_chain is not None:
            return True
        else:
            return False

# viral_tweet_generation

seq2seq×ツイッターデータを活用し，バズるツイートを生成するモデルを作成する

## 目次
- ツイートを収集する
- ツイートからキーワードを抽出
- ツイートをseq2seqの入出力に整形する
- fairseqで学習する
- 結果をまとめる

## ツイートを収集する
Twitterのデータは`/home/work/data/twitter_crawl_daily`に置いてある．

`extract_viral_tweet.sh`を実行するとTwitterデータを収集できる．使い方は

```Bash
bash extract_viral_tweet.sh [save directory] [year] [month]
```
という感じ．`bash extract_viral_tweet.sh ~/ 2019 10`なら，ホームディレクトリに2019年10月のデータから500いいね1リツイート以上のツイートを収集したjsonlファイルが作られる．


- [ ] このコードを用いて2018年10月〜2020年2月までのツイートを収集する
  - もしかしたらtmuxについて知らないとダメかも？


## ツイートからキーワードを抽出
収集されたデータからseq2seqの入力となるキーワードを取得する．キーワードはmecabでtokenizeし，名詞と判定されたもののうち，ひらがなのみで構成されたものを除外したものとか？



## ツイートをseq2seqの入出力に整形する
- [ ] ツイートをトークナイズする
  - 文字区切り，単語区切り，サブワード etc...
  - ツイッターの場合はきれいな文法じゃないのでsentence pieceを使用するのがいいかも
- [ ] sourceとtargetに分割する
  - target : `春 [SEP] 雪`
  - source : `春　なのに　雪　降っ　て　ん　じゃん`


## seq2seqを学習する
[fairseq](https://github.com/pytorch/fairseq)を使用する．

``` Bash
pip install fairseq
pip install tensorboard
pip install tensorboardX
```


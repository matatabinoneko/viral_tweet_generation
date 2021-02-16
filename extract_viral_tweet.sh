#!/bin/bash
# ツイッターデータを収集するためのスクリプト


SAVE_DIR=${1}
year=${2}
month=${3}

f_c=500
r_c=1


zcat /home/work/data/twitter_crawl_daily/tweets-${year}${month}*-json.txt.gz \
    |python extract_viral_tweet.py --exclude_verified --exclude_urls \
        --favorite_count ${f_c} \
        --retweet_count ${r_c} \
        --output ${SAVE_DIR}/tweets-${year}${month}-fc_${f_c}-rc_${r_c}.jsonl

    

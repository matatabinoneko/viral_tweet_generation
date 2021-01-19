#!/bin/bash

SAVE_DIR=${1}
friend_ratio=( 10000 )
favorite_count=( 10000   )
retweet_count=( 10000  )
date_list=( 202012* )

for f_r in ${friend_ratio[@]}
do
    for f_c in ${favorite_count[@]}
    do
        for r_c in ${retweet_count[@]}
        do
            for d in ${date_list[@]}
            do
                zcat /home/work/data/twitter_crawl_daily/tweets-${d}-json.txt.gz \
                |python extract_viral_tweet.py --exclude_verified --exclude_urls \
                    --friend_ratio ${f_r} \
                    --favorite_count ${f_c} \
                    --retweet_count ${r_c} \
                > ${SAVE_DIR}/tweets-${d}-fr_${f_r}-fc_${f_c}-rc_${r_c}.jsonl &
            done
        done
    done
done
    

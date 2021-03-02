### preprocess ###
. setting.sh

mkdir -p ${PROCESS_DIR}

fairseq-preprocess --source-lang source --target-lang target \
    --trainpref ${DECODE_FILE}/train \
    --validpref ${DECODE_FILE}/dev \
    --testpref ${DECODE_FILE}/test \
    --destdir ${PROCESS_DIR} \
    --workers 12

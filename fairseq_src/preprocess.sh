### preprocess ###
. setting.sh

mkdir -p ${PROCESS_DIR}

fairseq-preprocess --source-lang source --target-lang target \
    --trainpref ${DECODE_FILE}/train \
    --validpref ${DECODE_FILE}/dev \
    --destdir ${PROCESS_DIR} \
    --workers 5

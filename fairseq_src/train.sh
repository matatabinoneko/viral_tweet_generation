### training script ###
. setting.sh

mkdir -p ${MODEL_DIR}
mkdir -p ${LOG_DIR}

CUDA_VISIBLE_DEVICES=${GPU} fairseq-train ${DATA_DIR} \
	-s source -t target \
	--arch lstm \
	--encoder-layers 4 \
	--decoder-layers 4 \
	--encoder-bidirectional \
	--criterion cross_entropy \
	--optimizer adam \
	--adam-betas '(0.9, 0.98)' \
	--lr 0.0005 \
	--lr-scheduler inverse_sqrt \
	--min-lr 1e-09 \
	--warmup-init-lr 1e-07 \
	--warmup-updates 4000 \
	--dropout 0.3 \
	--weight-decay 0.0001 \
	--dataset-impl 'mmap' \
	--max-tokens 4000 \
	--max-update ${MAX_UPDATE} \
	--keep-last-epochs 3 \
	--keep-interval-updates 10 \
	--save-interval-updates 500 \
	--save-dir ${MODEL_DIR} \
	--tensorboard-logdir ${LOG_DIR} \
	--log-format simple \
	--seed ${SEED} | tee ${MODEL_DIR}/log.txt

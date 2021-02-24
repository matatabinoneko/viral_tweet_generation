### interactive script ###
. setting.sh

#CUDA_VISIBLE_DEVICES=${GPU} fairseq-interactive ${DATA_DIR} \
CUDA_VISIBLE_DEVICES=${GPU} python src/interactive-for-japanese.py ${DATA_DIR} \
	--path ${MODEL_DIR}/checkpoint_best.pt \
	--source-lang source \
  --target-lang target \
	--nbest 5

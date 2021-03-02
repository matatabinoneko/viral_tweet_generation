export DIR=/work01/stepqi2020/fairseq_model/improve01
# preprocess
export PROCESS_DIR="${DIR}/preprocessed"
export DECODE_FILE="${DIR}/tokenized"

# training
export GPU=0
export MODEL_DIR="${DIR}/models"
export LOG_DIR="${DIR}/logs"
export DATA_DIR=${PROCESS_DIR}
export MAX_UPDATE=100000
export SEED=1234

# interactive
# export TRAINED_DIR=/work01/club-imi-taiwa-2019/fairseq_data/tutorial
#export MODEL_DIR=${TRAINED_DIR}
#export DATA_DIR=${TRAINED_DIR}

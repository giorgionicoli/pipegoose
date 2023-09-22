# RPC global worker name
WORKER_NAME = "RPC_GLOBAL_WORKER_{}"


CHECKPOINT_WEIGHTS_NAME = "pytorch_model_tp_{}_pp_{}.bin"
CHECKPOINT_PATH_NAME = "./"


# PIPELINE PARALLELISM


# NOTE: the minimum number of cocurrent worker threads that execute jobs
# in the background of pipeline parallelism
PIPELINE_MIN_WORKERS = 3
PIPELINE_MAX_WORKERS = 4

JOB_KEY_LENGTH = 15

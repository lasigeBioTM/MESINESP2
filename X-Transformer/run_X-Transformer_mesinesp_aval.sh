#!/bin/bash
#Executes the X-BERT algorithm to classify the 'unlabeled' test set to given by the BioASQ competitions.
#This script was developed exclusively for the MESINESP task and only using the bert-base-multilingual-cased model.
#
#HOW TO RUN:
# ./run_X-Transformer_mesinesp_aval.sh DATASET_FOLDER_NAME bert-base-multilingual-cased


DATASET=$1
MODEL=$2

CPUS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
#GPUS=0,1,2,3

#Creates necessary dataset dirs
#mkdir  -p datasets/${DATASET}_Aval/
#mkdir  -p datasets/${DATASET}_Aval/mapping/

#Moves the training and test files to the X-Transformer newly created dataset dirs
#cd ..

#cp preprocessing/processed_data/${DATASET}/train.txt X-Transformer/datasets/${DATASET}_Aval/train.txt
#cp preprocessing/processed_data/${DATASET}/train_raw_labels.txt X-Transformer/datasets/${DATASET}_Aval/train_raw_labels.txt
#cp preprocessing/processed_data/${DATASET}/train_raw_texts.txt X-Transformer/datasets/${DATASET}_Aval/train_raw_texts.txt
#cp preprocessing/processed_data/${DATASET}/test.txt X-Transformer/datasets/${DATASET}_Aval/test.txt
#cp preprocessing/processed_data/${DATASET}/test_raw_labels.txt X-Transformer/datasets/${DATASET}_Aval/test_raw_labels.txt
#cp preprocessing/processed_data/${DATASET}/test_raw_texts.txt X-Transformer/datasets/${DATASET}_Aval/test_raw_texts.txt

#cp preprocessing/processed_data/${DATASET}/label_vocab.txt X-Transformer/datasets/${DATASET}_Aval/label_vocab.txt
#cp preprocessing/processed_data/${DATASET}/label_map.txt X-Transformer/datasets/${DATASET}_Aval/mapping/label_map.txt

#Now, it will execute the necessary X-Transformer steps
#cd X-Transformer

#File vectorizer. Converts to libsvm format
echo '>>>> CONVERTING TO LIBSVM <<<<'
taskset -c ${CPUS}  python -m datasets.new_preprocess_tfidf -i datasets/${DATASET}

echo '>>>> LABEL EMBEDING AND DATA MATRICES <<<<'
cd datasets
python proc_data.py --dataset ${DATASET}

#python label_embedding.py -d ${DATASET}_Aval -e pifa
python label_embedding.py -d ${DATASET} -e pifa

cd ..

echo '>>>> INDEXER <<<<'
#mkdir -p save_models/${DATASET}_Aval/pifa-a5-s0/indexer
mkdir -p save_models/${DATASET}/pifa-a5-s0/indexer

python -m xbert.indexer \
	-i datasets/${DATASET}/L.pifa.npz \
	-o save_models/${DATASET}/pifa-a5-s0/indexer \
	-d 6 --algo 5 --seed 0 --max-iter 20

echo '>>>> PREPROCESS <<<<'
OUTPUT_DIR=save_models/${DATASET}/pifa-a5-s0
mkdir -p ${OUTPUT_DIR}/data-bin-cased

python -m xbert.preprocess \
	-m bert \
	-n bert-base-multilingual-cased \
	-i datasets/${DATASET} \
	-c ${OUTPUT_DIR}/indexer/code.npz \
	-o ${OUTPUT_DIR}/data-bin-cased

echo '>>>> RANKER TRAINING <<<<'
mkdir -p ${OUTPUT_DIR}/ranker_${DATASET}_${MODEL}

taskset -c ${CPUS} python -m xbert.ranker train \
  -x1 datasets/${DATASET}/X.trn.npz \
  -x2 save_models/${DATASET}/pifa-a5-s0/matcher/${MODEL}/trn_embeddings.npy \
  -y datasets/${DATASET}/Y.trn.npz \
  -z save_models/${DATASET}/pifa-a5-s0/matcher/${MODEL}/C_trn_pred.npz \
  -c save_models/${DATASET}/pifa-a5-s0/indexer/code.npz \
  -o ${OUTPUT_DIR}/ranker_${DATASET}_${MODEL} -t 0.01 \
  -f 0 -ns 0 --mode ranker

echo '>>>> RANKER PREDICTION <<<<'
taskset -c ${CPUS} python -m xbert.ranker predict \
  -m ${OUTPUT_DIR}/ranker_${DATASET}_${MODEL} \
  -o ${OUTPUT_DIR}/ranker_${DATASET}_${MODEL}/tst_${num}.pred.npz \
  -x1 datasets/${DATASET}/X.tst.npz \
  -x2 save_models/${DATASET}/pifa-a5-s0/matcher/${MODEL}/tst_embeddings.npy \
  -y datasets/${DATASET}/Y.tst.npz \
  -z save_models/${DATASET}/pifa-a5-s0/matcher/${MODEL}/C_tst_pred.npz -t noop \
  -f 0 -k 20

echo '>>>> END <<<<'
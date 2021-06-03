#!/bin/bash
#Executes the code to process the data given by MESINESP and stores it in the format required for X-Transformer.
#This script requires the name of the dataset to preprocess (scientific_literature, clinical_trials or patents) 
#a threshold determining the fraction of entities to include in the processed dataset (1.0, 0.75, 0.5, 0.25).


############## Args ##############
DATASET=$1
THRESHOLD=$2 # 100%, 75%, 50%, and 25% top entities to consider


############## pre-processing ##############
out_dir="./processed_data/${DATASET}_${THRESHOLD}/"
mkdir -p $out_dir

python pre_process_dataset.py $DATASET $THRESHOLD $out_dir

############## Moving the created files ##############

#Creates the directory for the BioASQ in the X-Transformer datasets folder
mkdir -p ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/
mkdir -p ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/mapping

#Then, copies the files required by X-Transformer to the directory
cp ${out_dir}label_map.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/mapping/label_map.txt
cp ${out_dir}label_vocab.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/label_vocab.txt

cp ${out_dir}train.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/train.txt
cp ${out_dir}train_raw_labels.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/train_raw_labels.txt
cp ${out_dir}train_raw_texts.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/train_raw_texts.txt

cp ${out_dir}dev.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/dev.txt
cp ${out_dir}dev_raw_labels.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/dev_raw_labels.txt
cp ${out_dir}dev_raw_texts.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/dev_raw_texts.txt

cp ${out_dir}test.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/test.txt
cp ${out_dir}test_raw_labels.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/test_raw_labels.txt
cp ${out_dir}test_raw_texts.txt ../X-Transformer/datasets/${DATASET}_${THRESHOLD}/test_raw_texts.txt
	
echo "Input files moved to dir ../X-Transformer/datasets/${DATASET}_${THRESHOLD}"



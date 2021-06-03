# -*- coding: utf-8 -*-
"""
Processes the predictions made by the X-Transformer model and stores them in 
a json file with the required format by the MESINESP2 competition. 

@author: André Neves
@modified by: Pedro Ruas
"""
import os
import json
import argparse
import logging
import numpy as np
import text_files_utils as tfu
from pandas.io.json import json_normalize


def main(args):
    vocab_path = args.vocab_path
    npz_file = args.npz_file
    out_path = args.output_path
    json_path = args.json_path
    competition = args.competition
        
    if not os.path.exists(out_path): 
        print('Creating path %s' % out_path)
        os.mkdir(out_path)

    with open(json_path, 'r', encoding='utf-8') as bioasq_input:
        data = json.load(bioasq_input)
        
        if competition == 'mesinesp': 
            df_bioasq = json_normalize(data['articles'])
            l_pmid = df_bioasq['id'].values.tolist()
    
    df_size = len(df_bioasq)
    
    with open(vocab_path + 'test.txt', 'r', encoding='utf-8') as ftest:
        test_lines = ftest.readlines()
        
    with open(vocab_path + 'label_correspondence.txt', 'r', encoding='utf-8') as flabels:
        labels = flabels.readlines()    
    
    #Stores test file labels
    print('processing labels...')
    l_test_labs = []
    
    for i in range(len(test_lines)):
        spli = test_lines[i].split('\t')
        l_test_labs.append(spli[0].split(','))
        test_lines[i] = spli[1]
        
    #Remove possible duplicates
    for i in range(len(l_test_labs)):
        l_test_labs[i] = list(dict.fromkeys(l_test_labs[i]))
            
    #Converts the labels of each article into int and sorts them inside the list
    l_aux = []
    
    for i in range(len(l_test_labs)):
    
        for j in l_test_labs[i]:
            l_aux.append(int(j))
    
        l_test_labs[i] = l_aux
        l_test_labs[i].sort()
        l_aux = []
    
    #Creates dictionary with the correspondence between the X-TRANSFORMER labels and the 
    #DeCS labels
    dict_labels, dict_labels_rev = {}, {}
    
    for i in range(len(labels)):
        dict_labels[labels[i].split('=')[0]] = (labels[i].split('=')[1], 
                   labels[i].split('=')[2].replace('\n',''))
        dict_labels_rev[labels[i].split('=')[1]] = (labels[i].split('=')[0], 
               labels[i].split('=')[2].replace('\n',''))
    
    #loads npz prediction file and stores the predictions in list. 
    data = np.load(npz_file)
    
    count = 0
    l_probs, l_aux = [], []
    
    for i, j in zip(data['indices'], data['data']):
        
        if count == 19: #number of predictions made by X-BERT/X-Transformer for each article
            l_probs.append(l_aux)
            l_aux = []
            count = 0
        
        else:
            l_aux.append((i,j))
            count += 1
    
    #Writes the predictions with a confidence value >= to the confidence threshold
    print('Writing files...')

    tfu.write_json_output(out_path, l_probs, l_pmid, dict_labels, 'baseline', competition)
    
  
#Begin
parser = argparse.ArgumentParser()

#Required parameters
parser.add_argument('-npz', '--npz-file', type=str, required=True,
                    help='Path to the .npz file containing the X-BERT/X-Transformer predictions.')
parser.add_argument('-i1', '--vocab-path', type=str, required=True,
                    help='Path to the folder that contains the label_correspondence file and \
                    the .txt file for which the predictions were made')
parser.add_argument('-i2', '--json-path', type=str, required=True,
                    help='Path to the .json file given by BioASQ/MESINESP containing the articles \
                    to make the predictions')
parser.add_argument('-o', '--output-path', type=str, required=True,
                    help='Path to the directory that will contain the output prediction files')
parser.add_argument('-c', '--competition', type=str, required=True,
                    help='Name of the competition. Valid values: \'mesinesp\' or \'bioasq\'.')

args = parser.parse_args()
print(args)
main(args)
print('Finished processing')
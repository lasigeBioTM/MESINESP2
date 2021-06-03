# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 18:03:05 2020

@author: André Neves
@modified by: Pedro Ruas
"""

from datetime import date
import json
import sys
sys.path.append("./")


def gen_vocab(terms, codes, out_path):
    
    l_vocab, l_corr = list(), list()
    
    for i in range(len(terms)):
        l_vocab.append(str(i) + '\t' + terms[i].lower().replace(' ', '_'))
        l_corr.append(str(i) + '=' + codes[i] + '=' + terms[i])
    
    out_path += "/"
    
    #Label_vocab:
    #Label number  KB term    
    with open(out_path + 'label_vocab.txt', 'w', encoding='utf-8') as f:
        for i in l_vocab:
            f.write('%s\n' % i)

    #Label_correspondence:
    #Label=KB Code=KB term          
    with open(out_path + 'label_correspondence.txt', 'w', encoding='utf-8') as f:
        for i in l_corr:
            f.write('%s\n' % i)
            
    #Label_map:
    #KB terms -> sorted alphabetical
    with open(out_path + 'label_map.txt', 'w', encoding='utf-8') as f:
        terms.sort()
        for i in range(len(terms)):
            f.write('%s\n' % terms[i].lower().replace(' ', '_'))
    
    #Creates a dict to be returned with the label correspondence
    #Dict Format = {DeCS Code: (label number, DeCS Term)}
    dict_corr = dict()
    
    for i in range(len(l_corr)):
        dict_corr[l_corr[i].split('=')[1]] = (l_corr[i].split('=')[0], 
                   l_corr[i].split('=')[2])
    
    return dict_corr
            
  
def convert_labels(l_labels, dict_labels):
    
    l_labels_name = list()
    
    for i in range(len(l_labels)):
        #print(l_labels[i]) #DEBUG
        l_aux = []
        
        for l in range(len(l_labels[i])):
            #print(l_labels[i][l]) #DEBUG
            l_aux.append(dict_labels.get(l_labels[i][l])[1].lower().replace(' ', '_'))
            l_labels[i][l] = dict_labels.get(l_labels[i][l])[0]
        
        l_labels_name.append(l_aux)
    
    return l_labels, l_labels_name


def output_processed_files(stemmed_text, kb_names, kb_codes, subset, out_dir):
    """Outputs files associated with given subset that will be the input of the classification algorithm

    :param: stemmed_text, includes the stemmed texts for all docs in given subset
    :type: dict
    :param kb_names: DeCS terms associated with the docs (i.e. gold labels)
    :type kb_names: list
    :param kb_codes: DeCS codes associated with the docs (i.e. gold labels)
    :type kb_codes: list
    :param subset: 'train', 'dev', 'test
    :type subset: str
    :param out_dir: output dir of processed files
    :type out_dir: str
    :return: the files: "<subset>.txt", "<subset>_raw_texts.txt", "<subset>_raw_labels.txt" in out_dir dir
    """
  
    #Outputs file with format: Code 1 int, Code 2 int, ... \t stemmed text
    out_subset_filepath =  out_dir + "/" + subset + ".txt"
    
    with open(out_subset_filepath, 'w', encoding='utf-8') as out_subset:
        
        for i in range(len(stemmed_text)):
            str_decs = str(kb_codes[i]).replace('[', '').replace(']', '').replace(' ', '').replace('\'', '')
            str_final = str_decs + '\t' + stemmed_text[i]
            out_subset.write('%s\n' % str_final)

    #Outputs raw texts and raw labels 
    out_raw_text_filepath = out_dir + "/" + subset + '_raw_texts.txt'
    
    with open(out_raw_text_filepath, 'w', encoding='utf-8') as out_text:
    
        for i in range(len(stemmed_text)):
            out_text.write('%s\n' % stemmed_text[i])
    
    out_raw_labels_filepath = out_dir + "/" + subset + '_raw_labels.txt'
    
    with open(out_raw_labels_filepath, 'w', encoding='utf-8') as out_labels:
    
        for i in range(len(kb_names)):
            str_final = ''
    
            for j in range(len(kb_names[i])):
                str_final = str_final + kb_names[i][j] + ' '
    
            out_labels.write('%s\n' % str_final)

                        
def write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, eval_type, competition):
    
    dict_json = {"documents":[]}
    
    for i, j in zip(l_pred_labs, l_pmid):
        
        if competition == 'mesinesp':
            dict_aux = {"labels":[], "id":''} # For MESINESP
        
        for z in i:  
            term_int = str(z[0])
            decs_term = dict_labels[term_int]
            dict_aux["labels"].append(decs_term[0])
        
        if competition == 'mesinesp':
            dict_aux["id"] = j
        
        else:
            dict_aux["pmid"] = j
            
        dict_json["documents"].append(dict_aux)
        
    with open(out_path + competition + '_prediction_' + eval_type + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(dict_json, outfile, ensure_ascii=False, indent=4)


def build_test_set_clinical_trials(threshold):
    """Builds a new test set by concatenating the content of several files:
        - 'train_2.txt', 'dev.txt', and 'test.txt' into 'test.txt'
        - 'train_2_raw_labels.txt', 'dev_raw_labels.txt', and 'test_raw_labels.txt' into 'test_raw_labels.txt'
        - 'train_2_raw_text.txt', 'dev_raw_text.txt', 'test_raw_text.txt' into 'test_raw_text.txt'
    
    Only run once after the output from the script 'prepare_input.sh' 
    is on the "processed_data/clinical_trials_{threshold}" dir
    """

    def read_file(filepath):
        
        with open(filepath, 'r') as input_file:
            data = input_file.read()

        return data

    def output_file(filepath, data):

        with open(filepath, 'w') as out_file:
            out_file.write(data)
            out_file.close()

    dataset_dir = "processed_data/clinical_trials_{}/".format(threshold) 
    
    ## Build 'test.txt'
    train_2_data = read_file(dataset_dir + "train_2.txt")
    dev_data = read_file(dataset_dir + "dev.txt")
    test_data = read_file(dataset_dir + "test.txt")
    
    #DEBUG
    print("len train_2_data:", str(len(train_2_data.split("\n"))), \
            "len dev_data:", str(len(dev_data.split("\n"))), \
            "len test_data:", str(len(test_data.split("\n")))   )

    test_data += train_2_data + dev_data
    output_file(dataset_dir + "test.txt", test_data)

    ## Build 'test_raw_labels.txt'
    train_2_labels_data = read_file(dataset_dir + "train_2_raw_labels.txt")
    dev_labels_data = read_file(dataset_dir + "dev_raw_labels.txt")
    test_labels_data = read_file(dataset_dir + "test_raw_labels.txt")
    
    #DEBUG
    print("len train_2_labels_data:", str(len(train_2_labels_data.split("\n"))), \
            "len dev_labels_data:", str(len(dev_labels_data.split("\n"))), \
            "len test_labels_data:", str(len(test_labels_data.split("\n")))   )
    
    test_labels_data += train_2_labels_data + dev_labels_data
    output_file(dataset_dir + "test_raw_labels.txt", test_labels_data)

    ## Build 'test_raw_text.txt'
    train_2_text_data = read_file(dataset_dir + "train_2_raw_texts.txt")
    dev_text_data = read_file(dataset_dir + "dev_raw_texts.txt")
    test_text_data = read_file(dataset_dir + "test_raw_texts.txt")
    
    #DEBUG
    print("len train_2_text_data:", str(len(train_2_text_data.split("\n"))), \
            "len dev_text_data:", str(len(dev_text_data.split("\n"))), \
            "len test_text_data:", str(len(test_text_data.split("\n")))   )

    test_text_data += train_2_text_data + dev_text_data
    output_file(dataset_dir + "test_raw_texts.txt", test_text_data)

   

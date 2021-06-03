import json
import logging
import os
import pandas as pd
import stem_utils as su
import sys
import text_files_utils as tfu
sys.path.append("./")


def extract_info_from_table(subset, table, dict_labels):
    """Imports content of given subset json file into several lists

    :param subset: "train", "dev" or "test"
    :type subset: str()
    :param table: includes the subset in table format
    :type table: DataFrame
    :param dict_labels: has format {DeCS Code: (label number, DeCS Term)}
    :type dict_labels: dict
    :return: four corresponding lists storing the subset info, doc_ids, titles, kb_codes, kb_names
    :rtype: list, list, list, list
    """    

    doc_ids = table['id'].values.tolist()
    titles = table['title'].values.tolist()

    if subset == "test": # Test set is unlabeled, does not have decs codes, we need to add a placeholder to each doc
        kb_codes = [0] * len(titles)
        kb_names = [str(0)] * len(titles)

    else:
        kb_codes = table['decsCodes'].values.tolist()
        kb_codes, kb_names = tfu.convert_labels(kb_codes, dict_labels)
  
    return doc_ids, titles, kb_codes, kb_names
    

def get_kb_info(out_dir):
    """Import DeCS2020.tsv file into two dicts, code_to_term and dict_labels"""

    kb_file = "retrieved_data/DeCS2020.tsv"

    # Checks if input files/paths exist
    assert os.path.exists(kb_file), "KB file/path doesn't exist"
    
    if not os.path.exists(out_dir): # Create output dir if does not exist
        print('- Creating path %s' % out_dir)
        os.mkdir(out_dir)
    
    # Reads KB file (.tsv format) and stores the KB terms and the respective KB Code in lists    
    print('Reading KB file \'%s\' ...' % kb_file)
    kb_data = pd.read_csv(kb_file, sep='\t')
    
    l_terms = kb_data['descriptor_name'].astype(str).values.tolist()
    l_codes = kb_data['descriptor_id'].astype(str).values.tolist()
    
    code_to_term = dict()

    for i, term in enumerate(l_terms):
        code = l_codes[i]
        code_to_term[code] = term
   
    # Generates vocab and label_correspondence files, and returns dict with label correspondence
    dict_labels = tfu.gen_vocab(l_terms, l_codes, out_dir)

    return code_to_term, dict_labels


def stem_subset_append_entities(subset_text, subset, extracted_entities, docs_dict_subset, code_to_term):
    """Stems all docs in given subset and append the extracted entities to the end of each doc text

    :param subset_text: includes all the texts of the docs belonging to specified subset
    :type subset_text: list
    :param subset: 'train', 'dev', 'test'
    :type subset: str
    :param extracted_entities: has format {doc_count: [[entity_str, begin, end, decs_id]}
    :type extracted_entities: dict
    :param docs_dict_subset: has format {doc_id: doc_count}, stores the relative position of each doc)
    :type docs_dict_subset: dict
    :param code_to_term: has format {decs_code: decs_term}
    :type code_to_term: dict
    :return: stemmed_text, includes the stemmed texts for all docs in given subset
    :rtype: dict
    """

    print('- Stemming %s titles' % subset)

    # Generate Stemmer
    su.check_nltk_punkt()
    stemmer = su.set_stemmer('spanish')
    stemmed_text = su.list_stemming(subset_text, stemmer) #Stem the titles in current subset
 
    print("- Appending extracted entities to %s titles" % subset)

    for doc in range(len(stemmed_text)):
       
        entities = list()

        if doc in docs_dict_subset.keys() and (subset == "dev" or subset == "test"):        
            ee_doc_count = docs_dict_subset[doc]
            entities = extracted_entities[str(ee_doc_count)]
        
        elif doc in extracted_entities.keys() and subset == "train":
            entities = extracted_entities[str(doc)]
        
        entities_str = str()

        if len(entities) >= 1:      # If at least 1 entity was recognized in the respective abstracts append it, 
            entities_added = list() # otherwise keep original title
                            
            for entity in entities:
                                
                if len(entity[3]) > 4: # Ignore root concepts such as "C", "D", or "DeCS"

                    if entity[3] not in entities_added and entity[3] in code_to_term.keys():
                        concept_str = code_to_term[entity[3]]
                        entities_str += concept_str + " "
                        entities_added.append(entity[3])

            entities_str = entities_str[:-1]
            stemmed_text[doc] = stemmed_text[doc] + " " + entities_str
    
    return stemmed_text


def get_extracted_entities(extracted_entities_filepath, subset, dataset):
    """Retrieve the ouput output of the named entity linking module into dicts

    :param extracted_entities_filepath: path for the file containing the output of the named entity linking module
    :type extracted_entities_filepath: str
    :param subset: 'train', 'dev', 'test'
    :type subset: str
    :param dataset: 'scientific_literature', 'clinical_trials', 'patents'
    :type dataset: str
    :return: extracted_entities (with format {doc_count: [[entity_str, begin, end, mesh_id]}), 
            docs_dict (with format {doc_id: doc_count}, stores the relative position of each doc)
    :rtype: dict, dict
    """

    with open(extracted_entities_filepath, 'r', encoding='utf-8') as extracted_entities_file:
        extracted_entities = json.load(extracted_entities_file) 

    original_extracted_entities = "extracted_entities/Additional data"

    if dataset == "scientific_literature":
            original_extracted_entities += "/Subtrack3-Scientific_Literature/entities_subtrack1_" + subset + ".json"
    
    elif dataset == "clinical_trials":
            original_extracted_entities += "/Subtrack2-Clinical_Trials/entities_subtrack2_" + subset + ".json"
    
    docs_dict = dict()
    
    with open(original_extracted_entities, "r") as original_entities_file:
        original_entities = json.load(original_entities_file)

    doc_count = 0

    for doc in original_entities['articles']:
            
        if str(doc_count) in extracted_entities.keys():
            doc_id = doc['id']  
            docs_dict[doc_id] = doc_count

        doc_count += 1

    return extracted_entities, docs_dict


def preprocess_dataset(dataset, threshold, out_dir):
    """Generate processed files of given dataset for input of the classification algorithm

    :param dataset: 'scientific_literature', 'clinical_trials', 'patents'
    :type dataset: str
    :param threshold: semantic similarity filter, has values '1.0', '0.75', '0.5', '0.25'
    :type threshold: str
    :param out_dir: output dir of processed files
    :type out_dir: str
    :return: processed dataset files to be the input of the classification algorithm
    """

    dataset_dir = str()
    train_filepath = str()
    extracted_entities_dir = "extracted_entities/"

    if dataset == "scientific_literature":
        dataset_dir =  "retrieved_data/Subtrack1-Scientific_Literature/"
        train_filepath = dataset_dir + "Train/training_set_subtrack1_all.json"
        extracted_entities_dir += "Subtrack1-Scientific_Literature/"
        dev_filepath = dataset_dir + "Development/development_set_subtrack1.json"
        test_filepath = dataset_dir + "Test/test_set_subtrack1.json"
    
    elif dataset == "clinical_trials":
        dataset_dir =  "retrieved_data/Subtrack2-Clinical_Trials/"
        train_filepath = dataset_dir + "Train/training_set_subtrack2.json"
        extracted_entities_dir += "Subtrack2-Clinical_Trials/"
        dev_filepath = dataset_dir + "Development/development_set_subtrack2.json"
        test_filepath = dataset_dir + "Test/test_set_subtrack2.json"

    elif dataset == "patents": # The dataset 'patents' does not have a training set: we use the training set from
        dataset_dir =  "retrieved_data/Subtrack3-Patents/"
        train_filepath = "retrieved_data/Subtrack1-Scientific_Literature/Train/training_set_subtrack1_all.json"
        extracted_entities_dir += "Subtrack3-Patents/"
        dev_filepath = dataset_dir + "Development/development_set_subtrack3.json"
        test_filepath = dataset_dir + "Test/test_set_subtrack3.json"
        
    code_to_term, dict_labels = get_kb_info(out_dir)

    for subset in ["train", "dev", "test"]:  
        print("processing {} set...".format(subset))         
        subset_filepath = str()

        if subset == "train":
            subset_filepath = train_filepath
        
        elif subset == "dev":
            subset_filepath = dev_filepath
        
        elif subset == "test":
            subset_filepath = test_filepath

        with open(subset_filepath, 'r', encoding='utf-8') as train_file:
            subset_data = json.load(train_file)
            subset_table = pd.json_normalize(subset_data["articles"])
            
        subset_doc_ids, subset_titles, subset_kb_codes, subset_kb_names = extract_info_from_table(subset, subset_table, dict_labels)            
        
        extracted_entities_filepath = extracted_entities_dir + dataset + "_" + subset + "_" + threshold + ".json"
        subset_extracted_entities, docs_dict = get_extracted_entities(extracted_entities_filepath, subset, dataset)
        
        stemmed_text_subset = stem_subset_append_entities(subset_titles, subset, subset_extracted_entities, docs_dict, code_to_term)
        
        print('- Outputting %s processed files' % subset)
        tfu.output_processed_files(stemmed_text_subset, subset_kb_names, subset_kb_codes, subset, out_dir)

if __name__ == "__main__":
    dataset = sys.argv[1]
    threshold = sys.argv[2]
    out_dir = sys.argv[3]
    
    preprocess_dataset(dataset, threshold, out_dir)
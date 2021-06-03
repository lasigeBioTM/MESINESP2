import os
import xml.etree.ElementTree as ET
import sys
import json

sys.path.append("./")


def parse_ner_output(ic=True):
    """Get the annotations in the Additional_data files"""
    
    subtrack_number = sys.argv[-2]
    subtrack_set = sys.argv[-1]

    filenames = list()
    ner_dir = './evaluation/Additional_data/Subtrack' + subtrack_number + '/entities_subtrack' + subtrack_number + '_' + subtrack_set + '.json'

    if ic:
        evaluation = False
    else:
        evaluation = True
        
    annotations = dict()
    

    file = open(ner_dir,'r',encoding = 'utf-8')
    data = json.load(file)

    keys = list(data.keys())
    for key in keys:
        doc_id = key
        ner_output = data.get(doc_id)
        if len(ner_output) == 0:
            annotations[doc_id] = []
        for annotation in ner_output:

            if len(annotation) == 3:

                annotation_text = annotation[0]
                annotation_begin = annotation[1]
                annotation_end = annotation[2]
                annotation_data = (annotation_text, annotation_begin, annotation_end)

                if doc_id in annotations.keys():
                    current_values = annotations[doc_id]
                    current_values.append(annotation_data)
                    annotations[doc_id] = current_values
                                    
                else:
                    annotations[doc_id] = [annotation_data]

    return annotations







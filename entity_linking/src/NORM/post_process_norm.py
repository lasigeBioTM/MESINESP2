import os
import sys
import json
from annotations import parse_ner_output

sys.path.append("./")


def get_ppr_output(ont_number, model):
    """ Get the results outputted by the PPR algorithm into dict."""

    results_dict, results_file = dict(), str()
    
    with open("./tmp/norm_results/" + ont_number + "/ppr_ic_all_candidates") as results:
        data = results.read()
        results.close()
    
    doc_id = str()
    temp_dict = dict()
    line_count = int()
    
    split_results = data.split("======= ")

    def get_score(candidate):
        return candidate[1]

    for element in split_results:
        #print(element)

        if element != "" and element != "\n":
                
            if element[0] != "\n":
                doc_name = element.split(" =")[0]
                
            else:
                doc_data = element.split("\n")
                temp_dict = dict()

                if len(doc_data) and doc_data[0] == "" and doc_data[1] == "" and doc_data[2] == "":
                    continue

                else:
                    for element_2 in doc_data:

                        if element_2 != "" and element_2 != "==============================================":
                            if element_2[1] == 'null\t':
                                pass

                            if element_2[0] == "=":
                                if element_2 == '======':
                                    element_2 = element_2 +  ')=>NaN (in=0  deg=0)  (fb=Infinity)'
                                if element_2[1] == '=':
                                    element_2 = element_2 +  ')=>NaN (in=0  deg=0)  (fb=Infinity)'

                                else:
                                    entity_text = element_2.split("= ")[1].split("\t")[0]
                                    candidate_count = 0
                                    candidates = list()

                       
                                
                            else:
                                if element_2[:5] == "\tbest": #The selected candidate from DeCS
                                    best_candidate_url= element_2.split("(")[1].split(")")[0]
                                        
                                    if best_candidate_url[0] == "C" or best_candidate_url[0] == "D" or ("/" not in best_candidate_url[0]): 
                                        candidates.sort(key=get_score, reverse=True)
                                        found_new_best_candidate = False
                                               
                                        for candidate in candidates:
                                                
                                            if candidate[0][0] != "C" and candidate[0][0] != "D" and found_new_best_candidate == False:
                                                new_best_candidate = candidate[0]
                                                    
                                                found_new_best_candidate = True
                                                temp_dict[entity_text] = new_best_candidate
                                        
                                    else:  
                                        temp_dict[entity_text] = best_candidate_url    
                                        
                                else:
                                    if len(element_2) == 8:
                                        element_2 = element_2 +  ')=>NaN (in=0  deg=0)  (fb=Infinity)'
                                    if element_2 == '(NaN) false =':
                                        element_2 = element_2 + '> NaN       (in=0  deg=0)'
                                    best_candidate_url= element_2.split("(")[1].split(")")[0]
                                    score = element_2.split("(")[1].split(")")[1].split("=>")[1].strip(" ")
                                    
                                    if score == 'null\t':
                                        score = 0
                                    
                                    candidates.append((best_candidate_url, score))
                                    

                        
                results_dict[doc_name] = temp_dict           
    
    return results_dict            


def build_annotation_files(results_dict, ont_number):
    """Create the annotation files containing the DeCS codes"""
    
    output_dir = "./evaluation/NORM/" + ont_number + "/"
    subtrack_number = sys.argv[-2]
    subtrack_set = sys.argv[-1]
    
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ner_annotations = parse_ner_output()
    new_dict = {}
    for doc in ner_annotations.keys():
        ls = []
        output = str()

        if len(ner_annotations.get(doc))== 0:
               new_dict[doc] = []
        else:
                

            if doc.strip(".ann") in results_dict.keys():
                doc_results = results_dict[doc.strip(".ann")]
                doc_annotations = ner_annotations[doc]
                for annotation in doc_annotations:
                    tmp_annotation_text = annotation[0].lower().replace(" ", "_")

                    if tmp_annotation_text in doc_results.keys():
                        ecieo3_code = doc_results[tmp_annotation_text]
                        output = [annotation[0],annotation[1],annotation[2],ecieo3_code.replace('"','')]
                        ls.append(output)

                    new_dict[doc] = ls

    with open(output_dir + subtrack_set + '_' + 'subtask' + subtrack_number + '_norm_output.json', 'w',encoding = 'utf-8') as output_file:
        json.dump(new_dict,output_file,ensure_ascii=False)
               
                
if __name__ == "__main__":
    ont_number = str(sys.argv[1])
    model = "ppr_ic"
    
    results_dict = get_ppr_output(ont_number, model)
    build_annotation_files(results_dict, ont_number)
    
    print("Post-processing complete. Submission files in '.evaluation/NORM/'" + ont_number + " dir")

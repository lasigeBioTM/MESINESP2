import sys
import json
import ssmpy
import copy
import os
from statistics import mean
from operator import itemgetter

sys.path.append("./")

track = str(sys.argv[1])
sets = str(sys.argv[2])
perc = (sys.argv[3]) 
doc_dir = '../evaluation/NORM/single_ont/' + str(sets) + '_subtask' + str(track) + '_norm_output.json'
file = open(doc_dir,'r',encoding = 'utf-8')
data = json.load(file)
keys = list(data.keys())
new_dict = {}
for key in keys:
    print(keys.index(key) + 1 , '/',  len(keys))
    values = data[key]
    cp_values = copy.deepcopy(values)
    entities_codes = []
    #delete begin and end of annotation
    for i in cp_values:
        del i[1:3]
        entities_codes.append(i)

    
    new_entities_codes = []
    # delete duplicate entities
    [new_entities_codes.append(i) for i in entities_codes if i not in new_entities_codes]
    sem = []
    av_entities = []
    for i in new_entities_codes:
        av_entity = []
        av_list = []
        for j in new_entities_codes:
            if i != j:
                
                ssmpy.semantic_base("mesh.db")
                e1 = ssmpy.get_id(i[1])
                e2 = ssmpy.get_id(j[1])
                res = ssmpy.ssm_resnik(e1,e2)
                av_list.append(res)

        if av_list == []:
            av_list.append(0)
        av = mean(av_list)
        # append the entity to a new list
        av_entity.append(i)
        # append the average of resnik of the entity
        av_entity.append(av)
        av_entities.append(av_entity)

    av_entities = sorted(av_entities,key = itemgetter(1),reverse = True)
    # select the 1st, 2nd or 3rd quartile
    quantile = int(len(av_entities) * float(perc))
    av_entities_quantil = av_entities[:quantile+1]

    
    out_values = []
    for i in values:
        for j in av_entities_quantil:
            if i[3] in j[0] and j[1] > 0:
                out_values.append(i)
    

    new_dict[key] = out_values

if not os.path.exists("../evaluation/Semantic_Similarity/Subtrack" + str(track) + "/"):
        os.makedirs("../evaluation/Semantic_Similarity/Subtrack" + str(track) + "/")
with open('../evaluation/Semantic_Similarity/Subtrack' + str(track) + '/entities_subtrack' + str(track) + '_' + str(sets) + '_' + str(perc) + \
          '_semantic_similarity' + '.json','w',encoding = 'utf-8') as outFile:

    json.dump(new_dict,outFile,ensure_ascii=False)

print('output files in /evaluation/Semantic_Similarity/Subtrack' + str(track) + '/')
        

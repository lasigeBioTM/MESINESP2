import sys
import json
import os

sys.path.append("./")

track = sys.argv[1]
sets = sys.argv[2]

input_doc = '../Additional_data/Subtrack' + str(track) + '/entities_subtrack' + str(track) + '_' + str(sets) + '.json'

file = open(input_doc,'r',encoding = 'utf-8')
data = json.load(file)
docs = data.get('articles')
pos = int()
new_dict = {}
out_ls = []
for i in docs:
    ls = list(i.values())
    ls = [ i for i in ls if i!=[]]
    for j in ls:
        if type(j) == list and j!=[]:
            #print(j)
            index_j = ls.index(j)
            #print(index_j)
            jls = []
            for a in j:
                als = list(a.values())
                jls.append(als)
            ls[index_j] = jls

    out_list = [item for sublist in ls[1:] for item in sublist]
    new_dict[pos] = out_list
    pos += 1

if not os.path.exists("./evaluation/Additional_data/Subtrack" + str(track) + "/"):
        os.makedirs("./evaluation/Additional_data/Subtrack" + str(track) + "/")
with open('./evaluation/Additional_data/Subtrack' + str(track) + '/entities_subtrack' + str(track) + '_' + str(sets) + '.json','w',encoding = 'utf-8') as outFile:
    json.dump(new_dict,outFile,ensure_ascii=False)



    




cd preprocessing
mkdir retrieved_data
cd retrieved_data

# DeCS in obo format
wget https://zenodo.org/record/4634129/files/DeCS2020.obo?download=1
mv DeCS2020.obo?download=1 DeCS2020.obo

# DeCS in .tsv format
wget https://zenodo.org/record/4634129/files/DeCS2020.tsv?download=1
mv DeCS2020.tsv?download=1 DeCS2020.tsv

# Subtrack 1 corpus: Scientific literature (https://temu.bsc.es/mesinesp2/sub-track-1-scientific-literature/)
wget https://zenodo.org/record/4634129/files/Subtrack1-Scientific_Literature.zip?download=1
unzip Subtrack1-Scientific_Literature.zip?download=1

# Subtrack 2 corpus: Clinical Trials ()
wget https://zenodo.org/record/4634129/files/Subtrack2-Clinical_Trials.zip?download=1
unzip Subtrack2-Clinical_Trials.zip?download=1

# Subtrack 3 corpus: Patents ()
wget https://zenodo.org/record/4634129/files/Subtrack3-Patents.zip?download=1
unzip Subtrack3-Patents.zip?download=1

cd ../../

# Download recognized entities files
wget https://zenodo.org/record/4701973/files/Additional%20data.zip?download=1
unzip Additional\ data.zip?download=1

#Change the directories names
mv ./Additional\ data/ ./Additional_data/
mv ./Additional_data/Subtrack1-Scientific_Literature ./Additional_data/Subtrack1
mv ./Additional_data/Subtrack2-Clinical_Trials ./Additional_data/Subtrack2
mv ./Additional_data/Subtrack3-Patents ./Additional_data/Subtrack3

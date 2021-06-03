# MESINESP2

### 1. Setup
#### 1.1 Get "Additional_data" files
```
./get_data.sh
```
#### 1.2 Pre process
```
python pre_process_additional_data.py <track> <subset>
```
Args:
- "track" - 1, 2 or 3.

1- Scientific Literature; 2- Clinical Trials; 3- Patents

- "subset" - train, dev, test

Output in evaluation/Additional_data/ directory

### 2. Find the DeCS for each entity from the Additional_data directory
```
./norm.sh <track> <subset>
```
Output in evaluation/NORM/ directory

### 3. Filter the entities from the NORM step based on their semantic similarity
```
pip install merpy
```

```
python semantic_similarity.py <track> <subset> <filter>
```
- "filter" - "0.25" or "1.0"

Filters the top 25% entities based on the semantic similarity or selects all the entities from the NORM output

Output in evaluation/Semantic_Similariry/ directory

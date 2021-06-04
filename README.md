# MESINESP2

Code associated with the participation of the LASIGE_BioTM team in [MESINESP2 (Medical Semantic Indexing in Spanish Shared Task)](https://temu.bsc.es/mesinesp2/)

The pipeline includes three modules:
- Entity Linking: links the recognized entities provided by the organization to [DeCS](https://decs.bvsalud.org/) terms
- Preprocessing: processes MESINESP2 corpus files (appending extracted entities to the end of texts, stemming) tobe the input for the classification algorithm
- Extreme Multi-Label Classification: assigns each doc the top-20 relevant DeCS codes

To download the required data:

```
./get_data.sh
```

Then build a Docker image from the provided Dockerfile. Go to each dir for specific script execution instructions.

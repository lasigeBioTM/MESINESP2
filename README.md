# MESINESP2

Code associated with the participation of the LASIGE_BioTM team in [MESINESP2 (Medical Semantic Indexing in Spanish Shared Task)](https://temu.bsc.es/mesinesp2/)

The pipeline includes two modules:
- Entity Linking: links the recognized entities provided by the organization to [DeCS](https://decs.bvsalud.org/) terms
- preprocessing: processes MESINESP2 corpus files (append extracted entities to text, stemming) for input of the classification algorithm
- Extreme Multi-Label Classification: assigns each doc the top-20 relevant DeCS codes

Build a Docker image from the provided Dockerfile. Go to each dir for specific script execution instructions.

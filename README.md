Code associated with the participation of the LASIGE_BioTM team in [MESINESP2 (Medical Semantic Indexing in Spanish Shared Task)](https://temu.bsc.es/mesinesp2/)

The pipeline includes two modules:
- Entity Linking: linking the recognized entities provided by the organization to [DeCS](https://decs.bvsalud.org/) terms
- Extreme Multi-Label Classification: preprocesses MESINESP2 corpus files and then assigns each doc the top-20 relevant DeCS codes

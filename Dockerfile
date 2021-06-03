FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-devel

RUN apt-get update && apt-get install -y wget && apt-get autoclean -y
RUN apt-get update && apt-get install -y nano && apt-get autoclean -y

#COPY ./requirements ./
#RUN pip install -r requirements

RUN pip install h5py
RUN pip install scipy
RUN pip install sklearn
RUN pip install torch
RUN pip install pandas
RUN pip install nltk
RUN pip install sentencepiece
RUN pip install transformers==2.2.2
RUN pip install allennlp
RUN pip install pytorch_pretrained_bert

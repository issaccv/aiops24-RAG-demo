#!/bin/bash

# create bin dir
mkdir bin

# install ollama
curl -L https://mirror.ghproxy.com/https://github.com/ollama/ollama/releases/download/v0.1.32/ollama-linux-amd64 -o bin/ollama
chmod +x bin/ollama

# run ollama in the background
bin/ollama serve &

# download model 
wget "https://www.modelscope.cn/api/v1/models/qwen/Qwen1.5-14B-Chat-GGUF/repo?Revision=master&FilePath=qwen1_5-14b-chat-q4_0.gguf" -O qwen-1.5-14b-chat.gguf

# create qwen with modelfile
bin/ollama create qwen -f modelfile

# download the embedding model
git clone https://www.modelscope.cn/AI-ModelScope/bge-small-zh-v1.5.git demo/BAAI/bge-small-zh-v1.5

# download dataset
git clone https://www.modelscope.cn/datasets/issaccv/aiops2024-challenge-dataset.git demo/dataset

mv demo/dataset/question.jsonl demo/question.jsonl

unzip demo/dataset/data.zip -d demo/

# print info 
echo "The Ollama server is running in the background. Please close current terminal and you can now play with demo!"
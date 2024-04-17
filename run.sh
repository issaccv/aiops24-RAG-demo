#!/bin/bash

# create bin dir
mkdir bin

# install ollama
curl -L https://ollama.com/download/ollama-linux-amd64 -o bin/ollama
chmod +x bin/ollama

# run ollama in the background
bin/ollama &

# download model 
wget "https://www.modelscope.cn/api/v1/models/qwen/Qwen1.5-14B-Chat-GGUF/repo?Revision=master&FilePath=qwen1_5-14b-chat-q4_0.gguf" -O qwen-1.5-14b-chat.gguf

# create qwen with modelfile
ollama create qwen -f modelfile

# download the embedding model
git clone https://www.modelscope.cn/AI-ModelScope/bge-small-zh-v1.5.git demo/BAAI/bge-small-zh-v1.5

# print info 
echo "The Ollama server is running in the background. You can now play with demo!"
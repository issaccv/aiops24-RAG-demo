import asyncio

from dotenv import dotenv_values
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from qdrant_client import models
from tqdm.asyncio import tqdm

from pipeline.ingestion import build_pipeline, build_vector_store, read_data
from pipeline.qa import read_jsonl, save_answers
from pipeline.rag import QdrantRetriever, generation_with_knowledge_retrieval


async def main():
    config = dotenv_values(".env")

    # 初始化 LLM 嵌入模型 和 Reranker
    llm = Ollama(model="qwen", base_url=config["OLLAMA_URL"], temperature=0)
    embeding = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5", cache_folder="./"
    )
    Settings.embed_model = embeding

    # 初始化 数据ingestion pipeline 和 vector store
    client, vector_store = await build_vector_store(config, reindex=False)

    collection_info = await client.get_collection(
        config["COLLECTION_NAME"] or "aiops24"
    )

    if collection_info.points_count == 0:
        data = read_data("data")
        pipeline = build_pipeline(llm, embeding, vector_store=vector_store)
        # 暂时停止实时索引
        await client.update_collection(
            collection_name=config["COLLECTION_NAME"] or "aiops24",
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0),
        )
        await pipeline.arun(documents=data, show_progress=True)
        # 恢复实时索引
        await client.update_collection(
            collection_name=config["COLLECTION_NAME"] or "aiops24",
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
        )
        print(len(data))

    retriever = QdrantRetriever(vector_store, embeding, similarity_top_k=3)

    queries = read_jsonl("question.jsonl")

    # 生成答案
    print("Start generating answers...")
    pbar = tqdm(total=len(queries))

    # 将任务打包为一个列表
    tasks = [
        generation_with_knowledge_retrieval(
            query["query"], retriever, llm, progress=pbar
        )
        for query in queries
    ]

    # 并行执行并等待所有任务完成
    results = await asyncio.gather(*tasks)
    pbar.close()
    # 处理结果
    save_answers(queries, results, "submit_result.jsonl")


if __name__ == "__main__":
    asyncio.run(main())

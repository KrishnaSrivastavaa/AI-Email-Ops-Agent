import chromadb
import chromadb.utils.embedding_functions as embedding_functions

client = chromadb.Client()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="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",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="agent_memory",
    embedding_function=openai_ef
)

collection.add(
    documents=["Krishna is building AI agents"],
    ids=["1"]
)

results = collection.query(
    query_texts=["Apple"],
    n_results=1
)

print(results)

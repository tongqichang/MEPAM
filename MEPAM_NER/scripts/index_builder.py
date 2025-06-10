import os
import sys
import argparse

import nest_asyncio
nest_asyncio.apply()

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import SimpleDirectoryReader
import faiss
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.vector_stores.simple import SimpleVectorStore
from llama_index.graph_stores.nebula import NebulaPropertyGraphStore
from llama_index.core import PropertyGraphIndex

def main(args):
    Settings.embed_model = OllamaEmbedding(model_name=args.embed_model, base_url=args.ollama_url)
    Settings.llm = Ollama(model=args.llm, base_url=args.ollama_url, request_timeout=120.0)
    Settings.chunk_size = args.chunk_size

    documents = SimpleDirectoryReader(args.data_dir).load_data()

    # Ensure that the environment variables are set before running:
    # NEBULA_ADDRESS, NEBULA_USER, NEBULA_PASSWORD
    graph_store = NebulaPropertyGraphStore(
        url=args.graph_url,
        username=args.graph_username,
        password=args.graph_password,
        space=args.graph_space_name, overwrite=True)

    vec_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(1024))
    #vec_store = SimpleVectorStore()
    index = PropertyGraphIndex.from_documents(
        documents,
        property_graph_store=graph_store,
        vector_store=vec_store,
        show_progress=True,
    )
    index.storage_context.vector_store.persist(args.vector_path)

def valid_directory(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Index Builder')
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="ollama service address"
    )
    parser.add_argument(
        "--graph-url",
        type=str,
        required=True,
        help="graph database service address"
    )
    parser.add_argument(
        "--graph-username",
        type=str,
        required=True,
        help="user name of graph database"
    )
    parser.add_argument(
        "--graph-password",
        type=str,
        required=True,
        help="password of graph database"
    )
    parser.add_argument(
        "--embed-model",
        type=str,
        default="bge-m3:567m",
        help="embedding model, must from ollama server"
    )
    parser.add_argument(
        "--llm",
        type=str,
        default="qwen2.5:14b",
        help="llm for extract or others generate, must from ollama server"
    )
    parser.add_argument(
        "--data_dir",
        type=valid_directory,
        required=True,
        help="the directory containing the data to be indexed"
    )
    parser.add_argument(
        "--vector-path",
        type=str,
        required=True,
        help="the file path to save the vector index"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="chunk size for embedding"
    )
    parser.add_argument(
        "--graph-space-name",
        type=str,
        required=True,
        help="the space name of graph database"
    )
    args = parser.parse_args()
    main(args)
#export NEBULA_USER=root
#export NEBULA_PASSWORD=123456
#export NEBULA_ADDRESS=localhost:9669

python index_builder.py \
--ollama-url "http://localhost:11434" \
--graph-url "nebula://localhost:9669" \
--graph-username root \
--graph-password 123456 \
--llm "mixtral:8x7b" \
--data_dir "../data/test/" \
--graph-space-name "enzyme_extract_test" \
--chunk-size 512 \
--vector-path "../vec/faiss_test"
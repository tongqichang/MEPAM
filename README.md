 # MEPAM
a evidence-based Question-Answering system：Microbial Enzyme Production and Catalytic Activit
## Technical Architecture
MEPAM_NER:Named Entity Recognition based on OntoGPT

MEPAM_QA：Question-Answering System based on GraphRAG
## Quick Start
## MEPAM_NER
You can quickly build a knowledge graph using MEPAM_NER. If you only need to use the QA system, you can skip to the MEPAM_QA section.
### 1. Environment Configuration
```bash
conda env create -f environment.yaml
conda activate ner
poetry install
```
Before running the code, please set your API key and basic settings in the INI file. You can also save your API key in the .env file or set it using export:
 ```bash
export OPENAI_API_KEY=your_api_key_here 
 ```
1.1 Install the Evaluation Model ollama/qwen2.5:14b
```bash
export OLLAMA_MIRROR="https://ghproxy.cn/https://github.com/ollama/ollama/releases/latest/download"
curl -fsSL https://ollama.com/install.sh | sed "s|https://ollama.com/download|$OLLAMA_MIRROR|g" | sh
ollama run qwen2.5:14b
```
### 2. Triple Extraction
2.1 Extract Information from PDFs

```bash
python MEPAM_NER/scripts/grobid_pdf2csv.py MEPAM_NER/scripts/pdf2txt.ini
python MEPAM_NER/scripts/cermine_pdf2csv.py MEPAM_NER/scripts/pdf2txt.ini
python MEPAM/MEPAM_NER/scripts/combine.py
 ```
2.2 Evaluate the Accuracy of PDF Extraction
Please modify the INI configuration before use:
```bash
python MEPAM_NER/scripts/parse_metric.py MEPAM_NER/scripts/pdf2txt.ini
 ```
#### Before extraction, please download the corresponding literature according to the list in data/100txtlist.xlsx for testing.

2.3 Extract Triples Using LinkML
```bash
bash MEPAM_NER/scripts/LinkML.sh
```
2.4 Extract Triples Using NonLinkML
```bash
python MEPAM_NER/scripts/getjson.py --input_folder MEPAM_NER/data/2txt/ --output_folder data/nonlinkml/qwen/  --api_key your_api_key_here --model openai/qwen2.5-72b-instruct --base_url https://dashscope.aliyuncs.com/compatible-mode/v1 
```
2.5 Evaluate the Results
```bash
python MEPAM_NER/scripts/ner_metric.py ner_metric.ini
```
####In the data directory, we have saved the results of LinkML, NonLinkML, and manual extraction for 100 articles, as well as the final evaluation results.
### 3.  The database of QA System
3.1 Vector database
Before constructing the vector database, please download bge-m3:567m and qwen2.5:14b using Ollama, and make sure NebulaGraph is properly deployed. You can find NebulaGraph at:
https://github.com/vesoft-inc/nebula
```bash
pip install llama-index-embeddings-ollama
cd MEPAM_QA
sh index_builder.sh
```
3.2  Knowledge graph database
After generating the YAML file using the NER module, you can use the following code to generate the triplet structure and import it into NebulaGraph. You can find all the triplet data from this article in Supplementary Tables S7 and S8.
```bash
python yaml2nebula_tsv.py  yaml2tsv.ini
python nebula_create.py
```


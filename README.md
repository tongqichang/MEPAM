# MEPCA
a evidence-based Question-Answering system：Microbial Enzyme Production and Catalytic Activit
## 效果图
![问答系统效果图](img/qa_show.png)
## Before using the QAsystem
Please download the QAsystem:
```bash
wget -O MEPCA_QA.tar "https://example.com/path/to/MEPCA_QA.tar"
```
## 技术架构
MEPCA_NER:基于ontogpt的实体识别
MEPCA_QA：基于graphrag的问答系统
## 快速开始
## MEPCA_NER
您可以通过MEPCA_NER快速进行图谱的构建工作，如果仅需要使用问答系统可直接跳转MEPCA_QA部分
### 1. 环境配置
```bash
conda env create -f environment.yaml
conda activate ner
poetry install
```
在运行代码前请设置您的api key和ini文件中的基本设置
通过设置.env文件保存您的api key也可以通过export设置
 ```export OPENAI_API_KEY=your_api_key_here 
 ```
1.1 安装结果评估模型ollama/qwen2.5:14b
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run qwen2.5:14b
```
### 2. 三元组提取
2.1 pdf提取信息
请在使用前修改ini配置
```bash
python MEPCA_NER/scripts/grobid_pdf2csv.py MEPCA_NER/scripts/pdf2txt.ini
python MEPCA_NER/scripts/cermine_pdf2csv.py MEPCA_NER/scripts/pdf2txt.ini
python MEPCA/MEPCA_NER/scripts/combine.py
 ```
2.2 PDF提取的准确度评估
```bash
python MEPCA_NER/scripts/parse_metric.py MEPCA_NER/scripts/pdf2txt.ini
 ```
#### 在提取前请您根据noid3/100txtlist.xlsx中的名单下载对应文献以便进行测试

2.3 LinkML提取三元组
```bash
bash MEPCA_NER/scripts/LinkML.sh
```
2.4 NonLinkML提取三元组
```bash
python MEPCA_NER/scripts/getjson.py --input_folder MEPCA_NER/noid3/100txt/ --output_folder noid3/nonlinkml/qwen/  --api_key your_api_key_here --model openai/qwen2.5-72b-instruct --base_url https://dashscope.aliyuncs.com/compatible-mode/v1 
```
2.5 结果评估
```bash
python MEPCA_NER/scripts/ner_metric.py ner_metric.ini
```
####在noid3文件中我们保存了100篇文献的linkml、nonlinkml以及人工提取结果，以及最终评估的效果
### 3. 问答系统的使用
3.1 启动Ollama服务
```bash
cd MEPCA_QA/ollama
sh start_service.sh
```
验证ollama服务是否运行
在浏览器地址栏中输入http://your_IP:11434 检查是否显示Ollama is running
3.2 启动nebula graph
```bash
cd nebula/nebula-graph-3.8
docker-compose pull
docker-compose up -d
```
3.3 启动nebula graph console
```bash
cd nebula-graph-studio-3.10.0
docker-compose pull
docker-compose up -d
```
你可以通过http://your_IP:7001/进行登录，默认账号是root密码是12345678
3.4 确认数据索引是否都存在
节点索引，如果存在则跳过下一步的索引创建环节
![问答系统效果图](img/index-1.png)
如果不存在，请手动创建一下这三个顶点的索引
![问答系统效果图](img/index-2.png)
创建完成后执行rebuild
![问答系统效果图](img/index-3.png)
3.5 边索引是否存在，如果存在则跳过下一步的索引创建环节
![问答系统效果图](img/index-4.png)
如果不存在，请手动创建一下边的索引
![问答系统效果图](img/index-5.png)
创建完成后执行rebuild
![问答系统效果图](img/index-6.png)
3.5 chatbot服务
```bash
cd enzyme-rag-server
```
修改app/config.yaml，将地址修改为部署nebula和ollama部署机器的IP
```bash
sh start_service.sh
docker ps | grep enzyme_rag_server
```
你可以通过http://your_IP:8000/进行登录，默认账号是admin密码是admin
#### 当服务器资源较少时可能会出现未响应的问题，请通过docker logs enzyme_rag_server查看是否出现times out报错，请确保具有一定的服务器资源再进行调用

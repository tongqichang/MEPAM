import pandas as pd

# 读取Excel文件
file_path = r"C:\Users\LEGION\Desktop\第六部分网络图\纤维素酶produce_ph_temp.xlsx"
df = pd.read_excel(file_path, sheet_name='cellulase_produce_id')

# 定义列顺序（从start_id开始到end_id结束）
columns_order = [
    'start_id',  # 起点
    'temperature',  # 需要连接的列
    'ph',
    'incubation_period',
    'moisture',
    'carbon_source',
    'nitrogen_source',
    'aeration',
    'agitation',
    'volume',
    'quantitative_value',
    'end_id'  # 终点
]

edges = []  # 存储所有边（包含重复）

# 遍历每一行数据
for _, row in df.iterrows():
    # 获取当前行的所有列值（转换为字符串，避免NaN问题）
    row_data = {col: str(row[col]).strip() if pd.notna(row[col]) else None for col in columns_order}

    # 初始化前驱节点为start_id
    prev_node = str(row_data['start_id']) if row_data['start_id'] else None

    if not prev_node:
        continue  # 如果start_id为空，跳过此行

    # 按列顺序遍历连接节点
    for col in columns_order[1:-1]:  # 跳过start_id和end_id，只处理中间的列
        current_node = row_data[col]
        if current_node and current_node not in ['None', 'nan']:
            if prev_node:
                edges.append({'source': prev_node, 'target': current_node})
            prev_node = current_node  # 更新前驱节点

    # 最后连接到end_id（如果end_id存在且前驱存在）
    end_node = str(row_data['end_id']) if row_data['end_id'] else None
    if prev_node and end_node:
        edges.append({'source': prev_node, 'target': end_node})

# 生成边数据DataFrame
edges_df = pd.DataFrame(edges)

# 统计边权重（使用分组统计出现次数）
edges_df = edges_df.groupby(['source', 'target'], as_index=False).size().rename(columns={'size': 'weight'})

# 保存到新的Excel文件
output_path = r"C:\Users\LEGION\Desktop\第六部分网络图\纤维素酶produce_ph_temp_edge.xlsx"
edges_df.to_excel(output_path, index=False, columns=['source', 'target', 'weight'])

print(f"边数据已生成并保存至：{output_path}")
print(f"总生成 {len(edges_df)} 条唯一边，包含权重信息")
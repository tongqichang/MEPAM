import pandas as pd


def create_id_label_tsv(input_file_path, output_tsv_path):
    # 读取Excel文件中的两个sheet
    try:
        # 读取时跳过空行，确保数据对齐
        df_catalysis = pd.read_excel(input_file_path,
                                     sheet_name='cellulase_produce',
                                     engine='openpyxl').dropna(how='all')
        df_produce_id = pd.read_excel(input_file_path,
                                      sheet_name='cellulase_produce_id',
                                      engine='openpyxl').dropna(how='all')
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return

    # 检查是否有数据
    if df_catalysis.empty or df_produce_id.empty:
        print("错误：至少有一个工作表是空的！")
        return

    # 创建id-label映射字典（展平所有值）
    id_label_map = {}

    # 获取所有非空单元格的对应关系
    for (_, col_cat), (_, col_id) in zip(df_catalysis.items(), df_produce_id.items()):
        for label, id_val in zip(col_cat.dropna(), col_id.dropna()):
            try:
                id_label_map[int(id_val)] = str(label)
            except (ValueError, TypeError):
                continue  # 跳过无效的ID值

    if not id_label_map:
        print("错误：没有有效的id-label匹配对！")
        return

    # 创建包含id和label的DataFrame
    result_df = pd.DataFrame({
        'id': id_label_map.keys(),
        'label': id_label_map.values()
    }).sort_values('id')

    # 写入TSV文件
    try:
        result_df.to_csv(output_tsv_path, sep='\t', index=False, encoding='utf-8') 
        print(f"成功创建TSV文件: {output_tsv_path}")
        print(f"共匹配了 {len(result_df)} 对id-label关系")
    except Exception as e:
        print(f"写入TSV文件失败: {e}")


if __name__ == "__main__":
    input_excel = r"C:\Users\LEGION\Desktop\第六部分网络图\纤维素酶produce_培养基.xlsx"
    output_tsv = r"C:\Users\LEGION\Desktop\第六部分网络图\纤维素酶produce_培养基.tsv"

    create_id_label_tsv(input_excel, output_tsv)
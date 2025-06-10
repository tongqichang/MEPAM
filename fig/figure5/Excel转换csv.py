import pandas as pd
import os


def excel_to_csv(input_excel, output_csv):
    """
    将Excel文件转换为CSV格式
    :param input_excel: 输入的Excel文件路径
    :param output_csv: 输出的CSV文件路径
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(input_excel, sheet_name='Sheet1')

        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        # 保存为CSV，保留原始列名，不添加索引，UTF-8编码
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')  # utf-8-sig处理Excel兼容性
        print(f"转换成功: {input_excel} → {output_csv}")
        return True
    except Exception as e:
        print(f"转换失败: {input_excel}\n错误信息: {str(e)}")
        return False


# 主程序
if __name__ == "__main__":
    # 定义输入输出文件路径（根据您的实际路径修改）
    base_dir = r"C:\Users\LEGION\Desktop\第六部分网络图"
    output_dir = os.path.join(base_dir, "csv_produce培养基")  # 新建输出文件夹

    input_files = {
        os.path.join(base_dir, "纤维素酶produce_培养基_node.xlsx"): os.path.join(output_dir, "nodes.csv"),
        os.path.join(base_dir, "纤维素酶produce_培养基_edge.xlsx"): os.path.join(output_dir, "edges.csv")
    }

    print("=" * 50)
    print("开始转换Excel文件为CSV格式...")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 逐个转换文件
    success_count = 0
    for input_excel, output_csv in input_files.items():
        if os.path.exists(input_excel):
            if excel_to_csv(input_excel, output_csv):
                success_count += 1
        else:
            print(f"文件不存在: {input_excel}")

    print("=" * 50)
    print(f"转换完成！成功转换 {success_count}/{len(input_files)} 个文件")
    print(f"CSV文件已保存到: {output_dir}")
    print("=" * 50)

    # 添加暂停以便查看结果（仅限Windows）
    if os.name == 'nt':
        os.system("pause")
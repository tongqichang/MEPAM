import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from scipy.stats import ttest_ind

# 设置绘图风格
sns.set_theme(style="whitegrid", font_scale=1.2)

# 文件路径
file_path = r"/文章素材/questions(4).xlsx"

# 首先查看Excel文件中的所有sheet名称
excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names
print(f"Excel文件中的sheet名称: {sheet_names}")

# 模型名称
model_names = ["MEPAM", "MEPAM(NO KG)", "GPT-4o", "mixtral8×7B", "DeepSeek-V3", "Qwen2.5 72B"]

# 要读取的指标列
target_columns = ["Exact Match", "Hallucination rate", "Faithfulness", "Precision", "Recall", "F1 score"]

# 存储数据
all_model_data = []
successful_models = []

# 检查每个sheet
for i, model in enumerate(model_names):
    try:
        if i < len(sheet_names):
            df_temp = pd.read_excel(file_path, sheet_name=i)
            print(f"\n=== {model} 数据详细检查 ===")
            print(f"Sheet形状: {df_temp.shape}")
            print(f"列名: {df_temp.columns.tolist()}")

            found_columns = []
            for col in target_columns:
                if col in df_temp.columns:
                    found_columns.append(col)
                    non_null_count = df_temp[col].notna().sum()
                    print(f"  {col}: {non_null_count} 个非空值")

            print(f"找到的目标列: {found_columns}")

            if found_columns:
                record_count = 0
                for idx, row in df_temp.iterrows():
                    for col in found_columns:
                        if not pd.isna(row[col]):
                            all_model_data.append({
                                'Model': model,
                                'Metric': col,
                                'Score': row[col],
                                'Question_Index': idx
                            })
                            record_count += 1

                successful_models.append(model)
                print(f"成功读取 {model} 的数据，共 {record_count} 条记录")
            else:
                print(f"警告: {model} 没有找到任何目标列")
        else:
            print(f"警告: 没有足够的sheet来读取 {model} 的数据")
    except Exception as e:
        print(f"读取 {model} 数据时出错: {e}")

# 检查是否有数据
if not all_model_data:
    raise ValueError("错误: 没有成功读取任何数据")

# 创建 DataFrame
df_long = pd.DataFrame(all_model_data)
print(f"\n=== 最终数据汇总 ===")
print(f"数据形状: {df_long.shape}")
print(f"\n包含的模型: {df_long['Model'].unique()}")
print(f"\n包含的指标: {df_long['Metric'].unique()}")

# 自定义颜色（顺序与 successful_models 一致）
model_colors = ['#4489C8', '#EE7C79', '#008F91', '#FFCD44', '#A55CA9', '#60B568']
palette = {model: model_colors[i % len(model_colors)] for i, model in enumerate(successful_models)}

# 按模型和指标分组统计
print(f"\n=== 各模型数据统计 ===")
model_metric_counts = df_long.groupby(['Model', 'Metric']).size().unstack(fill_value=0)
print(model_metric_counts)

# 绘图
metrics = df_long['Metric'].unique().tolist()
metrics = [m for m in metrics if m not in ["Faithfulness", "Hallucination rate"]] + ["Faithfulness", "Hallucination rate"]

fig, axes = plt.subplots(2, 3, figsize=(20, 14))
axes = axes.flatten()

for i, metric in enumerate(metrics):
    metric_data = df_long[df_long['Metric'] == metric]

    print(f"\n绘制指标 {metric} - 包含的模型: {metric_data['Model'].unique()}")

    # 柱状图
    bars = sns.barplot(
        data=metric_data,
        x="Model", y="Score",
        palette=palette,
        alpha=0.85,
        estimator='mean',
        ax=axes[i],
        order=successful_models,
        errorbar=None
    )

    # 散点图
    sns.stripplot(
        data=metric_data,
        x="Model", y="Score",
        palette=palette,
        alpha=0.8,
        size=6,
        edgecolor='black',
        linewidth=0.5,
        jitter=0.2,
        ax=axes[i],
        order=successful_models
    )

    axes[i].set_title(f'{metric}', fontsize=21, weight='bold')
    axes[i].set_ylabel('Score',fontsize=21)
    axes[i].set_xlabel("")
    axes[i].tick_params(axis='x', rotation=45, labelsize=18)
    axes[i].tick_params(axis='y', labelsize=21)
    axes[i].set_ylim(-0.1, 1.1)  # 稍微增加y轴上限以容纳数据标签

    # 参考线
    axes[i].axhline(y=0, color='gray', linestyle='-', alpha=0.3, linewidth=1)
    axes[i].axhline(y=0.5, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    axes[i].axhline(y=1.0, color='gray', linestyle='-', alpha=0.3, linewidth=1)

    # 在每个柱子上添加具体的数据值
    for j, model in enumerate(successful_models):
        model_scores = metric_data[metric_data['Model'] == model]['Score'].dropna()
        if len(model_scores) > 0:
            avg_score = model_scores.mean()
            axes[i].text(
                j,  # x 轴位置
                avg_score + 0.02,  # y 轴位置（略高于柱子顶端）
                f"{avg_score:.2f}",  # 显示两位小数
                ha='center',  # 水平居中
                va='bottom',  # 在柱子顶部对齐
                fontsize=18,
                fontweight='bold'
            )

    # -------------------
    # 显著性标注仍在柱子上方
    # -------------------
    ref_model = successful_models[0]
    ref_data = metric_data[metric_data['Model'] == ref_model]['Score'].dropna()
    if len(ref_data) > 1:
        for j, model in enumerate(successful_models[1:], 1):
            comp_data = metric_data[metric_data['Model'] == model]['Score'].dropna()
            if len(comp_data) > 1:
                t_stat, p_value = ttest_ind(ref_data, comp_data, equal_var=False)
                if p_value < 0.001:
                    sig_symbol = '***'
                elif p_value < 0.01:
                    sig_symbol = '**'
                elif p_value < 0.05:
                    sig_symbol = '*'
                else:
                    sig_symbol = 'ns'
                comp_height = metric_data[metric_data['Model'] == model]['Score'].mean()
                text_y = comp_height + 0.08  # 显著性符号略高于数值标签
                axes[i].text(j, text_y, sig_symbol,
                             ha='center', va='bottom', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(r"D:\知识图谱\模型\baitu\文章素材\metrics_individual_comparison_with_values.png",
            dpi=350, bbox_inches="tight")
plt.show()

# 打印统计
print(f"\n=== 最终统计汇总 ===")
print(f"成功读取了 {len(successful_models)} 个模型的数据:")
for model in successful_models:
    model_data = df_long[df_long['Model'] == model]
    print(f"- {model}: {len(model_data)} 条记录")

print(f"\n各指标的平均分数:")
avg_scores = df_long.groupby(['Model', 'Metric'])['Score'].mean().unstack()
print(avg_scores)

print(f"\n各模型在各指标上的记录数:")
counts = df_long.groupby(['Model', 'Metric']).size().unstack(fill_value=0)
print(counts)
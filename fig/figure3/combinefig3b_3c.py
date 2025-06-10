import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import mannwhitneyu

# 设置 Matplotlib 以文本形式保存 SVG 中的文字
plt.rcParams['svg.fonttype'] = 'none'
# 应用Seaborn主题
sns.set_theme(style="whitegrid")

# 设置文件路径和指标名称
metric_files = {
    'Precision': r"C:\Users\Lenovo\Desktop\150篇\新建文件夹\precision.xlsx",
    'Recall': r'C:\Users\Lenovo\Desktop\150篇\新建文件夹\recall.xlsx',
    'F1': r"C:\Users\Lenovo\Desktop\150篇\新建文件夹\F1.xlsx"
}

# 初始化存储所有数据的字典
all_data = {metric: {'non_linkml': None, 'linkml': None} for metric in metric_files}

# 读取所有数据
for metric, file_path in metric_files.items():
    df_non_linkml = pd.read_excel(file_path, sheet_name=0, index_col=0)
    df_linkml = pd.read_excel(file_path, sheet_name=1, index_col=0)
    all_data[metric]['non_linkml'] = df_non_linkml
    all_data[metric]['linkml'] = df_linkml

# 设置绘图参数
models = list(all_data['Precision']['non_linkml'].columns)
n_models = len(models)
metrics = list(metric_files.keys())
n_metrics = len(metrics)
# 组间宽度，增加一些间隔

# 原始颜色
model_colors = ['#41539F', '#3075B6', '#CE2F39', '#F17A37']
non_model_colors = ['#67589B', '#3DB4E5', '#E77E7F', '#FDCF1D']

# 调整颜色饱和度
desaturated_model_colors = [sns.desaturate(color, 0.4) for color in model_colors]
desaturated_non_model_colors = [sns.desaturate(color, 0.4) for color in non_model_colors]

# 调整后的颜色方案
colors = {
    'linkml': desaturated_model_colors,
    'non_linkml': desaturated_non_model_colors
}

# 创建大图
fig = plt.figure(figsize=(20, 8))

# 图1
ax1 = plt.subplot2grid((1, 50), (0, 0), colspan=38)

# 遍历每个指标进行绘图
bar_width = 0.1 # 柱宽
group_width = bar_width * (n_models * 2 + 4)  # 组间宽度，增加一些间隔，这里将间隔设置为1
metric_centers = [group_width * i + group_width / 2 for i in range(n_metrics)]
# 遍历每个指标进行绘图
for metric_idx, metric in enumerate(metrics):
    # 计算均值和标准差
    means_non_linkml = all_data[metric]['non_linkml'].mean(axis=0)
    means_linkml = all_data[metric]['linkml'].mean(axis=0)
    stds_non_linkml = all_data[metric]['non_linkml'].std(axis=0)
    stds_linkml = all_data[metric]['linkml'].std(axis=0)

    # 遍历每个模型
    for model_idx, model in enumerate(models):

        # Non-LinkML 柱状图
        ax1.bar(
            metric_idx * group_width + model_idx * (bar_width+0.03)* 2,
            means_non_linkml[model_idx],
            bar_width,
            color=colors['non_linkml'][model_idx],
            alpha=0.8,
            edgecolor='none',
            linewidth=0.5,
            label=f'Non-LinkML ({model})' if metric_idx == 0 else ""
        )

        # LinkML 柱状图
        ax1.bar(
            metric_idx * group_width + model_idx * (bar_width+0.03) * 2 + (bar_width+0.03),
            means_linkml[model_idx],
            bar_width,
            color=colors['linkml'][model_idx],
            alpha=0.8,
            edgecolor='none',
            linewidth=0.5,
            label=f'LinkML ({model})' if metric_idx == 0 else ""
        )

        # 绘制实心散点图
        # Non-LinkML 数据点
        y_non_linkml = all_data[metric]['non_linkml'].iloc[:, model_idx].values
        x_non_linkml = np.random.normal(
            metric_idx * group_width + model_idx * (bar_width+0.03) * 2,
            0.01,
            len(y_non_linkml)
        )
        ax1.scatter(
            x_non_linkml, y_non_linkml,
            color=colors['non_linkml'][model_idx],
            alpha=0.4, s=60, edgecolor='none', linewidth=0.5, marker='o'
        )

        # LinkML 数据点
        y_linkml = all_data[metric]['linkml'].iloc[:, model_idx].values
        x_linkml = np.random.normal(
            metric_idx * group_width + model_idx * (bar_width+0.03) * 2 + (bar_width+0.03),
            0.01,
            len(y_linkml)
        )
        ax1.scatter(
            x_linkml, y_linkml,
            color=colors['linkml'][model_idx],
            alpha=0.4, s=60, edgecolor='none', linewidth=0.5, marker='o'
        )

        # # 添加显著性标记
        # stat, p_val = mannwhitneyu(
        #     all_data[metric]['non_linkml'].iloc[:, model_idx],
        #     all_data[metric]['linkml'].iloc[:, model_idx],
        #     alternative='two-sided'
        # )
        # if p_val < 0.001:
        #     significance = '***'
        # elif p_val < 0.01:
        #     significance = '**'
        # elif p_val < 0.05:
        #     significance = '*'
        # else:
        #     significance = 'ns'
        #
        # max_height = max(
        #     means_non_linkml[model_idx],
        #     means_linkml[model_idx]
        # )
        # significance_height = max_height + 0.06  # 显著性标记和横线的高度
        #
        # # 计算显著性标记的 x 坐标
        # x_position = metric_idx * group_width + model_idx * (bar_width + 0.03) * 2 + (bar_width + 0.03) / 2
        #
        # # 添加显著性标记
        # ax1.text(
        #     x_position,
        #     significance_height + 0.03,  # 显著性标记位于横线上方0.03的位置
        #     significance,
        #     ha='center', va='bottom', fontsize=40, weight='bold'
        # )
        #
        # # 添加横线
        # ax1.plot(
        #     [x_position - (bar_width + 0.03) / 2, x_position + (bar_width + 0.03) / 2],  # 横线的起始和结束位置
        #     [significance_height+ 0.04, significance_height+ 0.04],  # 横线的高度
        #     color='black', linewidth=2
        # )
# 设置坐标轴和图例
from matplotlib.ticker import MultipleLocator
ax1.set_ylim(0, 1.3)
#ax1.set_ylabel('Score', fontsize=16)
ax1.set_xticks([])  # 隐藏 x 轴刻度
ax1.set_xticklabels([])  # 隐藏 x 轴标签
ax1.set_yticklabels([])  # 隐藏 x 轴标签
print(metrics)
#ax1.set_xticklabels(metrics, fontsize=14)
x_max = metric_idx * group_width + (n_models * 2 + 1) * bar_width + 0.5  # 计算x轴的最大值，增加右侧空白
# ax1.set_xlim(-0.15, x_max)
# 添加辅助线
ax1.axhline(0, color='black', linewidth=0.5)
ax1.yaxis.set_major_locator(MultipleLocator(0.2))  # 确保 y 轴刻度为整数
ax1.tick_params(axis='y', which='major', direction='out', length=10, width=1, colors='black')  # 设置 y 轴刻度线的样式
ax1.grid(axis='y', linestyle='--', alpha=0.4)

# 优化图例显示
handles, labels = ax1.get_legend_handles_labels()
non_linkml_handles = handles[::2]
linkml_handles = handles[1::2]
non_linkml_labels = labels[::2]
linkml_labels = labels[1::2]
combined_handles = non_linkml_handles + linkml_handles
combined_labels = non_linkml_labels + linkml_labels

# 创建自定义图例
# legend = ax1.legend(combined_handles, combined_labels, loc='upper center', bbox_to_anchor=(0.5, 0.99), ncol=2, fontsize=18)
# legend.set_frame_on(False)
# # 调整网格和边框
# ax1.grid(axis='y', linestyle='--', alpha=0.4)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# 图2
ax2 = plt.subplot2grid((1, 50), (0, 40), colspan=10)

# 读取Excel文件
df = pd.read_excel(r"C:\Users\Lenovo\Desktop\150篇\新建文件夹\pdf100.xlsx", sheet_name='Sheet1')

# 提取两组数据
abstract_match_metric = df['abstract_match_metric'].values
result_match_metric = df['result_match_metric'].values

# 定义颜色
colors = ['#CBB2B6', '#ABBFCA']

# 计算均值和标准差
mean_abstract = abstract_match_metric.mean()
mean_result = result_match_metric.mean()
print(mean_result)
std_abstract = abstract_match_metric.std()
std_result = result_match_metric.std()

# 计算每个模型的偏移量
bar_width = 0.1  # 柱状图宽度
# 添加一个额外的索引，用于虚拟柱子
index = [0, 0.2]
# 绘制柱状图
ax2.bar(index[0], mean_abstract, bar_width, yerr=std_abstract, label='Abstract', alpha=0.7, color=colors[0], capsize=5)
ax2.bar(index[1], mean_result, bar_width, yerr=std_result, label='Result', alpha=0.7, color=colors[1], capsize=5)

# 绘制散点图
x_Abstract = np.random.normal(index[0], 0.01, size=len(abstract_match_metric))  # 调整数据点分布范围
x_Result = np.random.normal(index[1], 0.01, size=len(result_match_metric))

ax2.scatter(x_Abstract, abstract_match_metric, color=colors[0], alpha=0.5, s=20)  # 调整散点大小
ax2.scatter(x_Result, result_match_metric, color=colors[1], alpha=0.5, s=20)

# 设置坐标轴和图例
#ax2.set_ylabel('Score', fontsize=14)
ax2.set_xticks([])  # 隐藏 x 轴刻度
ax2.set_xticklabels([])  # 隐藏 x 轴标签
ax2.set_yticklabels([])
# 调整网格和边框
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.spines['top'].set_visible(False)  # 隐藏顶部边框
ax2.spines['right'].set_visible(False)  # 隐藏右侧边框
ax2.spines['left'].set_linewidth(1.5)  # 设置左侧边框宽度
ax2.spines['bottom'].set_linewidth(1.5)  # 设置底部边框宽度
ax2.set_ylim(0, 1.3)
# 调整布局并保存
plt.tight_layout()
plt.savefig(r"C:\Users\Lenovo\Desktop\150篇\新建文件夹\combined_plot.svg", dpi=350, bbox_inches='tight', transparent=False)
plt.show()
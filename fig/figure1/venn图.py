import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from matplotlib import patheffects

# 设置字体 - 中文用SimHei，英文用Times New Roman
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.size'] = 14  # 设置基础字体大小

# 创建画布（增大画布尺寸以容纳更大字体）
fig, ax = plt.subplots(figsize=(14, 12))

# 固定总数量
biobert_total = 51211
scibert_total = 40816
xgboost_total = 31216

# 固定三者交集
all_three_intersection = 11068

# 计算两两交集（假设固定值）
xgboost_scibert_intersection = 16904  # XGBoost 和 SciBERT 的交集
xgboost_biobert_intersection = 12463  # XGBoost 和 BioBERT 的交集
scibert_biobert_intersection = 16201  # SciBERT 和 BioBERT 的交集

# 计算各集合独占部分
xgboost_only = xgboost_total - (xgboost_scibert_intersection + xgboost_biobert_intersection - all_three_intersection)
scibert_only = scibert_total - (xgboost_scibert_intersection + scibert_biobert_intersection - all_three_intersection)
biobert_only = biobert_total - (xgboost_biobert_intersection + scibert_biobert_intersection - all_three_intersection)

# 绘制Venn图
venn = venn3(
    subsets=(
        xgboost_only,
        scibert_only,
        xgboost_scibert_intersection - all_three_intersection,
        biobert_only,
        xgboost_biobert_intersection - all_three_intersection,
        scibert_biobert_intersection - all_three_intersection,
        all_three_intersection,
    ),
    set_labels=('XGBoost', 'SciBERT', 'BioBERT'),
    set_colors=('#AEC2CD', '#EFE5E4', '#CEB3B8'),
    alpha=0.6,
    ax=ax
)

# 调整Venn图标签字体（全面放大）
for text in venn.set_labels:
    text.set_fontsize(28)  # 集合名称放大
    text.set_fontweight('bold')
    text.set_color('#222222')  # 深色增加可读性

# 调整所有数字标签（特别处理交集数字）
for text in venn.subset_labels:
    if text is not None:
        base_size = 24 if text.get_text() != '11068' else 28  # 交集数字更大
        text.set_fontsize(base_size)
        text.set_fontweight('bold')

        # 特殊处理三模型交集
        if text.get_text() == '11068':
            text.set_color('red')
            text.set_fontsize(30)  # 最大最醒目
            text.set_fontweight('black')  # 最粗
            # 添加白色描边增强对比
            text.set_path_effects([
                patheffects.withStroke(
                    linewidth=3,
                    foreground='white'
                )
            ])

# 调整布局适应大字体
plt.tight_layout(pad=5)

# 设置保存路径
save_path = r"C:\Users\LEGION\Desktop\PNG\venn_newroman.svg"

# 保存为SVG格式
plt.savefig(save_path, format='svg', bbox_inches='tight', dpi=300)

print(f"高清大字体Venn图已保存到: {save_path}")
plt.show()
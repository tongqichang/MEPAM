import matplotlib.pyplot as plt
import numpy as np

# 设置字体
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 自定义颜色
colors = {
    'XGBoost': '#AEC2CD',
    'SciBERT': '#EFE5E4',
    'BioBERT': '#CEB3B8'
}

# 完整十轮数据
epoch_data = {
    'SciBERT': {
        'Accuracy': [0.9886, 0.9886, 0.9810, 0.9772, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886],
        'Precision': [0.9891, 0.9891, 0.9809, 0.9771, 0.9887, 0.9887, 0.9887, 0.9887, 0.9887, 0.9887],
        'Recall': [0.9886, 0.9886, 0.9810, 0.9772, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886],
        'F1 Score': [0.9887, 0.9887, 0.9809, 0.9771, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886, 0.9886],
        'AUC': [0.9925, 0.9925, 0.9708, 0.9628, 0.9870, 0.9870, 0.9870, 0.9870, 0.9870, 0.9870]
    },
    'XGBoost': {
        'Accuracy': [0.9885, 0.9890, 0.9825, 0.9780, 0.9875, 0.9880, 0.9888, 0.9892, 0.9878, 0.9882],
        'Precision': [0.9505, 0.9510, 0.9450, 0.9420, 0.9495, 0.9505, 0.9512, 0.9520, 0.9485, 0.9495],
        'Recall': [0.9605, 0.9610, 0.9550, 0.9520, 0.9595, 0.9605, 0.9612, 0.9620, 0.9585, 0.9595],
        'F1 Score': [0.9745, 0.9750, 0.9700, 0.9670, 0.9735, 0.9745, 0.9752, 0.9760, 0.9725, 0.9735],
        'AUC': [0.9855, 0.9860, 0.9800, 0.9770, 0.9845, 0.9855, 0.9862, 0.9870, 0.9835, 0.9845]
    },
    'BioBERT': {
        'Accuracy': [0.9915, 0.9920, 0.9905, 0.9890, 0.9910, 0.9915, 0.9920, 0.9925, 0.9905, 0.9910],
        'Precision': [0.9625, 0.9630, 0.9605, 0.9580, 0.9610, 0.9620, 0.9630, 0.9640, 0.9600, 0.9610],
        'Recall': [0.9685, 0.9690, 0.9665, 0.9640, 0.9670, 0.9680, 0.9690, 0.9700, 0.9660, 0.9670],
        'F1 Score': [0.9815, 0.9820, 0.9805, 0.9780, 0.9800, 0.9810, 0.9820, 0.9830, 0.9790, 0.9800],
        'AUC': [0.9895, 0.9900, 0.9885, 0.9870, 0.9890, 0.9895, 0.9900, 0.9910, 0.9880, 0.9890]
    }
}

# 计算均值和标准差
train_data = {}
error_bars = {}
for model in ['XGBoost', 'SciBERT', 'BioBERT']:
    train_data[model] = [np.mean(epoch_data[model][metric]) for metric in
                         ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC']]
    error_bars[model] = [np.std(epoch_data[model][metric]) for metric in
                         ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC']]

# 创建画布
fig, ax = plt.subplots(figsize=(15, 8))
x = np.arange(len(train_data['XGBoost']))
width = 0.25
gap = 0.15

positions = {
    'XGBoost': x - width - gap / 2,
    'SciBERT': x,
    'BioBERT': x + width + gap / 2
}

# 绘制带误差条的柱状图 (修改了error_kw参数使误差条更细)
for model in ['XGBoost', 'SciBERT', 'BioBERT']:
    ax.bar(positions[model], train_data[model], width, label=model,
           color=colors[model], yerr=error_bars[model],
           error_kw=dict(lw=1, capsize=3, capthick=1, ecolor='black'))

# 设置图表属性
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC']
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=24)
ax.set_ylabel('Score', fontsize=24)
ax.set_ylim(0.94, 1.005)
ax.tick_params(axis='both', which='major', labelsize=22)

# 智能调整数值标签位置
for i, metric in enumerate(metrics):
    for model_idx, model in enumerate(['XGBoost', 'SciBERT', 'BioBERT']):
        # 动态计算最小安全高度
        safe_height = train_data[model][i] + error_bars[model][i] + 0.003

        # 特殊处理Accuracy和AUC的错位
        if metric == 'Accuracy':
            vertical_offsets = [0.006, 0.010, 0.008]  # XGBoost低, SciBERT高, BioBERT中
            y_pos = max(safe_height, train_data[model][i] + vertical_offsets[model_idx])
        elif metric == 'AUC':
            vertical_offsets = [0.009, 0.007, 0.011]  # XGBoost高, SciBERT中, BioBERT更高
            y_pos = max(safe_height, train_data[model][i] + vertical_offsets[model_idx])
        else:
            y_pos = max(safe_height, train_data[model][i] + 0.008)  # 默认高度

        # 水平轻微错位
        x_offset = 0.02 if model == 'XGBoost' else (-0.02 if model == 'BioBERT' else 0)

        ax.text(positions[model][i] + x_offset, y_pos,
                f'{train_data[model][i]:.4f}',
                ha='center', va='bottom', fontsize=16)

# 调整图例位置
legend = ax.legend(fontsize=22, loc='upper center',
                   bbox_to_anchor=(0.5, 1.03),
                   ncol=3, frameon=False)

# 微调顶部边距
plt.subplots_adjust(top=0.88)

# 保存结果
save_path = r"C:\Users\LEGION\Desktop\PNG\test_evaluation_newroman.svg"
plt.savefig(save_path, format='svg', bbox_inches='tight')

print(f"优化后的评估图已保存到: {save_path}")
plt.show()
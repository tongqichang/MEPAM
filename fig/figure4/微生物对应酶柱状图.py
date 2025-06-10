import numpy as np
import matplotlib.pyplot as plt

enzyme_config = {
    'S.cerevisiae': [
        {'enzyme': 'cellulase', 'count': 90, 'percentage': 4.1, 'color': '#CBB2B6'},
        {'enzyme': 'β-glucosidase', 'count': 78, 'percentage': 3.6, 'color': '#ABBFCA'},
        {'enzyme': 'xylitol dehydrogenase', 'count': 75, 'percentage': 3.5, 'color': '#FBFBE6'}
    ],
    'E.coli': [
        {'enzyme': 'alcohol dehydrogenase', 'count': 54, 'percentage': 2.8, 'color': '#FDE8DE'},
        {'enzyme': 'lactate dehydrogenase', 'count': 72, 'percentage': 3.7, 'color': '#F5EFEE'},
        {'enzyme': 'citrate synthase', 'count': 24, 'percentage': 1.22, 'color': '#949EAC'}
    ],
    'T.reesei': [
        {'enzyme': 'cellulase', 'count': 583, 'percentage': 55.5, 'color': '#CBB2B6'},
        {'enzyme': 'β-glucosidase', 'count': 88, 'percentage': 8.4, 'color': '#ABBFCA'},
        {'enzyme': 'cellobiohydrolase', 'count': 98, 'percentage': 9.3, 'color': '#7D7D7D'}
    ]
}

microbe_list = list(enzyme_config.keys())

enzyme_name_list, per_list, color_list = [], [], []
for microbe in microbe_list:
    sub_dict = enzyme_config[microbe]
    for item in sub_dict:
        enzyme_name_list.append(item['enzyme'])
        per_list.append(item['percentage'])
        color_list.append(item['color'])

group = len(microbe_list)
bar_width = .2
bar_gap = .05
plot_ind = []
for i in range(group):
    min_ind = -1*bar_width-bar_gap
    max_ind = bar_width+bar_gap
    plot_ind += [i+min_ind, i, i+max_ind]

fig = plt.figure(figsize=(10, 6))
plt.rcParams["font.family"] = 'Times New Roman'
fig.subplots_adjust(hspace=0.05)

# 坐标轴设置
BREAK_POINT = 5.5
UPPER_LIMIT = 100
LOWER_LIMIT = 6

ax1 = fig.add_subplot(211)
bars = plt.bar(plot_ind, per_list, bar_width, color=color_list, edgecolor="#565656")
plt.ylim(BREAK_POINT, UPPER_LIMIT)
plt.yticks([20, 40, 60, 80, 100], fontsize=20)

# 百分比标签（上半部分）
for ind, per in zip(plot_ind, per_list):
    if per > BREAK_POINT:
        plt.text(ind, per + (3 if per < 50 else 5), f"{per:.1f}%",
               ha='center', va='bottom', fontsize=20)

# 微生物名称标签（改为Times New Roman斜体）
for ind, microbe in enumerate(microbe_list):
    plt.text(ind, 97, microbe,
            ha='center', va='top', fontsize=20, fontstyle='italic')

plt.xticks([])
for grid_ind in range(0, group-1):
    plt.axvline(x=grid_ind+.5, color='#b2bec3', linestyle='--', linewidth=1)

ax2 = fig.add_subplot(212)
ax2.bar(plot_ind, per_list, bar_width, color=color_list, edgecolor="#565656")
plt.ylim(0, LOWER_LIMIT)
plt.yticks([0, 1, 2, 3, 4, 5], fontsize=20)

# 小值标签
for ind, per in zip(plot_ind, per_list):
    if per <= BREAK_POINT:
        plt.text(ind, per + 0.3, f"{per:.1f}%",
               ha='center', va='bottom', fontsize=20)

# 酶名称标签（不换行，保持原始名称）
plt.xticks(plot_ind, enzyme_name_list, fontsize=20, rotation=45, ha='right')

for grid_ind in range(0, group-1):
    plt.axvline(x=grid_ind+.5, color='#b2bec3', linestyle='--', linewidth=1)

plt.ylabel('Proportion (%)', fontsize=20, weight='regular')

# 隐藏边界线
ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)

# 添加断裂符号
d = 0.5
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
             linestyle="none", color='k', mec='k', mew=1, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

plt.savefig(r'C:\Users\LEGION\Desktop\微生物中的酶.svg',
           dpi=330, bbox_inches='tight', format='svg')
plt.show()
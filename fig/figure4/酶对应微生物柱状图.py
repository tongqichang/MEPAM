import numpy as np
import matplotlib.pyplot as plt

enzyme_config = {
    'cellulase': [
        {'microbe': 'T.reesei', 'count': 522, 'percentage': 66.8, 'color': '#F5EFEE'},
        {'microbe': 'S.cerevisiae', 'count': 80, 'percentage': 10.2, 'color': '#CBB2B6'},
        {'microbe': 'A.niger', 'count': 23, 'percentage': 2.9, 'color': '#949EAC'}

    ],
    'β_glucosidase': [
        {'microbe': 'T.reesei', 'count': 85, 'percentage': 28.5, 'color': '#F5EFEE'},
        {'microbe': 'S.cerevisiae', 'count': 82, 'percentage': 27.5, 'color': '#CBB2B6'},
        {'microbe': 'A.niger', 'count': 16, 'percentage': 5.4, 'color': '#949EAC'}

    ],
    'alcohol_dehydrogenase': [
        {'microbe': 'S.cerevisiae', 'count': 84, 'percentage': 46.4, 'color': '#CBB2B6'},
        {'microbe': 'E.coli', 'count': 55, 'percentage': 30.4, 'color': '#ABBFCA'},
        {'microbe': 'K.marxianus', 'count': 8, 'percentage': 4.4, 'color': '#FDE8DE'}
    ],
    'xylose_reductase': [
        {'microbe': 'S.cerevisiae', 'count': 71, 'percentage': 63.4, 'color': '#CBB2B6'},
        {'microbe': 'E.coli', 'count': 8, 'percentage': 7.1, 'color': '#ABBFCA'},
        {'microbe': 'P.stipitis', 'count': 6, 'percentage': 5.4, 'color': '#FBFBE6'}
    ]
}

enzyme_list = enzyme_config.keys()

sp_name_list, per_list, color_list = [], [], []
for enzyme in enzyme_list:
    sub_dict = enzyme_config[enzyme]
    for item in sub_dict:
        sp_name_list.append(item['microbe'])
        per_list.append(item['percentage'])
        color_list.append(item['color'])

group = len(enzyme_list)
bar_width = .2
bar_gap = .05
plot_ind = []
for i in range(group):
    min_ind = -1*bar_width-bar_gap
    max_ind = bar_width+bar_gap
    plot_ind += [i+min_ind, i, i+max_ind]

fig = plt.figure(figsize=(10, 6))
plt.rcParams["font.family"] = 'Times New Roman'
fig.subplots_adjust(hspace=0.05)  # adjust space between Axes

ax1 = fig.add_subplot(211)
plt.bar(plot_ind, per_list, bar_width, color=color_list, edgecolor="#565656")
plt.ylim(17, 100)
plt.yticks(fontsize=20)
for ind, per in zip(plot_ind, per_list):
    if per > 17 and ind == plot_ind[3]:
        plt.text(ind, per+14, f"{per}%", ha='center', va='bottom', fontsize=20)
    elif per > 17:
        plt.text(ind, per+5, f"{per}%", ha='center', va='bottom', fontsize=20)
for ind, enzyme in enumerate(enzyme_list):
    plt.text(ind, 97, enzyme.replace('β_', 'β-').replace('_', '\n'), ha='center', va='top', fontsize=20)
plt.xticks([])
for grid_ind in range(0, group-1):
    plt.axvline(x=grid_ind+.5, color='#b2bec3', linestyle='--', linewidth=1)

ax2 = fig.add_subplot(212)
ax2.bar(plot_ind, per_list, bar_width, color=color_list, edgecolor="#565656")
for ind, per in zip(plot_ind, per_list):
    if per < 17:
        plt.text(ind, per+1.5, f"{per}%", ha='center', va='bottom', fontsize=20)
plt.ylim(0, 18)
plt.yticks([0, 5, 10, 15], fontsize=20)
plt.xticks(plot_ind, ['']*len(plot_ind))

# Create microbial names in Times New Roman italic (not Latin italic)
plt.xticks(plot_ind, sp_name_list, fontsize=20, rotation=45, ha='right',
           fontstyle='italic', fontfamily='Times New Roman')

for grid_ind in range(0, group-1):
    plt.axvline(x=grid_ind+.5, color='#b2bec3', linestyle='--', linewidth=1)

plt.ylabel('Proportion (%)', fontsize=20, weight='regular')

ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
d = .5  # proportion of vertical to horizontal extent of the slanted line
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# Save as SVG to the specified path
plt.savefig(r'C:\Users\LEGION\Desktop\酶中的微生物.svg',
           dpi=330, bbox_inches='tight', format='svg')
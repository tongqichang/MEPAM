import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# Set font to Times New Roman
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12

# Data
labels = ['Saccharomyces', 'Escherichia', 'Trichoderma',
          'Bacillus', 'Aspergillus', 'Lactobacillus',
          'Pichia', 'Streptomyces', 'Clostridium', 'Others']
sizes = [5628, 4929, 2124, 869, 597, 514, 260, 258, 245, 2437]
colors = ['#CBB2B6', '#ABBFCA', '#FBFBE6', '#FDE8DE', '#E6F2D9',
          '#949EAC', '#D4C5C7', '#7D7D7D', '#E6C3B5', '#D3D3D3']

# Calculate radius proportions
radii = np.sqrt(sizes)

# Create figure
fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

# Create pie chart without labels and percentages
wedges = ax.pie(
    sizes,
    colors=colors,
    startangle=140,
    wedgeprops={"linewidth": 1.5, "edgecolor": "black"},
    autopct=None  # 移除百分比显示
)[0]

# Adjust wedge radii to match the enzyme chart's radius adjustment formula
for i, wedge in enumerate(wedges):
    wedge.set_radius(0.5 + 0.5 * radii[i] / max(radii))  # Same radius adjustment as the enzyme chart

ax.axis('equal')
plt.title('Microbial Species Distribution', fontsize=14, pad=20)

plt.savefig(r"C:\Users\LEGION\Desktop\microbial_distribution.svg", format='svg', bbox_inches='tight')
plt.show()

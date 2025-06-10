import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# Set font to Times New Roman
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12

# Data
sizes = [6372, 4054, 2983,516, 125, 1513]
colors = ['#CBB2B6', '#E6F2D9', '#FBFBE6', '#FDE8DE', '#ABBFCA', '#949EAC']

# Calculate radius proportions
radii = np.sqrt(sizes)

# Create figure
fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

# Create pie chart with no labels or percentages
wedges = ax.pie(
    sizes,
    colors=colors,
    startangle=140,
    wedgeprops={"linewidth": 1.5, "edgecolor": "black"},
    labels=None,  # Remove labels
    autopct=None,  # Remove percentages
)

# Adjust wedge radii
for i, wedge in enumerate(wedges[0]):
    wedge.set_radius(0.5 + 0.5 * radii[i] / max(radii))

ax.axis('equal')
plt.title('Enzyme Classification Distribution', fontsize=14, pad=20)

plt.savefig(r"C:\Users\LEGION\Desktop\enzyme_distribution.svg", format='svg', bbox_inches='tight')
plt.show()

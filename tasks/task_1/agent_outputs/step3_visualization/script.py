import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data and genes of interest
data = pd.read_csv('/data0/data.csv')
genes_of_interest = pd.read_csv('/outputs/step2_identify_extremes/genes_of_interest.csv')

# Extract the genes with the strongest correlations
genes = genes_of_interest['gene'].tolist()

# Create a scatter plot for each gene
plt.figure(figsize=(12, 6))
for i, gene in enumerate(genes):
    plt.subplot(1, 2, i+1)
    sns.scatterplot(x=data[gene], y=data['drug_response'], hue=data['cell_line'], palette='viridis', s=100, edgecolor='w', alpha=0.7)
    plt.title(f'{gene} vs Drug Response')
    plt.xlabel(f'{gene} Expression')
    plt.ylabel('Drug Response')
    plt.axhline(y=data['drug_response'].mean(), color='r', linestyle='--', label='Mean Drug Response')
    plt.legend()

plt.tight_layout()
plt.savefig('/outputs/step3_visualization/gene_expression_vs_drug_response.pdf')
plt.show()
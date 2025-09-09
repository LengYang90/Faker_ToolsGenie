import pandas as pd

# Load the correlations
gene_correlations = pd.read_csv('/outputs/step1_data_prep/gene_correlations.csv', index_col=0)

# Identify the genes with the strongest positive and negative correlations
strongest_positive_gene = gene_correlations['correlation'].idxmax()
strongest_negative_gene = gene_correlations['correlation'].idxmin()

# Save the results
genes_of_interest = pd.DataFrame({
    'gene': [strongest_positive_gene, strongest_negative_gene],
    'correlation': [gene_correlations.loc[strongest_positive_gene, 'correlation'],
                    gene_correlations.loc[strongest_negative_gene, 'correlation']]
})
genes_of_interest.to_csv('/outputs/step2_identify_extremes/genes_of_interest.csv', index=False)
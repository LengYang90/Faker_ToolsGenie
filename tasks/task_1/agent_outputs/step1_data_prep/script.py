import pandas as pd

# Load the data
data = pd.read_csv('/data0/data.csv')

# Calculate the correlation between each gene and drug response
gene_columns = data.columns[2:]  # All columns except 'cell_line' and 'drug_response'
correlations = data[gene_columns].corrwith(data['drug_response'])

# Save the correlations to a CSV file
correlations.to_csv('/outputs/step1_data_prep/gene_correlations.csv', header=['correlation'])
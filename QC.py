import pandas as pd

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')

print(len(exp_df))
print(exp_df.cond_id.value_counts())
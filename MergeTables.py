import pandas as pd

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')
cond_df = pd.read_excel(r'input/Conditions_table.xlsx')

def merge_ID():
    cond_df = cond_df[['Cond_id', 'Cond_name']]
    merged_inner = pd.merge(left=exp_df, right=cond_df, left_on='cond_id', right_on='Cond_id')
    merged_inner.drop(['Cond_id', 'Unnamed: 0'], axis=1, inplace=True)
    merged_inner.to_csv('output/experiment_table.csv', sep=';')

merge_ID()

'''
# This function doubles the input value
def double(x):
    return 2*x
# Apply this function to double every value in a specified column
df.column1 = df.column1.apply(double)
# Lambda functions can also be supplied to `apply()`
df.column2 = df.column2.apply(lambda x: 3*x)
# Applying to a row requires it to be called on the entire DataFrame
df['newColumn'] = df.apply(lambda row: row['column1']*1.5+row['column2'],axis=1)
'''
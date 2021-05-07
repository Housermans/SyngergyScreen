import pandas as pd

def load_condition(cond_id):
    exp_df = pd.read_csv('output/experiment_table_cut.csv', ';').drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
    # exp_df = pd.read_csv('file_name.csv').drop(['unnamed 0'], axis=1)
    cond_df = exp_df[exp_df['cond_id'] == cond_id]
    # cond_df = exp_df.loc[exp_df['cond_id'] == cond_id]
    return cond_df

lapabini = load_condition(8)
lapabini['Lapa_round'] = round(lapabini['Lapa'],3)
lapabini['Bini_round'] = round(lapabini['Bini'],3)
print(lapabini['Bini_round'].value_counts())



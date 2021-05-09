import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from find_apply_cutoff import summarize_per_well

def load_condition(cond_id):
    exp_df = pd.read_csv('output/experiment_table_cut.csv', ';').drop(['well_id','Unnamed: 0',
                                                                       'Unnamed: 0.1'], axis=1)
    cond_df = exp_df[exp_df['cond_id'] == cond_id]
    return cond_df

def synergy_table(body, lapa, bini, plot=False):
    lapabini = load_condition(body)
    lapa = load_condition(lapa)
    bini = load_condition(bini)

    table = pd.concat([lapabini, lapa, bini], axis=0)
    table['Lapa_round'] = round(table['Lapa'],3)
    table['Bini_round'] = round(table['Bini'],3)
    mean_ratio = table[['Lapa_round', 'Bini_round', 'norm_ratio']].groupby(['Lapa_round','Bini_round'])\
        .mean().reset_index().rename(columns={'norm_ratio':'mean'})
    sem_ratio = table[['Lapa_round', 'Bini_round', 'norm_ratio']].groupby(['Lapa_round','Bini_round'])\
        .sem().reset_index().rename(columns={'norm_ratio':'sem'})
    result = pd.concat([mean_ratio, sem_ratio['sem']], axis=1, join="inner")
    if plot:
        heatmap(result, plot=plot)
    return result

def heatmap(df, plot=False):
    # creates broad table for heatmap
    syn_table = pd.pivot_table(df, values='mean', index=['Lapa_round'], columns=['Bini_round'])
    syn_table.sort_index(ascending=False, inplace=True)

    # apply heat map if plot argument is given as True
    if plot:
        sns.heatmap(syn_table, annot=True, cmap='RdYlGn')
        plt.show()
    return syn_table

df_broad = synergy_table(8, 4, 6, plot=True)
df_broad.to_excel('output/synergy_2.xlsx')

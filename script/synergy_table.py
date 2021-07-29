import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_condition(cond_id):
    exp_df = pd.read_csv('output/experiment_table_cut.csv', ';')
    cond_df = exp_df[exp_df['cond_id'] == cond_id]
    return cond_df

def synergy_table(body, lapa, bini, plot=False, title='lapabini', save=True):
    lapabini = load_condition(body)
    lapa = load_condition(lapa)
    bini = load_condition(bini)

    table = pd.concat([lapabini, lapa, bini], axis=0)
    count = table[['Lapa_round', 'Bini_round', 'norm_ratio']].groupby(['Lapa_round', 'Bini_round']) \
        .count().reset_index().rename(columns={'norm_ratio': 'count'})
    mean_ratio = table[['Lapa_round', 'Bini_round', 'norm_ratio']].groupby(['Lapa_round','Bini_round'])\
        .mean().reset_index().rename(columns={'norm_ratio':'mean'})
    sem_ratio = table[['Lapa_round', 'Bini_round', 'norm_ratio']].groupby(['Lapa_round','Bini_round'])\
        .sem().reset_index().rename(columns={'norm_ratio':'sem'})
    result = pd.concat([mean_ratio, sem_ratio['sem'], count['count']], axis=1, join="inner")
    well1 = []
    well1_ratio = []
    well2 = []
    well2_ratio = []
    for index, row in result.iterrows():
        titration = table[((table['Lapa_round'] == row['Lapa_round']) & (table['Bini_round'] == row['Bini_round']))]
        wells_list = titration['well_name'].tolist()
        ratio_list = titration['norm_ratio'].tolist()
        if len(titration) == 2:
            well1.append(wells_list[0])
            well1_ratio.append(ratio_list[0])
            well2.append(wells_list[1])
            well2_ratio.append(ratio_list[1])
        elif len(titration) == 1:
            well1.append(wells_list[0])
            well1_ratio.append(ratio_list[0])
            well2.append(None)
            well2_ratio.append(None)
        else:
            well1.append(None)
            well1_ratio.append(None)
            well2.append(None)
            well2_ratio.append(None)
    result['well1'] = well1
    result['well1_ratio'] = well1_ratio
    result['well2'] = well2
    result['well2_ratio'] = well2_ratio
    if plot:
        heatmap(result, plot=plot, title=title)
    if save:
        result.to_excel(f'output/synergy_{title}.xlsx')
    return result

def heatmap(df, plot=False, title="lapabini"):
    # creates broad table for heatmap
    syn_table = pd.pivot_table(df, values='mean', index=['Lapa_round'], columns=['Bini_round'])
    syn_table.sort_index(ascending=False, inplace=True)

    # apply heat map if plot argument is given as True
    if plot:
        plt.figure(figsize=(10,7))
        sns.heatmap(syn_table, annot=True, cmap='RdYlGn')
        plt.savefig(f'figures/heatmap_{title}.png')
        plt.close()
    return syn_table

def drug_response(drug_cond_id, plot=False, drug='NA', save=True):
    drug_df = load_condition(drug_cond_id)
    print(drug_df.columns)
    if drug == 'NA':
        drug = input('type exact drug name (4 letters)')
    drug_round = drug + '_round'
    print(drug_round)
    count = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round]) \
        .count().reset_index().rename(columns={'norm_ratio': 'count'})
    mean_ratio = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round])\
        .mean().reset_index().rename(columns={'norm_ratio':'mean'})
    sem_ratio = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round])\
        .sem().reset_index().rename(columns={'norm_ratio':'sem'})
    result = pd.concat([mean_ratio, sem_ratio['sem'], count['count']], axis=1, join="inner")
    print(result.head())
    well1 = []
    well1_ratio = []
    well2 = []
    well2_ratio = []
    for index, row in result.iterrows():
        titration = drug_df[(drug_df[drug_round] == row[drug_round])]
        wells_list = titration['well_name'].tolist()
        ratio_list = titration['norm_ratio'].tolist()
        if len(titration) == 2:
            well1.append(wells_list[0])
            well1_ratio.append(ratio_list[0])
            well2.append(wells_list[1])
            well2_ratio.append(ratio_list[1])
        elif len(titration) == 1:
            well1.append(wells_list[0])
            well1_ratio.append(ratio_list[0])
            well2.append(None)
            well2_ratio.append(None)
        else:
            well1.append(None)
            well1_ratio.append(None)
            well2.append(None)
            well2_ratio.append(None)
    result['well1'] = well1
    result['well1_ratio'] = well1_ratio
    result['well2'] = well2
    result['well2_ratio'] = well2_ratio
    # if plot:
    #    heatmap(result, plot=plot, title=title)
    if save:
        result.to_excel(f'output/response_{drug}.xlsx')
    return result

# df_lapabini = synergy_table(8, 4, 6, plot=True, title='lapa_vs_bini', save=True)
# df_lapabinivino = synergy_table(9,5,7, plot=True, title='lapa_vs_bini_vino120', save=True)
drug_response(3, drug='Navi')
drug_response(4, drug='Lapa')
drug_response(6, drug='Bini')
drug_response(11, drug='Vino')
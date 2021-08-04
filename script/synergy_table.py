import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

experiment = "E21-004_RAS13"
print(f"WARNING: working on {experiment}, if you are working in a new file, please update the experiment variable!")

def load_condition(cond_id):
    exp_df = pd.read_csv(f'{experiment}/output/experiment_table_cut.csv', ';')
    cond_df = exp_df[exp_df['cond_id'] == cond_id]
    return cond_df

def synergy_table(body, lapa, bini, plot=False, save=True):
    lapabini = load_condition(body)
    lapa = load_condition(lapa)
    bini = load_condition(bini)

    cond_df = pd.read_csv(f'{experiment}/output/condition_data.csv', ';')
    fancy_name = cond_df.loc[cond_df['cond_id'] == body, 'fancy_name'].iloc[0]
    cond_name = cond_df.loc[cond_df['cond_id'] == body, 'cond_name'].iloc[0]
    title = fancy_name


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
        heatmap(result, plot=plot, short_title=cond_name, fancy = fancy_name)
    if save:
        result.to_excel(f'{experiment}/output/synergy_{cond_name}.xlsx')
    return result

def heatmap(df, plot=False, short_title="lapabini", fancy = 'heatmap'):
    # creates broad table for heatmap
    syn_table = pd.pivot_table(df, values='mean', index=['Lapa_round'], columns=['Bini_round'])
    syn_table.sort_index(ascending=False, inplace=True)

    # apply heat map if plot argument is given as True
    if plot:
        plt.figure(figsize=(10,7))
        sns.heatmap(syn_table, annot=True, cmap='RdYlGn', vmin=0, vmax=1)
        plt.xlabel('Binimetinib Dose (mM)')
        plt.ylabel('Lapatinib Dose(mM)')
        plt.title(f'Proportion of organoids alive in condition: {fancy}')
        plt.savefig(f'{experiment}/figures/heatmap_{short_title}.png')
        plt.close()
    return syn_table

def drug_response(drug_cond_id, plot=True, save=True):
    drug_df = load_condition(drug_cond_id)
    cond_df = pd.read_csv(f'{experiment}/output/condition_data.csv', ';')
    fancy_name = cond_df.loc[cond_df['cond_id'] == drug_cond_id, 'fancy_name'].iloc[0]
    cond_name = cond_df.loc[cond_df['cond_id'] == drug_cond_id, 'cond_name'].iloc[0]
    drug_name = cond_df.loc[cond_df['cond_id'] == drug_cond_id, 'Drug1'].iloc[0]
    drug_round = drug_name[:4] + '_round'
    # print(drug_round)
    # gets the values to fill in the drug response excel format
    count = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round]) \
        .count().reset_index().rename(columns={'norm_ratio': 'count'})
    mean_ratio = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round])\
        .mean().reset_index().rename(columns={'norm_ratio':'mean'})
    sem_ratio = drug_df[[drug_round, 'norm_ratio']].groupby([drug_round])\
        .sem().reset_index().rename(columns={'norm_ratio':'sem'})
    result = pd.concat([mean_ratio, sem_ratio['sem'], count['count']], axis=1, join="inner")
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
    result['lower'] = result['mean'] - 1.96 * result['sem']
    result['upper'] = result['mean'] + 1.96 * result['sem']
    # print(result.head())
    if plot:
        plt.plot(result[drug_round], result['mean'])
        plt.fill_between(result[drug_round], result['lower'], result['upper'], alpha=0.5)
        plt.xscale('log')
        plt.title(fancy_name)
        plt.ylim(0,1)
        plt.xlim(0.0045,30)
        plt.xlabel(f'Log of {drug_name} concentration in nano molar (nM)')
        plt.ylabel('normalized proportion of organoids alive for given dose')
        plt.savefig(f'{experiment}/figures/drugresponse_{cond_name}.png')
        # plt.show()
        plt.close()
    if save:
        result.to_excel(f'{experiment}/output/response_{cond_name}.xlsx')
    return result

df_lapabini = synergy_table(8, 4, 6, plot=True, save=True)
df_lapabinivino = synergy_table(9,5,7, plot=True, save=True)
navi = drug_response(3)
lapa = drug_response(4)
lapavino = drug_response(5)
bini = drug_response(6)
binivino = drug_response(7)
vino = drug_response(11)

# bini.plot(x='Bini_round', y='mean', logx=True)
# plt.show()

# sns.lineplot(data=navi, x='Navi_round', y="norm_ratio")
# plt.show()
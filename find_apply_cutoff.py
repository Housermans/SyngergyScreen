import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')
cond_table = pd.read_excel("input/Conditions_table.xlsx")
cond_table.sort_values(by=['Cond_id'], axis=0, inplace=True)
cond_table.reset_index(inplace=True, drop=True)

def select_condition(select_id, maxsize=50000, plot=False, title='NA', drop=[], cutoff=None):
    select_df = exp_df.loc[exp_df['cond_id'] == select_id]
    cond_name = select_df['Cond_name'].unique()[0]
    organoid_df = pd.DataFrame(columns=['Unnamed: 0', 'ScreenName', 'ScreenID', 'PlateName', 'PlateID',
       'MeasurementDate', 'MeasurementID', 'WellName', 'Row', 'Column',
       'Field', 'Timepoint', 'Object Number', 'X', 'Y', 'Bounding Box',
       'mean_intensity', 'cell_round', 'cell_area', 'object_no'])
    for index, row in select_df.iterrows():
        temp_df = pd.read_csv(row['file_path'], sep=';')
        organoid_df = pd.concat([organoid_df, temp_df])
    # reset index omdat je verschillende dataframes aan elkaar hebt geplakt, anders krijg je rare uitkomsten met drop
    organoid_df.reset_index(inplace=True)
    organoid_df = organoid_df.drop(organoid_df[organoid_df.cell_area > maxsize].index)
    organoid_df['cond_name'] = cond_name
    if drop:
        for item in drop:
            # print('dropping', item)
            if not item in organoid_df['WellName'].unique():
                # print(f'{item} not found')
                return None
            organoid_df = organoid_df.drop(organoid_df[organoid_df.WellName == item].index)
    # if argument plot is set as true in function call, two summary plots are created for this condition
    # print(organoid_df['WellName'].unique())
    if plot:
        if (title == 'NA'):
            title = cond_name
        summarize_condition(organoid_df, title=title)
        summarize_per_well(organoid_df, title=title, drop=drop)
    if cutoff:
        organoid_df['alive_bool'] = np.where(organoid_df['cell_round'] > cutoff, True, False)
        organoid_df['status'] = np.where(organoid_df['alive_bool'], 'alive', 'dead')
    organoid_df.to_csv(f'output/conditions/{cond_name}_organoids.csv', sep=';')
    return organoid_df

def summarize_per_well(df, title="Organoids", drop=[]):
    wells = df['WellName'].unique()
    n_wells = len(wells) + len(drop)
    rows = int(n_wells / 8)
    columns = 8
    count = 1
    plt.subplots(rows, columns, sharey='row', sharex='col')
    for well in wells:
        if well in drop:
            ax = plt.subplot(rows, columns, count)
            plt.plot([])
            plt.title(f"{well} blinded")
            plt.xlim(0, 1)
            ax.set_xticks([0.5])
            ax.set_xticklabels([0.5])
            count += 1
            continue
        well_df = df[df['WellName'] == well]
        ax = plt.subplot(rows,columns,count)
        plt.title(well)
        plt.hist(well_df['cell_round'], density=True, stacked=True)
        plt.xlim(0,1)
        ax.set_xticks([0.5])
        ax.set_xticklabels([0.5])
        count += 1
    plt.subplots_adjust(wspace=0.25)
    plt.suptitle(title)
    plt.show()

def violin_plot(df1, df2, cutoff=None):
    together = pd.concat([df1, df2])
    plt.subplot(1,2,1)
    sns.set_theme(style="whitegrid")
    sns.violinplot(y=together['cell_round'], x=together['cond_name'])
    if cutoff:
        plt.axhline(y=cutoff)
    plt.title(f'{df1["cond_name"].unique()[0]} vs {df2["cond_name"].unique()[0]}')
    plt.show()

def summarize_condition(df, title='Organoids'):
    fig=plt.figure(figsize=(10,8))
    plt.subplot(121)
    plt.hist(df['cell_round'])
    plt.xlabel('Roundness')
    plt.ylabel('Count')
    plt.subplot(122)
    plt.scatter(df['cell_round'], df['cell_area'])
    plt.xlabel('Roundness')
    plt.ylabel('Area')
    plt.subplots_adjust(wspace=0.35)
    fig.suptitle(title)
    plt.show()

def classify_alive(df, cut_off):
    cut_off = cut_off/100
    alive = 0
    for index, row in df.iterrows():
        if row['cell_round'] > cut_off:
            alive += 1
    return alive/len(df)

def plt_cutoff(df, lower=0.5, upper=0.9, plot=False, title=''):
    lower_int = int(lower * 100)
    upper_int = int(upper * 100)
    range_int = range(lower_int, upper_int + 1, 1)
    pct_alive = []
    for value in range_int:
        pct_alive.append(classify_alive(df, value))
    if plot:
        ax = plt.subplot()
        plt.bar(range_int, pct_alive)
        x_ticks = list(range(lower_int, upper_int + 1, 5))
        x_ticklabels = [x / 100 for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels)
        if title:
            plt.title(f"Percentage alive for cut-off in {title}")
        plt.ylabel('Percentage Alive')
        plt.xlabel('Cut-off Value')
        plt.show()
    return pct_alive

def plt_diff(neg_df, pos_df, lower=0.5, upper=0.9, plot=False):
    upper_int = int(upper * 100)
    lower_int = int(lower * 100)
    range_int = range(lower_int, upper_int + 1, 1)
    if plot:
        neg = plt_cutoff(neg_df, lower=lower, upper=upper, plot=True, title='Negative Control')
        pos = plt_cutoff(pos_df, lower=lower, upper=upper, plot=True, title='Positive Control')
    else:
        neg = plt_cutoff(neg_df, lower=lower, upper=upper)
        pos = plt_cutoff(pos_df, lower=lower, upper=upper)
    diff = []
    for i in range(len(neg)):
        diff.append(neg[i] - pos[i])
    if plot:
        ax = plt.subplot()
        plt.bar(range_int, diff)
        x_ticks = list(range(lower_int, upper_int + 1, 5))
        x_ticklabels = [x/100 for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels)
        plt.title('Difference between positive and negative control at cut-off')
        plt.ylabel('Percentage Alive')
        plt.xlabel('Cut-off Value')
        plt.show()
    return diff

def find_cutoff(plot=False):
    negctrl_organoid_df = select_condition(1, plot=plot)
    posctrl_organoid_df = select_condition(2, plot=plot, drop=['K22'])
    diff = plt_diff(negctrl_organoid_df, posctrl_organoid_df, plot=plot)
    cutoff = max(diff)
    if plot:
        violin_plot(negctrl_organoid_df, posctrl_organoid_df, cutoff)
    return cutoff

def save_condition_tables(plot=False):
    cutoff = find_cutoff(plot=plot)
    conditions = exp_df['cond_id'].unique()
    cond_table['mean_round'] = 0
    cond_table['alive'] = 0
    cond_table['total'] = 0
    cond_table['ratio'] = 0
    for condition in conditions:
        df = select_condition(condition, plot=plot, cutoff=cutoff)
        cond_table.at[condition-1,'mean_round'] = df['cell_round'].mean()
        cond_table.at[condition-1,'alive'] = df['alive_bool'].sum()
        cond_table.at[condition-1,'total'] = len(df)
        cond_table.at[condition-1,'ratio'] = df['alive_bool'].sum()/len(df)
    cond_table.to_csv('output/condition_data.csv', sep=';')

save_condition_tables()
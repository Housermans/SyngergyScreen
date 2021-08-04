import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

experiment = "E21-004_RAS13"
print(f"WARNING: working on {experiment}, if you are working in a new file, please update the experiment variable!")

exp_df = pd.read_csv(fr'{experiment}/output/experiment_table.csv', sep=';')
cond_table = pd.read_excel(f"{experiment}/input/Conditions_table.xlsx")
cond_table.sort_values(by=['cond_id'], axis=0, inplace=True)
cond_table.reset_index(inplace=True, drop=True)


# bug fix because apparantly, this script is run from home folder instead of from the script folder.
# TODO: fix the bug permanently by making sure this script runs from the script folder instead.
def convert_file_path(path_with_dots):
    path_without_dots = path_with_dots[3:]
    return path_without_dots


def select_condition(select_id, maxsize=50000, plot=False, title='NA', drop=[], cutoff=None):
    select_df = exp_df.loc[exp_df['cond_id'] == select_id]
    cond_name = select_df['cond_name'].unique()[0]
    organoid_df = pd.DataFrame(columns=['Unnamed: 0', 'ScreenName', 'ScreenID', 'PlateName', 'PlateID',
                                        'MeasurementDate', 'MeasurementID', 'WellName', 'Row', 'Column',
                                        'Field', 'Timepoint', 'Object Number', 'X', 'Y', 'Bounding Box',
                                        'mean_intensity', 'cell_round', 'cell_area', 'object_no'])
    for index, row in select_df.iterrows():
        if row['is_empty']:
            print(row['well_name'], 'is empty! Therefore it is not included in this condition df')
            drop.append(row['well_name'])
        else:
            temp_df = pd.read_csv(convert_file_path(row['file_path']), sep=';')
            organoid_df = pd.concat([organoid_df, temp_df])
    # reset index omdat je verschillende dataframes aan elkaar hebt geplakt, anders krijg je rare uitkomsten met drop
    organoid_df.reset_index(inplace=True)
    organoid_df = organoid_df.drop(organoid_df[organoid_df.cell_area > maxsize].index)
    organoid_df['cond_name'] = cond_name
    if drop:
        for item in drop:
            print('dropping', item)
            if not item in organoid_df['WellName'].unique():
                print(f'{item} not found or has already been dropped')
                continue
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
    organoid_df.to_csv(f'{experiment}/output/conditions/{cond_name}_organoids.csv', sep=';')
    return organoid_df


def summarize_per_well(df, title="Organoids", drop=[]):
    wells = df['WellName'].unique()
    n_wells = len(wells) + len(drop)
    rows = int(n_wells / 8)
    columns = 8
    count = 1
    plt.figure(figsize=(10, 4 * rows))
    plt.subplots(rows, columns, sharey='row', sharex='col')
    for well in wells:
        if well in drop:
            ax = plt.subplot(rows, columns, count)
            plt.plot([])
            plt.title(f"{well} blinded")
            plt.xlim(0, 1)
            plt.ylim(0, 8)
            ax.set_xticks([0.5])
            ax.set_xticklabels([0.5])
            count += 1
            continue
        well_df = df[df['WellName'] == well]
        ax = plt.subplot(rows, columns, count)
        plt.title(well)
        plt.hist(well_df['cell_round'], density=True, stacked=True)
        plt.xlim(0, 1)
        plt.ylim(0, 8)
        ax.set_xticks([0.5])
        ax.set_xticklabels([0.5])
        count += 1
    # plt.subplots_adjust(wspace=0.25)
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(f'{experiment}/figures/summary_per_well_{title}.png')
    # plt.show()
    plt.close()


def violin_plot(df1, df2, cutoff=None):
    together = pd.concat([df1, df2])
    fig = plt.figure(figsize=(8, 10))
    fig.add_subplot(1, 1, 1)
    sns.set_theme(style="whitegrid")
    sns.violinplot(y=together['cell_round'], x=together['cond_name'])
    if cutoff:
        plt.axhline(y=cutoff, color='red')
    plt.title(f'{df1["cond_name"].unique()[0]} vs {df2["cond_name"].unique()[0]}')
    plt.savefig(f'{experiment}/figures/violinplot_{df1.cond_name.unique()[0]}_vs_{df2.cond_name.unique()[0]}.png')
    # plt.show()
    plt.close()


def summarize_condition(df, title='Organoids'):
    fig = plt.figure(figsize=(10, 8))
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
    plt.savefig(f'{experiment}/figures/summarize_condition_{title}')
    # plt.show()
    plt.close()


def classify_alive(df, cut_off):
    cut_off = cut_off / 100
    alive = 0
    for index, row in df.iterrows():
        if row['cell_round'] > cut_off:
            alive += 1
    return alive / len(df)


def plt_cutoff(df, lower=0.5, upper=0.9, plot=False, title=''):
    lower_int = int(lower * 100)
    upper_int = int(upper * 100)
    range_int = range(lower_int, upper_int + 1, 1)
    pct_alive = []
    for value in range_int:
        pct_alive.append(classify_alive(df, value))
    if plot:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot()
        plt.bar(range_int, pct_alive)
        x_ticks = list(range(lower_int, upper_int + 1, 5))
        x_ticklabels = [x / 100 for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels)
        if title:
            plt.title(f"Percentage alive for cut-off in {title}")
        plt.ylabel('Percentage Alive')
        plt.xlabel('Cut-off Value')
        plt.savefig(f'{experiment}/figures/cutoff_{title}')
        # plt.show()
        plt.close()
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
        plt.figure(figsize=(10, 8))
        ax = plt.subplot()
        plt.bar(range_int, diff)
        x_ticks = list(range(lower_int, upper_int + 1, 5))
        x_ticklabels = [x / 100 for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels)
        plt.title('Difference between positive and negative control at cut-off')
        plt.ylabel('Percentage Alive')
        plt.xlabel('Cut-off Value')
        plt.savefig(f'{experiment}/figures/cutoff_diff.png')
        # plt.show()
        plt.close()
    return diff


def find_cutoff(plot=False):
    negctrl_organoid_df = select_condition(1, plot=plot)
    posctrl_organoid_df = select_condition(2, plot=plot)
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
        cond_table.at[condition - 1, 'mean_round'] = df['cell_round'].mean()
        cond_table.at[condition - 1, 'alive'] = df['alive_bool'].sum()
        cond_table.at[condition - 1, 'total'] = len(df)
    cond_table.to_csv(f'{experiment}/output/condition_data.csv', sep=';')
    return cutoff


def normalize(plot=False):
    cond_table = pd.read_csv(f'{experiment}/output/condition_data.csv', sep=';')
    cond_table['ratio'] = cond_table['alive'] / cond_table['total']
    cond_table.sort_values(by=['ratio'], axis=0, inplace=True)

    norm_min = min(cond_table['ratio'])
    norm_max = max(cond_table['ratio']) - norm_min
    cond_table['norm_ratio'] = (cond_table['ratio'] - norm_min) / norm_max
    if plot:
        x_ticks = [x / 100 for x in list(range(0, 101, 20))]
        x_label = [str(x) + "%" for x in list(range(0, 101, 20))]
        # ax = plt.subplot()
        plt.figure(figsize=(10, 8))
        ax = sns.barplot(x=cond_table['norm_ratio'], y=cond_table['cond_name'])
        plt.title('Mean alive (normalized) in whole condition')
        plt.ylabel('Condition')
        plt.xlabel('Percent alive')
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_label)
        plt.tight_layout()
        # plt.show()
        plt.savefig(f'{experiment}/figures/conditions_summary.png')
        plt.close()
    cond_table.sort_values(by=['cond_id'], axis=0, inplace=True)
    cond_table.to_csv(f'{experiment}/output/condition_data.csv', ';')
    return norm_min, norm_max


def find_apply_cutoff(plot=False, save=True):
    cutoff = save_condition_tables(plot=plot)
    norm_min, norm_max = normalize(plot=plot)
    wells = exp_df['well_name'].tolist()
    total = exp_df['n_organoids'].tolist()
    path = exp_df['file_path'].tolist()
    empty = exp_df['is_empty'].tolist()
    path_new = [pathx[:-18] + '_cutoff' + pathx[-18:-4] + '_cut.csv' for pathx in path]
    alive = []
    ratio = []
    norm_ratio = []
    for i in range(len(wells)):
        if empty[i]:
            print(f"{wells[i]} is empty")
            alive.append(None)
            continue
        df = pd.read_csv(convert_file_path(path[i]), sep=';')
        df['alive_bool'] = np.where(df['cell_round'] > cutoff, True, False)
        df['status'] = np.where(df['alive_bool'], 'alive', 'dead')
        alive.append(df['alive_bool'].sum())
        if save:
            df.to_csv(convert_file_path(path_new[i]), sep=';')
    for i in range(len(wells)):
        # print(f'processing ratios {wells[i]}')
        if empty[i]:
            ratio.append(None)
            norm_ratio.append(None)
            continue
        ratio.append(alive[i] / total[i])
        # ratio.append(ratio)
        if (ratio[-1] - norm_min) / norm_max < 0:
            norm_ratio.append(0)
            continue
        elif (ratio[-1] - norm_min) / norm_max > 1:
            norm_ratio.append(1)
            continue
        else:
            norm_ratio.append((ratio[-1] - norm_min) / norm_max)
    exp_df['alive'] = alive
    exp_df['total'] = total
    exp_df['ratio'] = ratio
    exp_df['norm_ratio'] = norm_ratio
    if save:
        exp_df.drop(["Unnamed: 0"], axis=1)
        exp_df.to_csv(f'{experiment}/output/experiment_table_cut.csv', sep=';')


find_apply_cutoff(save=True, plot=True)
# select_condition(1, plot=True)

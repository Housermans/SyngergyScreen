import pandas as pd
import matplotlib.pyplot as plt

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')

def select_condition(select_id, maxsize=50000, plot=False, title='NA', drop=[]):
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

def plt_cutoff(df, lower, upper, plot=False):
    lower = int(lower*100)
    upper = int(upper*100)
    pct_alive = []
    for value in range(lower, upper+1, 1):
        pct_alive.append(classify_alive(df, value))
    if plot:
        plt.bar(range(lower, upper+1, 1), pct_alive)
        plt.show()
    return pct_alive

def plt_diff(neg_df, pos_df, lower, upper):
    neg = plt_cutoff(neg_df, lower, upper)
    pos = plt_cutoff(pos_df, lower, upper)
    lower = int(lower * 100)
    upper = int(upper * 100)
    diff = []
    for i in range(len(neg)):
        diff.append(neg[i] - pos[i])
    plt.bar(range(lower, upper+1, 1), diff)
    plt.show()
    return diff

negctrl_organoid_df = select_condition(1)
posctrl_organoid_df = select_condition(2, drop=['K22'])
plt_diff(negctrl_organoid_df, posctrl_organoid_df, 0.5, 0.9)
# summarize_condition(negctrl_organoid_df1, title="Negative Control (DMSO)")
# summarize_condition(posctrl_organoid_df2, title="Positive control (Navitoclax 10microM)")
# summarize_per_well(negctrl_organoid_df, title='negative control (DMSO)')
# summarize_per_well(posctrl_organoid_df, title='positive control (navitoclax)')

# print(classify_alive(negctrl_organoid_df, 70))
# neg = plt_cutoff(negctrl_organoid_df, 0.5, 0.9)
# pos = plt_cutoff(posctrl_organoid_df, 0.5, 0.9)


'''
print(f"Negative control: {len(negctrl_summary_df)}")
print(negctrl_summary_df['mean_roundness'])
print(negctrl_summary_df['n_organoids'].sum())

print(f"Positive control: {len(posctrl_summary_df)}")
print(posctrl_summary_df['mean_roundness'])
print(posctrl_summary_df['n_organoids'].sum())
'''
import pandas as pd
import matplotlib.pyplot as plt

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')

def select_condition(select_id, maxsize=50000, plot=False, title='NA'):
    select_df = exp_df.loc[exp_df['cond_id'] == select_id]
    cond_name = select_df['Cond_name'].unique()[0]
    organoid_df = pd.DataFrame(columns=['Unnamed: 0', 'ScreenName', 'ScreenID', 'PlateName', 'PlateID',
       'MeasurementDate', 'MeasurementID', 'WellName', 'Row', 'Column',
       'Field', 'Timepoint', 'Object Number', 'X', 'Y', 'Bounding Box',
       'mean_intensity', 'cell_round', 'cell_area', 'object_no'])
    for index, row in select_df.iterrows():
        temp_df = pd.read_csv(row['file_path'], sep=';')
        organoid_df = pd.concat([organoid_df, temp_df])
    organoid_df = organoid_df.drop(organoid_df[organoid_df.cell_area > maxsize].index)
    if plot:
        if (title == 'NA'):
            title = cond_name
        summarize_condition(organoid_df, title=title)
        summarize_per_well(organoid_df, title=title)
    return organoid_df

def summarize_per_well(df, title="Organoids"):
    wells = df['WellName'].unique()
    n_wells = len(wells)
    rows = int(n_wells / 8)
    columns = 8
    count = 1
    plt.subplots(rows, columns, sharey='row', sharex='col')
    for well in wells:
        well_df = df[df['WellName'] == well]
        ax = plt.subplot(rows,columns,count)
        plt.title(well)
        plt.hist(well_df['cell_round'], density=True, stacked=True)
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

vino120_organoids_df = select_condition(10, plot=True, title="vinorelbine 120")
negctrl_organoid_df = select_condition(1, plot=True)
# posctrl_summary_df, posctrl_organoid_df = select_condition(2)
# summarize_condition(negctrl_organoid_df1, title="Negative Control (DMSO)")
# summarize_condition(posctrl_organoid_df2, title="Positive control (Navitoclax 10microM)")
# summarize_per_well(negctrl_organoid_df, title='negative control (DMSO)')
# summarize_per_well(posctrl_organoid_df, title='positive control (navitoclax)')

'''
print(f"Negative control: {len(negctrl_summary_df)}")
print(negctrl_summary_df['mean_roundness'])
print(negctrl_summary_df['n_organoids'].sum())

print(f"Positive control: {len(posctrl_summary_df)}")
print(posctrl_summary_df['mean_roundness'])
print(posctrl_summary_df['n_organoids'].sum())
'''
import pandas as pd
import matplotlib.pyplot as plt

exp_df = pd.read_csv('output/experiment_table.csv', sep=';')

def select_condition(select_id):
    select_df = exp_df.loc[exp_df['cond_id'] == select_id]
    organoid_df = pd.DataFrame(columns=['Unnamed: 0', 'ScreenName', 'ScreenID', 'PlateName', 'PlateID',
       'MeasurementDate', 'MeasurementID', 'WellName', 'Row', 'Column',
       'Field', 'Timepoint', 'Object Number', 'X', 'Y', 'Bounding Box',
       'mean_intensity', 'cell_round', 'cell_area', 'object_no'])
    for index, row in select_df.iterrows():
        temp_df = pd.read_csv(row['file_path'], sep=';')
        organoid_df = pd.concat([organoid_df, temp_df])
    return select_df, organoid_df

negctrl_summary_df, negctrl_organoid_df1 = select_condition(1)
posctrl_summary_df, posctrl_organoid_df2 = select_condition(2)

print(negctrl_organoid_df1)
plt.hist(negctrl_organoid_df1['cell_round'])
plt.show()
'''
print(f"Negative control: {len(negctrl_summary_df)}")
print(negctrl_summary_df['mean_roundness'])
print(negctrl_summary_df['n_organoids'].sum())

print(f"Positive control: {len(posctrl_summary_df)}")
print(posctrl_summary_df['mean_roundness'])
print(posctrl_summary_df['n_organoids'].sum())
'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

cond_table = pd.read_csv('output/condition_data.csv', sep=';')
cond_table['ratio'] = cond_table['alive']/cond_table['total']
cond_table.sort_values(by=['ratio'], axis=0, inplace=True)

norm = max(cond_table['ratio'])
cond_table['norm_ratio'] = cond_table['ratio'] / norm
fancy_names = ['Positive control (10microM Navi)', 'Binimetinib titration with 120nm Vinorelbine',
               'Vinorelbine titration with 175nm Lapatinib and Binimetinib', 'Vinorelbine 120nm',
               'Lapatinib titration with 120nm vinorelbine', 'Synergy table with vinorelbine',
               'Binimetinib titration alone', 'Navitoclax titration', 'Lapatinib titration',
               'Synergy table without vinorelbine', 'Negative control (DMSO)']
cond_table['fancy_name'] = fancy_names

'''
x = range(len(cond_table))
ax = plt.subplot()
plt.bar(x,cond_table['ratio'])
ax.set_xticks(x)
ax.set_xticklabels(cond_table['Cond_name'], Rotation=80)
plt.show()'''
x_ticks = [x/100 for x in list(range(0,101,20))]
x_label = [str(x)+"%" for x in list(range(0,101,20))]
# ax = plt.subplot()
ax = sns.barplot(x=cond_table['norm_ratio'], y=cond_table['Cond_name'])
plt.title('Mean alive (normalized) in whole condition')
plt.ylabel('Condition')
plt.xlabel('Percent alive')
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_label)
plt.tight_layout()
plt.show()

cond_table.sort_values(by=['Cond_id'], axis=0, inplace=True)
cond_table.to_csv('output/condition_data.csv', ';')
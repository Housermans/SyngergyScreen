from Plot_graphs import drug_response, load_condition
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

navi = drug_response(3, drug='Navi')
# drug_response(4, drug='Lapa')
# drug_response(6, drug='Bini')
# drug_response(11, drug='Vino')

plt.plot(x=navi[1], y=navi[2])
plt.show()
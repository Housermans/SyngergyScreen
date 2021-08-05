from os.path import exists

import pandas as pd
import glob
from string import ascii_uppercase as abc
import os

# Here a class (or an object) is made to represent a well on the drug screen plate. This will then be used to aggregate
# data from that well. Most important: what treatment was given and what objects were identified.
# Step one: run 'folder_set_up()'
# Step two: fill 'input/well_csv' folder with .csv files from columbus
# Step three: add an file Conditions_table.xlsx (an overview of all conditions, see example)
# Step four: add Drugconcentrations_perwell.xlsx (that's the tab from the drugreport excelfile)
# Step five:

class DrugWell:
    def __init__(self, experiment, name, plate, row, column, id):
        self.name = name  # well_name is A01 or C06 etc.
        self.id = id
        self.plate = plate  # integers, if multiple plates were used in a drug screen
        self.row = row  # integer, instead of ABC etc.
        self.row_alpha = abc[row]
        self.column = column  # integer
        # below variables are defined to incorporate the drug variables per well. This should be changed if different
        # types of drugs are used.
        self.Lapa = 0
        self.Lapa_unit = "µM"
        self.isin_Lapa = False
        self.Lapa_round = 0
        self.Bini = 0
        self.Bini_unit = "µM"
        self.isin_Bini = False
        self.Bini_round = 0
        self.Vino = 0
        self.Vino_unit = "µM"
        self.isin_Vino = False
        self.Vino_round = 0
        self.isin_DMSO = False
        self.Navi = 0
        self.Navi_unit = "µM"
        self.isin_Navi = False
        self.Navi_round = 0
        # identifies plate number in the original file and links it to a known folder that contains the data (csv txt
        # files obtained from Columbus) on these plates.
        self.df_input_path = f"../data/{experiment}/input/well_csv/"
        self.df_output_path = f"../data/{experiment}/output/well_csv/"
        # the code below fixes a problem that in the columbus export, the 0 before a single digit number is left out,
        # whereas the drug screen uses a 0. Since the drug screen file is the 'basis', the 0 should be removed here to
        # search for the columbus files. Both txt and csv files here are defined, explanation of that choice below.
        if self.column == 1:
            self.file_name_csv = f"*result.{self.name.replace('01', '1[')}*.csv"
        elif self.column == 2:
            self.file_name_csv = f"*result.{self.name.replace('02', '2[')}*.csv"
        elif self.column < 10:
            self.file_name_csv = f"*result.{self.name.replace('0', '')}*.csv"
        else:
            self.file_name_csv = f"*result.{self.name}*.csv"
        # searches for a file that contains the variables set above. Glob identifies the * as a wildcard variable so
        # it knows to search for patterns instead of literal *.
        self.file_path_get_csv = glob.glob(self.df_input_path + self.file_name_csv)
        if os.path.getsize(self.file_path_get_csv[0]) == 0:
            print(f"ERROR {self.name} is empty (empty file)")
            self.total_cells = 0
            self.roundness_mean = None
            self.file = f"{self.df_output_path}{self.name}_organoids_EMPTY.csv"
            self.isEmpty = True
        else:
            self.df = pd.read_csv(self.file_path_get_csv[0], sep=';')
            if self.df.empty:
                print(f"{self.name} is empty (no elements selected)")
                self.total_cells = 0
                self.roundness_mean = None
                self.isEmpty = True
            else:
                self.df.rename(columns={"Organoids Selected - Intensity Cell Channel2 Mean": "mean_intensity",
                                        "Organoids Selected - Cell Roundness": "cell_round",
                                        "Organoids Selected - Cell Area [µm²]": "cell_area",
                                        "Organoids Selected - Object No in Organoids Selected": "object_no",
                                        #"Organoids Selected Selected - Cell Ratio Width to Length": "wtl_ratio",
                                        #"Organoids Selected Selected - Cell Length[µm]": "length",
                                        #"Organoids Selected Selected - Cell Width[µm]": "width"
                                        }, inplace=True)
                self.total_cells = len(self.df)
                self.roundness_mean = self.df.cell_round.mean()
                self.file = f"{self.df_output_path}{self.name}_organoids.csv"
                self.df.to_csv(self.file, sep=';')
                self.isEmpty = False


    # this method is used to import drug information from the drug printer export into the drug
    # well class.
    # the xml file from the drug printer has a new row for every drug and multiple rows per well.
    def update_drugs(self, name, concentration, unit):
        if name == "Lapatinib":
            self.Lapa = concentration
            self.Lapa_round = round(concentration, 3)
            self.Lapa_unit = unit
            self.isin_Lapa = True
            self.isin_DMSO = False
        elif name == "Binimetinib":
            self.Bini = concentration
            self.Bini_round = round(concentration, 3)
            self.Bini_unit = unit
            self.isin_Bini = True
            self.isin_DMSO = False
        elif name == "Vinorelbine":
            self.Vino = concentration
            self.Vino_round = round(concentration, 3)
            self.Vino_unit = unit
            self.isin_Vino = True
            self.isin_DMSO = False
        elif name == "Navitoclax":
            self.Navi = concentration
            self.Navi_round = round(concentration, 3)
            self.Navi_unit = unit
            self.isin_Navi = True
            self.isin_DMSO = False
        # the drug printer xml file contains a 'dmso normalization' in all wells as a last row for that well.
        # the step below registers if
        elif name == "DMSO normalization":
            if not self.isin_Lapa and not self.isin_Bini and not self.isin_Vino and not self.isin_Navi:
                self.isin_DMSO = True
            else:
                self.isin_DMSO = False
        else:
            print(f"{name} not defined, please refer to update_drugs method in the Drug"
                  f"Well class")

    # checks the proportion of objects identified that have a roundness above the cut_off variable.
    # gives a verbose summary of findings which can be shut off by overriding the standard verbose boolean
    # variable.
    def prop_alive(self, cut_off, verbose=False):
        self.death_cells = 0
        for cell in self.df.cell_round:
            if cell < cut_off:
                self.death_cells += 1
        self.death_cells_proportion = self.death_cells / self.total_cells
        if verbose:
            print(f"In {self.name}, {self.death_cells} out of {self.total_cells} are alive. "
                  f"\nProportion = {self.death_cells_proportion}"
                  f"\nMean roundness = {self.roundness_mean}")
        return self.death_cells_proportion

    def summary(self):
        print(f"____summary of well____"
              f"\nThis is well {self.name} of plate {self.plate}"
              f"\nLapa: {str(self.Lapa)}{self.Lapa_unit}"
              f"\nBini: {str(self.Bini)}{self.Bini_unit}"
              f"\nVino: {str(self.Vino)}{self.Vino_unit}"
              f"\nNavi: {str(self.Navi)}{self.Navi_unit}"
              f"\nDMSO: {str(self.isin_DMSO)}")


def fill_library(experiment):
    # Below the code actually starts.
    # imports 2 xlsx files: the drug print file and a file with conditions in the test
    # this is dependent on the openpyxl package!
    drug_df = pd.read_excel(fr'../data/{experiment}/input/Drugconcentrations_perwell.xlsx')
    cond_df = pd.read_excel(fr'../data/{experiment}/input/Conditions_table.xlsx')
    # print(drug_df.columns) # gives the following result:
    # Index(['Plate', 'Dispensed\nwell', 'Dispensed\nrow', 'Dispensed\ncol', 'Fluid',
    #     'Fluid name', 'Cassette', 'Dispense\nhead', 'Start time',
    #     'Dispensed concentration', 'Conc. units', 'Dispensed volume',
    #     'Volume units', 'Total well volume'],
    #     dtype='object')
    # below, two a library is made per plate in the experiment. These will hold the drug
    # well classes based on
    # the name of the well.
    class_dict = {}

    well_id = []
    well_name_lst = []
    row = []
    column = []
    plate = []
    cond_id = []
    Navi = []
    Navi_round = []
    Lapa = []
    Lapa_round = []
    Bini = []
    Bini_round = []
    Vino = []
    Vino_round = []
    n_organoids = []
    mean_roundness = []
    file_path = []
    empty = []

    # here, the library is filled based on the drug printer file with all the drugs per well in a different row
    id = 1
    for index in drug_df.index:
        well_name = str(drug_df['Dispensed\nwell'][index])
        drug_name = drug_df["Fluid name"][index]

        if well_name in class_dict.keys():
            class_dict[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index],
                                           drug_df["Conc. units"][index])
        else:
            class_dict[well_name] = DrugWell(experiment, drug_df['Dispensed\nwell'][index], drug_df["Plate"][index],
                                         drug_df["Dispensed\nrow"][index],
                                         drug_df["Dispensed\ncol"][index], id)
            class_dict[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index],
                                           drug_df["Conc. units"][index])
            id += 1

    print("Loaded all drug concentrations per well.")

# this for loop makes a master table with all conditions and well data combined, that is henceforth
# used to summarize results
    for key in class_dict:
        well_id.append(class_dict[key].id)
        well_name_lst.append(class_dict[key].name)
        row.append(class_dict[key].row)
        column.append(class_dict[key].column)
        plate.append(class_dict[key].plate)
        Navi.append(class_dict[key].Navi)
        Navi_round.append(class_dict[key].Navi_round)
        Lapa.append(class_dict[key].Lapa)
        Lapa_round.append(class_dict[key].Lapa_round)
        Bini.append(class_dict[key].Bini)
        Bini_round.append(class_dict[key].Bini_round)
        Vino.append(class_dict[key].Vino)
        Vino_round.append(class_dict[key].Vino_round)
        n_organoids.append(class_dict[key].total_cells)
        mean_roundness.append(class_dict[key].roundness_mean)
        file_path.append(class_dict[key].file)
        empty.append(class_dict[key].isEmpty)
        if class_dict[key].isin_DMSO:
            cond_id.append(1)
        elif class_dict[key].isin_Navi:
            if 10.018 < class_dict[key].Navi < 10.019:
                cond_id.append(2)
            else:
                cond_id.append(3)
        elif class_dict[key].isin_Lapa:
            if not class_dict[key].isin_Bini and not class_dict[key].isin_Vino:
                cond_id.append(4)
            elif not class_dict[key].isin_Bini and class_dict[key].isin_Vino:
                cond_id.append(5)
            elif class_dict[key].isin_Bini and not class_dict[key].isin_Vino:
                cond_id.append(8)
            elif class_dict[key].isin_Bini and class_dict[key].isin_Vino:
                if 0.119 < class_dict[key].Vino < 0.1191:
                    cond_id.append(9)
                else:
                    cond_id.append(11)
        elif class_dict[key].isin_Bini:
            if not class_dict[key].isin_Vino:
                cond_id.append(6)
            elif class_dict[key].isin_Vino:
                cond_id.append(7)
        elif class_dict[key].isin_Vino:
            cond_id.append(10)
        else:
            print("Couldn't define condition!")

    exp_dict = {'well_id': well_id,
                'well_name': well_name_lst,
                'row': row,
                'column': column,
                'plate': plate,
                'cond_id': cond_id,
                'Navi': Navi,
                'Navi_round' : Navi_round,
                'Lapa': Lapa,
                'Lapa_round': Lapa_round,
                'Bini': Bini,
                'Bini_round': Bini_round,
                'Vino': Vino,
                'Vino_round': Vino_round,
                'n_organoids': n_organoids,
                'mean_roundness': mean_roundness,
                'file_path': file_path,
                'is_empty' : empty
                }
    global exp_df
    exp_df = pd.DataFrame.from_dict(exp_dict)
    cond_df = pd.read_excel(fr'../data/{experiment}/input/Conditions_table.xlsx')
    cond_df = cond_df[['cond_id', 'cond_name']]
    if 'cond_name' in exp_df:
        print('This column already exists')
        return None
    merged_inner = pd.merge(left=exp_df, right=cond_df, left_on='cond_id', right_on='cond_id')
    merged_inner.to_csv(f'../data/{experiment}/output/experiment_table.csv', sep=';')
    print('Synthesized all data into experiment_table.csv')
    print('Continue to next code block')

def find_positive(plate, cut_off, verbose=True):
    # old code used to print 'positive control' conditions
    print("================positive controls================")
    for well in plate:
        if plate[well].DMSO:
            if verbose:
                plate[well].summary()
                plate[well].prop_alive(cut_off)
            else:
                print(f"{plate[well].name}: {plate[well].prop_alive(cut_off, False)}")


def find_negative(plate, cut_off, verbose=True):
    # same as find_positive, not in use anymore.
    print("================negative controls================")
    for well in plate:
        if not plate[well].Navi == 0:
            if verbose:
                plate[well].summary()
                plate[well].prop_alive(cut_off)
            else:
                print(f"{plate[well].name}: {plate[well].prop_alive(cut_off, False)}")


# fill_library("E21-002_RAS16")

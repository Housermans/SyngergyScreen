import pandas as pd
import glob
import string

abc = string.ascii_uppercase

# Here a class (or an object) is made to represent a well on the drug screen plate. This will then be used to aggregate
# data from that well. Most important: what treatment was given and what objects were identified.
class Drug_Well:
    def __init__(self, name, plate, row, column):
        self.name = name  # well_name is A01 or C06 etc.
        self.plate = plate  # integers, if multiple plates were used in a drug screen
        self.row = row  # integer, instead of ABC etc.
        self.row_alpha = abc[row]
        self.column = column  # integer
        # below variables are defined to incorporate the drug variables per well. This should be changed if different
        # types of drugs are used.
        self.Lapa = 0
        self.Lapa_unit = "µM"
        self.isin_Lapa = False
        self.Bini = 0
        self.Bini_unit = "µM"
        self.isin_Bini = False
        self.Vino = 0
        self.Vino_unit = "µM"
        self.isin_DMSO = False
        self.Navi = 0
        self.Navi_unit = "µM"
        self.isin_Navi = False
        # identifies plate number in the original file and links it to a known folder that contains the data (csv txt
        # files obtained from Columbus) on these plates.
        self.df_input_path = "input/well_csv/"
        self.df_output_path = "output/well_csv/"
        # the code below fixes a problem that in the columbus export, the 0 before a single digit number is left out,
        # whereas the drug screen uses a 0. Since the drug screen file is the 'basis', the 0 should be removed here to
        # search for the columbus files. Both txt and csv files here are defined, explanation of that choice below.
        if self.column == 1:
            self.file_name_csv = f"*result.{self.name.replace('01', '1[')}*.csv"
        elif self.column < 10:
            self.file_name_csv = f"*result.{self.name.replace('0','')}*.csv"
        else:
            self.file_name_csv = f"*result.{self.name}*.csv"
        # searches for a file that contains the variables set above. Glob identifies the * as a wildcard variable so
        # it knows to search for patterns instead of literal *.
        self.file_path_get_csv = glob.glob(self.df_input_path + self.file_name_csv)
        self.df = pd.read_csv(self.file_path_get_csv[0])
        self.df = self.df.rename(columns={"Organoids Selected - Intensity Cell Channel2 Mean": "mean_intensity",
                                          "Organoids Selected - Cell Roundness": "cell_round",
                                          "Organoids Selected - Cell Area [µm²]": "cell_area",
                                          "Organoids Selected - Object No in Organoids": "object_no"})
        self.df.to_csv(f"{self.df_output_path}{self.name}_organoids.csv", sep=';')


    # this method is used to import drug information from the drug printer export into the drug_well class.
    # the xml file from the drug printer has a new row for every drug and multiple rows per well.
    def update_drugs(self, name, concentration, unit):
        if name == "Lapatinib":
            self.Lapa = concentration
            self.Lapa_unit = unit
            self.isin_Lapa = True
            self.isin_DMSO = False
        elif name == "Binimetinib":
            self.Bini = concentration
            self.Bini_unit = unit
            self.isin_Bini = True
            self.isin_DMSO = False
        elif name == "Vinorelbine":
            self.Vino = concentration
            self.Vino_unit = unit
            self.isin_Vino = True
            self.isin_DMSO = False
        elif name == "Navitoclax":
            self.Navi = concentration
            self.Navi_unit = unit
            self.isin_Navi = True
            self.isin_DMSO = False
        # the drug printer xml file contains a 'dmso normalization' in all wells as a last row for that well.
        # the step below registers if
        elif name == "DMSO normalization":
            if not self.Lapa and not self.Bini and not self.Vino and not self.Navi:
                self.isin_DMSO = True
            else:
                self.isin_DMSO = False
        else:
            print(f"{name} not defined, please refer to update_drugs method in the Drug_Well class")
    #checks the proportion of objects identified that have a roundness above the cut_off variable.
    #gives a verbose summary of findings which can be shut off by overriding the standard verbose boolean
    #variable.
    def prop_alive(self, cut_off, verbose=True):
        self.roundness_mean = self.df.cell_round.mean()
        self.total_cells = self.df.cell_round.count()
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

def fill_library():
    # Below the code actually starts.
    # imports xlsx file with column names: Dispensed Well, Fluid name, Dispensed concentration.
    # this is dependent on the openpyxl package!
    drug_df = pd.read_excel(r'input/Drugconcentrations_perwell.xlsx')
    # print(drug_df.columns) # gives the following result:
    # Index(['Plate', 'Dispensed\nwell', 'Dispensed\nrow', 'Dispensed\ncol', 'Fluid',
    #     'Fluid name', 'Cassette', 'Dispense\nhead', 'Start time',
    #     'Dispensed concentration', 'Conc. units', 'Dispensed volume',
    #     'Volume units', 'Total well volume'],
    #     dtype='object')
    # below, two a library is made per plate in the experiment. These will hold the drug_well classes based on
    # the name of the well.
    plate1 = {}
    plate2 = {}
    # here, the library is filled based on the drug printer file with all the drugs per well in a different row
    for index in drug_df.index:
        well_name = str(drug_df['Dispensed\nwell'][index])
        drug_name = drug_df["Fluid name"][index]
        if drug_df['Plate'][index] == 1:
            if well_name in plate1.keys():
                plate1[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index],
                                               drug_df["Conc. units"][index])
            else:
                plate1[well_name] = Drug_Well(drug_df['Dispensed\nwell'][index], drug_df["Plate"][index], drug_df["Dispensed\nrow"][index],
                                              drug_df["Dispensed\ncol"][index])
                plate1[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index], drug_df["Conc. units"][index])
        elif drug_df['Plate'][index] == 2:
            if well_name in plate2.keys():
                plate2[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index], drug_df["Conc. units"][index])
            else:
                plate2[well_name] = Drug_Well(drug_df['Dispensed\nwell'][index], drug_df["Plate"][index], drug_df["Dispensed\nrow"][index],
                                              drug_df["Dispensed\ncol"][index])
                plate2[well_name].update_drugs(drug_name, drug_df["Dispensed concentration"][index], drug_df["Conc. units"][index])


def find_positive(plate, cut_off, verbose=True):
    print("================positive controls================")
    for well in plate:
        if plate[well].DMSO:
            if verbose:
                plate[well].summary()
                plate[well].prop_alive(cut_off)
            else:
                print(f"{plate[well].name}: {plate[well].prop_alive(cut_off,False)}")
def find_negative(plate, cut_off, verbose=True):
    print("================negative controls================")
    for well in plate:
        if not plate[well].Navi == 0:
            if verbose:
                plate[well].summary()
                plate[well].prop_alive(cut_off)
            else:
                print(f"{plate[well].name}: {plate[well].prop_alive(cut_off,False)}")
def find_condition(plate, Lapa=False, Bini=False, Vino=False, Navi=False, DMSO=False, verbose=True):
    variable_list = [Lapa, Bini, Vino, Navi, DMSO]
    mission = []
    for var in variable_list:
        if var:
            mission.append(var)
    if not mission:
        print(f"please name a variable from {variable_list} to use this function")
        return None
    elif len(mission) == 1 and DMSO == True:
        print("================positive controls================")
    elif len(mission) == 1 and Navi == True:
        print("================negative controls================")
    else:
        print(f"=======looking for {mission}=======")
    # for well in plate:
        # for objective in mission:
            # if plate[well].objective != 0:
                # if verbose:
                    # plate[well].summary()
                    # plate[well].prop_alive(cut_off)
                # else:
                    # print(f"{plate[well].name}: {plate[well].prop_alive(cut_off,False)}")

# find_positive(plate1, 0.75,False)
# find_negative(plate1, 0.75,False)
# find_condition(plate1, DMSO=True)
# find_condition(plate1, Navi=True, Bini=True)
# find_condition(plate1, Navi=True)
fill_library()
import os
from glob import glob

experiment_folder = "E21-004_RAS13"

def folder_set_up(experiment_folder):
    # input is the name of a experiment you want to analyse. Makes folders that are then used for the analysis.
    necessary_folders = ['','figures', 'input', 'input/well_csv', 'output',
                         'output/well_csv', 'output/well_csv_cutoff', 'output/conditions']
    for folder in necessary_folders:
        full_path = f"../{experiment_folder}/{folder}"
        if os.path.isdir(full_path):
            print(f"{full_path} exists, moving on")
            continue
        else:
            print(f"making {full_path}")
            os.mkdir(full_path)

def check_if_set(experiment_folder):
    necessary_files = ['input/well_csv/*.csv', 'input/Conditions_table.xlsx', 'input/Drugconcentrations_perwell.xlsx']
    all_set = True
    for file in necessary_files:
        full_path = f"../{experiment_folder}/{file}"
        glob_list = glob(full_path)
        if glob_list:
            print(f"Found {len(glob_list)} files for {file}")
        else:
            print(f'File {file} not found, make sure that you used the correct spelling (first letter is capitalized in both manditory excel files!)')
            all_set = False
    if all_set:
        print("All necessary files are complete, continue to next code block!")
    else:
        print("Something went wrong, make sure you used the correct names for the input folder and files.")

folder_set_up(experiment_folder)
check_if_set(experiment_folder)
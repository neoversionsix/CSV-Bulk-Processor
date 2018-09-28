# IMPORTING LIBRARIES ----------------------------------------------------------------------------
import pandas as pd
import numpy as np
import os
import re
import glob
import csv
import shutil

# INPUT VARIABLES----------------------------------------------------------------------------------
# Directory folder of the csv files you want to process
Input_path_CSVs = 'D:/FILES/Input_CSV/'
# Can change to xlsx if needed, other changes will be nessesary to code
Extension = 'csv'
# Csv files seperator for input and output files..generally (,) or (|)
Delimiter = '|'

# Directory folder of the TKC cross reference table
Input_path_TKC_files = 'D:/FILES/Input_TKC_files/'

# Directory excel file of the Sample Point Table
Input_path_SPT = 'D:/FILES/Sample Points_37883_20180926_134607.xlsx'

# Output folder of the CSV files
Output_path_processed_csv = 'D:/FILES/Output_CSV_Processed/'

# Output folder path of bad SPT CSV files
Output_path_badSPT = 'D:/FILES/Output_CSV_Bad_SPT/'

# Output folder path of Retest CSV files
Output_path_Retests = 'D:/FILES/Output_CSV_Retests/'

# Output folder path of TKC Unmapped Data
Output_path_Retests = 'D:/FILES/Output_CSV_Bad_TKC/'

# Output folder path of CSV Files with Structure that can't be Analysed
Output_path_bad_structure = 'D:/FILES/Output_CSV_Bad_Column_Structure/'

# Output folder path of Report on Analysed files
Output_path_Report = 'D:/FILES/'

print('Directories loaded...')

# READ AND PROCESS THE SAMPLE POINTS FILE----------------------------------------------------------
df_SPTs = pd.read_excel(Input_path_SPT, sheet_name='Data')
List_Columns_Keep = ['Name','OldSiteCode_post2007']
df_SPTs = df_SPTs[List_Columns_Keep]
df_SPTs.columns = ['SPT', 'OSC']

# Remove ESP points
df_SPTs = df_SPTs[~df_SPTs['SPT'].astype(str).str.startswith('ESP')]

# Delete non Unique (duplicate) OSC's
df_SPTs.drop_duplicates(subset='OSC', keep=False, inplace=True)
print('SPT Cross Reference Table created...')

# READ AND PROCESS THE TKC FILES---------------------------------------------------------------
os.chdir(Input_path_TKC_files)
filenames = [i for i in glob.glob('*.{}'.format('xlsx'))]

List_Columns_Keep = ['Test Key Code (TKC)','Valid', 'Data Type']
bool_df_created = False
for filename in filenames:
    if bool_df_created == False:
        df_TKCs = pd.read_excel(filename, sheet_name='Data')
        bool_df_created = True
        df_TKCs = df_TKCs[List_Columns_Keep]
        df_TKCs.columns = ['TKC', 'Valid','DT']
    else:
        df_temp = pd.read_excel(filename, sheet_name='Data')
        df_temp = df_temp[List_Columns_Keep]
        df_temp.columns = ['TKC', 'Valid','DT']
        df_TKCs.append(df_temp)

# Remove Biosolids Monitoring TKC's from Dataframe and delete DT column
df_TKCs = df_TKCs[~df_TKCs['SPT'].astype(str).str.startswith('Bio')]
df_TKCs.drop('DT', axis=1, inplace=True)

# Remove Invalid TKC's from Dataframe and delete Valid column
df_TKCs = df_TKCs[~df_TKCs['Valid'].astype(str).str.startswith('N')]
df_TKCs.drop('Valid', axis=1, inplace=True)

# Delete non Unique (duplicate) TKC's
df_TKCs.drop_duplicates(subset='TKC', keep=False, inplace=True)

print('TKC Cross Reference Table created...')
print(df_TKCs)


# SAVE CSV FILENAMES IN A LIST AND DATAFRAME--------------------------------------------------------
# Get the csv filenames into an array
os.chdir(Input_path_CSVs)
filenames = [i for i in glob.glob('*.{}'.format(Extension))]

# Get the number of csv files
NumFiles = len(filenames)
print(NumFiles, 'csv files found...')

# MOVE FILES WITHOUT 'LOCATIONCODE' or 'LocationDescription' ---------------------------------------
counter_good_files = 0
counter_bad_files = 0
List_Unsupported_Files = []
for filename in filenames:
    # Save an individual file as a DataFrame Object to analyse
    try:
        df_file = pd.read_csv(filename, sep=Delimiter, index_col=False, engine='python')
        if ('LOCATIONCODE' in df_file.columns) and ('LocationDescription' in df_file.columns):
            counter_good_files +=1
        else:
            List_Unsupported_Files.append(filename)
            counter_bad_files +=1
    except:
        List_Unsupported_Files.append(filename)
        counter_bad_files +=1

# Print stats        
print('Number of Files that can be Analysed:', counter_good_files)
print("Number of Files that can't be Analysed:", counter_bad_files)

# Move files
files = os.listdir(Input_path_CSVs)

for f in files:
    if f in List_Unsupported_Files:
        shutil.move(f, Output_path_bad_structure)

# READ THE CSV FILENAMES INTO AN ARRAY ----------------------------------------------------------------
os.chdir(Input_path_CSVs)
filenames = [i for i in glob.glob('*.{}'.format(Extension))]

# CREATE AN EMPTY DATAFRAME FOR REPORT--------------------------------------------------------------------
List_Columns = ['Filename', 'Total Rows', 'Duplicates', 'Retests', 'QA Data', 'No SPT Code']
df_Report = pd.DataFrame(columns=List_Columns)

# LOOP THOUGH EACH FILE AND PROCESS IT -------------------------------------------------------------------
# Loop through each csv file in the input directory
for filename in filenames:
    # Set File Identifiers to Not Guilty untill proven guilty
    QA_Data_In_File = False
    Bad_sptz = False
    Retests_In_File = False
    Duplicates_In_File = False
    
    Int_Total_Rows = int(0)
    Int_Bad_SPTz = int(0)
    Int_QA_Rows = int(0)
    Int_Dup_Rows = int(0)
    Int_Retest_Rows = int(0)
    
    # Save an individual file as a DataFrame Object to analyse
    df_file = pd.read_csv(filename, sep=Delimiter, index_col=False, engine='python')
    # Delete Rows with everything missing in the row
    df_file = df_file.dropna(axis='index', how='all')
    Int_Total_Rows = df_file.shape[0]

    
    
    ###################  QA DATA  ############################
    # Check and Find if Blanks exist in Location Code Rows
    bools_ml = df_file['LOCATIONCODE'].isnull()
    bools_ml = np.array(bools_ml)

    # Check and Find if Blanks exist in Location Description Rows
    bools_md = df_file['LocationDescription'].isnull()
    bools_md = np.array(bools_ml)

    # Find Quality Assurance Data Rows
    Series_Loc_Desc = df_file['LocationDescription']
    Series_Loc_Desc = Series_Loc_Desc.fillna(' ')
    bools_bd = Series_Loc_Desc == 'Blind Dup A'
    bools_bd = np.array(bools_bd)
    bools_bd = np.logical_and(bools_ml, bools_bd)
    bools_fb = Series_Loc_Desc == 'Field Blank'
    bools_fb = np.array(bools_fb)
    bools_fb = np.logical_and(bools_ml, bools_fb)
    bools_qa = np.logical_or(bools_bd, bools_fb)    
    bools_filter_QA = np.invert(bools_qa)
    if False in bools_filter_QA:
        QA_Data_In_File = True
        
    # Fixing QA Data and update DataFrame object if neccesary
    if QA_Data_In_File == True:
        # Number of QA Rows in data
        Int_QA_Rows = np.sum(bools_qa)
        # Filter Out Quality Control Data from DataFrame Object
        df_file = df_file[bools_filter_QA]

        
    ###################  MISSING SPT  ############################
    # Check if SPT's still don't exist in Location Code Rows
    Array_Loc_Codes = bools_good_sptz = df_file['LOCATIONCODE']
    # Create Array of Loc-Codes and Fill Blank Locations with a space so that we can check if it begins with SPT
    Array_Loc_Codes = Array_Loc_Codes.fillna(' ')
    # Generate Array of Booleans for rows that have SPT's
    bools_good_sptz = Array_Loc_Codes.str.startswith('SPT')
    bools_good_sptz = np.array(bools_good_sptz)

    
    # Save bad SPT codes in data to a new dataframe
    if False in bools_good_sptz:
        Bad_sptz = True
        # Create dataframe for stuff that can't load
        df_cant_load = df_file
        bools_filter_badSPT = np.invert(bools_good_sptz)
        # Count the number of Bad SPTz
        Int_Bad_SPTz = np.sum(bools_filter_badSPT)
        # Leave only Bad SPT data in 'df_cant_load' Dataframe
        df_cant_load = df_cant_load[bools_filter_badSPT]        
        # Filter Orginal Dataframe 'df_file' to delete SPT rows that won't load
        df_file = df_file[bools_good_sptz]
    
    ###################  DUPLICATES  ############################
    # Create Lists to Check for duplicates
    List_Row_Key = []
    for index, row in df_file.iterrows():
        String_Row =  str(row['LOCATIONCODE']) + str(row['SAMPLEDATE']) + str(row['TEST_KEY_CODE']) + str(row['RESULT'])
        # Append the row to the list of Rows to Check for Duplicates
        List_Row_Key.append(String_Row)

    # Create Array of Rows from List of Rows
    Array_Raw_Items_Results = np.array(List_Row_Key)
    
    # Decide if there are any exact duplicates    
    if len(np.unique(Array_Raw_Items_Results)) != len(Array_Raw_Items_Results):
        Duplicates_In_File = True
    
    # Find the rows where the exact duplicates live
    if Duplicates_In_File == True:
        # Create a dictionary of duplicate checker keys vs numvber of duplicates
        unique, counts = np.unique(Array_Raw_Items_Results, return_counts=True)
        Dict_Unique_Counts = dict(zip(unique, counts))
        #Create a list of keys for duplicates only
        List_Duplicate_Keys = ([key for key, val in Dict_Unique_Counts.items() if val > 1])
        # Find which Row Strings are exact duplicates and add their Index to a list
        List_Row_Index_Duplicates = []
        for key in List_Duplicate_Keys:
            # Get the row index's of the duplicate Key
            List_Indexes = [i for i, j in enumerate(List_Row_Key) if j == key]
            # Remove Fist Duplicate from List because we let the first one load
            List_Indexes.pop(0)
            # Append the row index's to a list
            List_Row_Index_Duplicates.extend(List_Indexes)
        # Count the number of Duplicates that will be deleted for Report
        Int_Dup_Rows = len(List_Row_Index_Duplicates)
        # Print feedback on Rows that are being deleted
        print('Deleting Duplicate Rows from:', filename)
        print(List_Row_Index_Duplicates)
        # Delete the rows that are duplicates from dataframe df_file
        df_file = df_file.drop(df_file.index[List_Row_Index_Duplicates])
        
    ###################  RETESTS  ############################
    # Create Lists to Check for Retests
    List_Row_Key = []
    for index, row in df_file.iterrows():
        String_Row =  str(row['LOCATIONCODE']) + str(row['SAMPLEDATE']) + str(row['TEST_KEY_CODE'])
        # Append the Row String Item to the list of Rows
        List_Row_Key.append(String_Row)

    # Create Array of Rows from List of Rows
    Array_Raw_Items_Results = np.array(List_Row_Key)
    # Decide if there are any Retests   
    if len(np.unique(Array_Raw_Items_Results)) != len(Array_Raw_Items_Results):
        Retests_In_File = True
    
    # Find the rows where the Retests live
    if Retests_In_File == True:
        # Create a dictionary of Row Strings to number of Retests
        unique, counts = np.unique(Array_Raw_Items_Results, return_counts=True)
        Dict_Unique_Counts = dict(zip(unique, counts))
        #Create a list of keys for Retests only
        List_Retest_Keys = ([key for key, val in Dict_Unique_Counts.items() if val > 1])
        # Find which Row Indexes are exact duplicates and add their Index to a list
        List_Row_Index_Retests = []
        for key in List_Retest_Keys:
            # Get the row index's of the duplicate Key
            List_Indexes = [i for i, j in enumerate(List_Row_Key) if j == key]
            # Remove Fist Duplicate from List because we let the first one load
            List_Indexes.pop(0)
            # Append the row index's to a list
            List_Row_Index_Retests.extend(List_Indexes)
        # Count the number of Retests
        Int_Retest_Rows = len(List_Row_Index_Retests)
        # Print feedback on Rows that are being deleted
        print('Moving Retests from', filename)
        print(List_Row_Index_Retests)
        
        # Generate bools for Retest Rows
        Num_New_Rows = df_file.shape[0]
        List_Bools_Retests = []
        Counter = int(0)
        for i in range(Num_New_Rows):
            if Counter in List_Row_Index_Retests:
                List_Bools_Retests.append(True)
                Counter += 1
            else:
                List_Bools_Retests.append(False)
                Counter += 1
        
        # Convert the list of Bools to a Numpy Array
        Array_Bools_Retests = np.array(List_Bools_Retests)
        
        # Create a new dataframe 'df_Retests' for only Retests
        df_Retests = df_file[Array_Bools_Retests]
                
        # Delete the rows that are Retests from dataframe df_file
        df_file = df_file.drop(df_file.index[List_Row_Index_Retests])
        
        
    ###################  REPORT UPDATING ############################
    # Append Update the Report Dataframe
    List_Row_Report = [filename, Int_Total_Rows, Int_Dup_Rows, Int_Retest_Rows, Int_QA_Rows, Int_Bad_SPTz]
    df_Temp_Report = pd.DataFrame([List_Row_Report], columns=List_Columns)
    df_Report = df_Report.append(df_Temp_Report, ignore_index=True)
  
    ###################  PROCESSED FILE  ############################
    # Create New Processed File if 1 or more rows
    if df_file.shape[0] > 0:
        new_filename = filename[:-4] + '-processed' + filename[-4:]
        Output_filename = Output_path_processed_csv + new_filename
        df_file.to_csv(path_or_buf=Output_filename, sep='|', index=False)
    
    ###################  CREATE NO SPT FILE  ############################
    # Create New Bad File for fixes that can't be made
    if (Bad_sptz == True):
        if df_cant_load.shape[0] > 0:
            new_filename = filename[:-4] + '-NoSPTs' + filename[-4:]
            Output_filename = Output_path_badSPT + new_filename
            df_cant_load.to_csv(path_or_buf=Output_filename, sep='|', index=False)   
            
    ###################  CREATE RETESTS FILE  ############################
    if (Retests_In_File == True):
        if df_Retests.shape[0] > 0:
            new_filename = filename[:-4] + '-Retests' + filename[-4:]
            Output_filename = Output_path_Retests + new_filename
            df_Retests.to_csv(path_or_buf=Output_filename, sep='|', index=False)

# CREATE EXCEL REPORT--------------------------------------------------------------------------------
# Generate Excel Report
Report_path_filename = Output_path_Report + 'Report.xlsx'
writer = pd.ExcelWriter(Report_path_filename)
df_Report.to_excel(writer,'Sheet1')
writer.save()
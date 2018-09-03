# CSV Bulk Processor

## Summary
This script will go into a folder of your choice and analyse data in all the csv files in that folder. It will filter data from the orginal file and export this data to another csv file. In some cases it will simply filter out data and create a copy.

## What it does (Step by step)
1. Analyse csv files in a certain 'input folder':
    * a) if they dont match a given structure those csv files will be moved to a 'bad column structure' folder.
    * b) if they match the structure they will stay in the 'input folder'.
2. For each csv file:
    * a) Read the csv file into a new 'processed' file and then delete rows that don't contain any data.
    * b) Count the number of rows.
    * c) Count and delete 'Quality Assurance (QA)' Rows from the processed file. Note: QA rows are defined as rows without anything in the 'LOCATIONCODE' column AND they contain EITHER 'Blind Dup A' OR 'Field Blank' in the 'LocationDescription' column.
    * d) Create a new file (NoSPT file) from the 'processed file' leaving only the rows without SPT codes. Remove the rows without SPT codes from the 'processed' file. A csv with the original filename with appended tag '-NoSPT' is created for the data with this issue.
    * e) Create a new file (Retests file) from the 'processed file' leaving only the rows that are retests. Note: retests are defined as rows with the same location, date-time, and test methods; but have a different result. Remove the rows that are retests from the 'processed' file. A csv with the original filename with appended tag '-Retests' is created for the data with this issue.
    * f) Create an Excel file for the counts of issues in each file that is analysed.
    
## How to use it
1. Create folders for:
    * a) the input file where all the csv's you wish to process live (Input_path_CSVs)
    * b) Output file where all the csv's with unreadable column stuctures will be placed (Output_path_bad_structure)
    * c) Output file where all the csv's  with only retests will be placed (Output_path_processed_csv)
    * d) Output file where all the csv's  without SPT codes will be placed (Output_path_processed_csv)
    * e) Output file where all the processed csv's will be placed (Output_path_processed_csv)
2. Set the file paths for 1) under 'Input Variables' cell below. Also choose the filepath where you want the generated Report to be placed (Output_path_Report)
3. Set the delimiter 'Input Variables'. Generally csv files use a comma (,) but I have it set to pipe (|) as default
4. Run the code and wait

#%%----------------------------------------------------------------------------
# Finds all TDMS files in /measurements/organized by ticket number/
#   and updates faDatabase.xlsx
# 
# NOTE: If USNR or SensorNr already found in xlsx file, data will be reused. 
#       Deleting the xlsx file forces the rebuilding of the database!
#  
# Run with Python 3!
#------------------------------------------------------------------------------

from nptdms import TdmsFile as td
import pandas as pd
from collections import OrderedDict
import sqlite3

#------------------------------------------------------------------------------
# CONFIG
#------------------------------------------------------------------------------

# where to store the database with all the failure analysis data
con = sqlite3.connect('BMI284.db')

def reorder_columns(dataframe, col_name, position=0):
    """Reorder a dataframe's column.
    Args:
        dataframe (pd.DataFrame): dataframe to use
        col_name (string): column name to move
        position (0-indexed position): where to relocate column to
    Returns:
        pd.DataFrame: re-assigned dataframe
    """
    temp_col = dataframe[col_name]
    dataframe = dataframe.drop(columns=[col_name])
    dataframe.insert(loc=position, column=col_name, value=temp_col)
    return dataframe


#------------------------------------------------------------------------------
# Find all tdms files
#------------------------------------------------------------------------------
tdmsList=pd.read_csv('faFileList.csv')

faDb = pd.DataFrame() # create empty failure analysis database

#------------------------------------------------------------------------------
# Iterate through all found files
#------------------------------------------------------------------------------
n=len(tdmsList)
for i, tdms in tdmsList.iterrows(): # iterate through all found files
    #------------------------------------------------------------------------------
    # new part: parse tdms
    #------------------------------------------------------------------------------
    file = tdms.tdmsLocation
    print('[{:02.0f}%] new part: '.format(100*i/n) + file)
    data={}

    metadata=OrderedDict(td.read_metadata(file).properties.items())

    # add readouts
    tdms_file=td.read(file)
      
    MgIdx = tdms_file['Messgroessen']['Index'][:]
    MgMg = tdms_file['Messgroessen']['Messgroesse'][:]
    dicMg = dict(zip(MgIdx, MgMg))
    
    DataIdxMg = tdms_file['Messungen']['Index_Messgroesse'][:]
    DataNameMg = [dicMg[i] for i in DataIdxMg]

    Messwert = tdms_file['Messungen']['Messwert'].data

    ## Insert the Messgroesse, Messwert and StdDev in a dictionary
    for key, val in zip(DataNameMg,Messwert):
        # add the dc values:
        data.update({key:val})

    # add metadata
    data.update(metadata)

    # add folder name
    data.update({'tdmsLocation':tdms.tdmsLocation})
    data.update({'comment':tdms.comment})
    data.update({'isReference':tdms.isReference})
    data.update({'Remeas':tdms.isRemeas})

    # convert dict to dataframe
    df=pd.DataFrame.from_dict([data])
    
    df=df.rename(columns={'Sensor Nr':'SensorNr'}) # remove annoying whitespace
    df['SensorNr']=df['SensorNr'].astype(int)
    
    # put some important columns at the beginning
    df = reorder_columns(df,'comment')
    df = reorder_columns(df,'Remeas')
    if 'USNR' in metadata: 
        df = reorder_columns(df,'USNR')
    df = reorder_columns(df,'SensorNr')
    
    if faDb.size == 0: # If this is the first file that we are parsing
        faDb = df
    else:
        faDb=pd.concat([faDb,df])
    
# export
faDb.to_sql('TDMS_Data', con)

#faDb

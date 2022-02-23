#%%----------------------------------------------------------------------------
# Finds all TDMS files in /measurements/organized by ticket number/
#   and updates faDatabase.xlsx
# 
# NOTE: If USNR or SensorNr already found in xlsx file, data will be reused. 
#       Deleting the xlsx file forces the rebuilding of the database!
#  
# Run with Python 3!
#------------------------------------------------------------------------------


#import glob
#import os 
#import pathlib
import math
from nptdms import TdmsFile as td
#import numpy as np
import pandas as pd
from collections import OrderedDict
#import ftQuery
#import trQuery

#------------------------------------------------------------------------------
# CONFIG
#------------------------------------------------------------------------------


# where to store the database with all the failure analysis data
csvFilePath = 'BMI284_DB.csv' # try reusing existing data in xlsxFilePath?#reuse_xlsx = False

#def rename_v2_v3(df):
#    conv = pd.read_table('namingConversion_v2_v3.tsv')
#    convDict=conv.set_index('v2').to_dict('dict')['v3']
#    df=df.rename(columns=convDict)
#    # rename ac values
#    conv_ac = conv
#    conv_ac['v2']=conv_ac['v2'].astype(str)+':ac'
#    conv_ac['v3']=conv_ac['v3'].astype(str)+':ac'
#    convDict_ac=conv_ac.set_index('v2').to_dict('dict')['v3']
#    df=df.rename(columns=convDict_ac)
#    return df

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

#if queryFTdata:
#    ftCnxn = ftQuery.connectToFT() # connect to final test database and store its connection pointer

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
    Messgroesse = tdms_file['Messgroessen']['Messgroesse'].data
    Messwert =    tdms_file['Messungen']['Messwert'].data
    StdAbw =      tdms_file['Messungen']['StdAbw'].data
    Zeit =        tdms_file['Messungen']['Zeit'].data
    Einheit =     tdms_file['Messgroessen']['Einheit'].data

    # Insert the Messgroesse, Messwert and StdDev in a dictionary
    for key, val, std in zip(Messgroesse,Messwert,StdAbw):
        # add the dc values:
        data.update({key:val})
        # add the ac values
#        key=key+':ac'
#        if std == 0.0: # replace zero StdDev
#            std = math.nan
#        data.update({key:std})


#    --------------------
#     add final test data (only if USNR is available!)
#    --------------------
#    if 'USNR' in metadata and queryFTdata:
#        USNR = metadata['USNR']
#        ftData = ftQuery.getFTdata(ftCnxn,USNR)
#        data.update(ftData[['testname','testvalue']].values)
#        lot_id = ftQuery.getLotId(ftCnxn,USNR)
#        data.update({'lot_id':lot_id})
#     add metadata
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
    if 'USNR' in metadata: 
        df = reorder_columns(df,'USNR')
    df = reorder_columns(df,'SensorNr')

    # convert naming conventions from v2 to v3
    # if metadata['Kommentar'][0:6] == 'fa_v2.':
#    if 'A_out' in df.columns: # A_out was in the old naming convention
#        df = rename_v2_v3(df)

    if faDb.size == 0: # If this is the first file that we are parsing
        faDb = df
    else:
        faDb=pd.concat([faDb,df])
    
# export
faDb.to_csv(csvFilePath)

#faDb

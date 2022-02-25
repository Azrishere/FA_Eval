# Autor:        Bijan Mielke
# Date :        25.02.2022
# Description:  Script for statistical analysis of BMI284 sensors

import pandas as pd
from matplotlib import pyplot as plt
from rich import print                      # type: ignore

# Path for the Databases:
#------------------------
dataPath = 'BMI284_DB.csv'                  
conversionPath = 'Specs\BMI284_conversion.csv'    #Database for the Values to check, conversion factors and the Spec 


#Settings:
#---------
Sensor = '0000H2NH52019028050KY'
checkSensor = 0
compareToRef = 0
compareToAll = 0
testMultiple = 1


#Init the Databases:      
#--------------------

print(f'\nLoading Database... \n ')
faDB = pd.read_csv(dataPath, index_col='USNR')
conv = pd.read_csv(conversionPath)
data = faDB.loc[Sensor]
print(f'done \n')


#Definition of Functions:
#-------------------------
def checkMultiple():
    print('Multiple Sensors with this USNR found')
    #for index in data:
    #    print(index : data)
    selection = input('Wich of the Listed Sensors should be used? \n Pos Number:      ') 
    selData = data.iloc[int(selection)]
    Sensor = selData.name
    return Sensor           

## Loads the Data of a Sensor with given ID
def loadData():
    if data.shape[0] > 1:
        Sensor = checkMultiple(Sensor)              
    print(f'Loading Data for the Sensor     USNR: {Sensor} \n')
    data = faDB.loc[Sensor]
    print(f'done \n')
    return data

## Data Conversion and FA like Output with markup of suspicious Values
def evaluateData(data):
    print(f'Evaluating Data:')
    for index, Measurement in conv.iterrows():    
        para = conv.iloc[index]
        Meas = para['Measurement']
        #calculate Values for CM_inSens Parameters
        if 'AIAA' in Meas:                        
            MeasMean = data['g:rate_x:CM_inSens_PD_AIAA_pos:mean'] - data['g:rate_x:CM_inSens_PD_AIAA_neg:mean']
            MeasStd = data['g:rate_x:CM_inSens_PD_AIAA_pos:std'] - data['g:rate_x:CM_inSens_PD_AIAA_neg:std']
        elif 'AI' in Meas:
            MeasMean = data['g:rate_x:CM_inSens_PD_AI_pos:mean'] - data['g:rate_x:CM_inSens_PD_AI_neg:mean']
            MeasStd = data['g:rate_x:CM_inSens_PD_AI_pos:std'] - data['g:rate_x:CM_inSens_PD_AI_neg:std']
        elif 'AA' in Meas:
            MeasMean = data['g:rate_x:CM_inSens_PD_AA_pos:mean'] - data['g:rate_x:CM_inSens_PD_AA_neg:mean']
            MeasStd = data['g:rate_x:CM_inSens_PD_AA_pos:std'] - data['g:rate_x:CM_inSens_PD_AA_neg:std']
        elif 'S31' in Meas:
            MeasMean = data['g:rate_x:CM_in_Sens_pos:mean'] - data['g:rate_x:CM_in_Sens_neg:mean']
            MeasStd = data['g:rate_x:CM_in_Sens_pos:std'] - data['g:rate_x:CM_in_Sens_neg:std']
        else:    
            MeasMean = data[para['Mean']]
            #catch empty Std lines
            try:
                MeasStd = data[para['Std']]
            except KeyError:
                MeasStd = 0

        #Convert Data
        ConvMean = MeasMean * para['Conversion']
        ConvStd = MeasStd * para['Conversion']
        if 'CV_D_in_Sens' == Meas:
            ConvMean = abs(ConvMean)
        
        #Output in FA Script Values
        if ConvMean > para['Min'] and ConvMean < para['Max']:
            print('{0:28} = {1:20} : {2:40}'.format(Meas, ConvMean, 'is in Spec'))
            continue
        elif ConvMean < para['Min']:
            print('{0:28} = {1:20} : {2:40}'.format(Meas, ConvMean, '[red]Mean is too low[/]')) 
        else:
            print('{0:28} = {1:20} : {2:40}'.format(Meas, ConvMean, '[red]Mean is too high[/]')) 

        if ConvStd < para['Std_max'] or ConvStd == 0:
            print('{0:28} = {1:20} : {2:40}'.format(Meas, ConvStd, 'is in Spec'))
            continue
        else:
            print('{0:28} = {1:20} : {2:20}'.format(Meas, ConvStd, '[yellow]Noise is too high[/]'))  
    print('\n --------------------All other Values are in Spec-------------------- \n')


# Function Calls:
#--------------------
if checkSensor == 1:
    SensorData = loadData()
    evaluateData(SensorData)

if testMultiple == 1:
    testVar = checkMultiple()
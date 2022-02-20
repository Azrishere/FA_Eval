# Autor:        Bijan Mielke
# Date :        13.02.2022
# Description:  Script for statistical analysis of BMI284 sensors


from matplotlib import pyplot as plt
import pandas as pd
#from nptdms import TdmsFile

dataPath = 'BMI284_DB.csv'
conversionPath = 'BMI284_conversion.csv'
Sensor = '0000H6K250004036038KY'
compareToRef = 0
compareToAll = 0

faDB = pd.read_csv(dataPath, index_col='USNR')
conv = pd.read_csv(conversionPath)

data = faDB.loc[Sensor]
#print(data)
#print(conv) 

#print(conv['Measurement'])

#MeasMean = conv['Mean']
#MeasStd = conv['Std']
#MeasConv = conv['Conversion']
#MeasMin = conv['Min']
#MeasMax = conv['Max']
#MeasStd_max = conv['Std_max']

#for Measurement in conv.iterrows():

'''
test if one Value can be converted and checked correctly before iterating over all values
CV_D_wodrivewoCM
'''
para = conv.iloc[6]

if data.size != 0:      #check if Sensor is listed in DB
    Meas = para['Measurement']
    MeasMean = data[para['Mean']]
    ConvMean = MeasMean * para['Conversion']
    if ConvMean > para['Min'] and ConvMean < para['Max']:
        print(f'{Meas} = {ConvMean} : is in Spec')
    else:
        print(f'{Meas} = {ConvMean} : is out of Spec')
    
else:
    print('ERROR: USNR not found')
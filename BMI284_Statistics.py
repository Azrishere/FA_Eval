# Autor:        Bijan Mielke
# Date :        13.02.2022
# Description:  Script for statistical analysis of BMI284 sensors


from matplotlib import pyplot as plt
import pandas as pd
#from nptdms import TdmsFile

dataPath = 'BMI284_DB.csv'
conversionPath = 'BMI284_conversion.xlsx'
Sensor = '0000H6K250004036038KY'
compareToRef = 0
compareToAll = 0

faDB = pd.read_csv(dataPath, index_col='USNR')
conv = pd.read_excel(conversionPath)

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

if data == 0:
    print('error no data found')
#if elif 
    
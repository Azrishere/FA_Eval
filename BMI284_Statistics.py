# Autor:        Bijan Mielke
# Date :        13.02.2022
# Description:  Script for statistical analysis of BMI284 sensors

from contextlib import suppress
from matplotlib import pyplot as plt
from numpy import isnan
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

for index, Measurement in conv.iterrows():
    para = conv.iloc[index]
    Meas = para['Measurement']
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
        try:
            MeasStd = data[para['Std']]
        except KeyError:
            MeasStd = 0
        
    ConvMean = MeasMean * para['Conversion']
    ConvStd = MeasStd * para['Conversion']
    if 'CV_D_in_Sens' == Meas:
        ConvMean = abs(ConvMean)
    if ConvMean > para['Min'] and ConvMean < para['Max']:
        #print(f'{Meas} = {ConvMean} : is in Spec')
        continue
    elif ConvMean < para['Min']:
        print(f'{Meas} = {ConvMean} : Mean is too low')
    else:
        print(f'{Meas} = {ConvMean} : Mean is too high') 

    if ConvStd < para['Std_max']:
        #print(f'{Meas} = {ConvMean} : is in Spec')
        continue
    else:
        print(f'{Meas} = {ConvStd} : Noise is too high') 
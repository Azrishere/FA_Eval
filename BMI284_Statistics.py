# Autor:        Bijan Mielke
# Date :        13.02.2022
# Description:  Script for statistical analysis of BMI284 sensors

from contextlib import suppress
from matplotlib import pyplot as plt
import pandas as pd
#from nptdms import TdmsFile

dataPath = 'BMI284_DB.csv'
conversionPath = 'BMI284_conversion.csv'
Sensor = '0000H2MH42021035014KY'
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
    elif 'AI' in Meas:
        MeasMean = data['g:rate_x:CM_inSens_PD_AI_pos:mean'] - data['g:rate_x:CM_inSens_PD_AI_neg:mean']
    elif 'AA' in Meas:
        MeasMean = data['g:rate_x:CM_inSens_PD_AA_pos:mean'] - data['g:rate_x:CM_inSens_PD_AA_neg:mean']
    elif 'S31' in Meas:
        MeasMean = data['g:rate_x:CM_in_Sens_pos:mean'] - data['g:rate_x:CM_in_Sens_neg:mean']
    else:    
        MeasMean = data[para['Mean']]
    ConvMean = MeasMean * para['Conversion']
    if 'CV_D_in_Sens' == Meas:
        ConvMean = abs(ConvMean)
    if ConvMean > para['Min'] and ConvMean < para['Max']:
        #print(f'{Meas} = {ConvMean} : is in Spec')
        continue
    elif ConvMean < para['Min']:
        print(f'{Meas} = {ConvMean} : is too low')
    else:
        print(f'{Meas} = {ConvMean} : is too high') 
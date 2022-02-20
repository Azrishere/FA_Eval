# Autor:        Bijan Mielke
# Date :        13.02.2022
# Description:  Script for statistical analysis of BMI284 sensors


from matplotlib import pyplot as plt
import pandas as pd
from nptdms import TdmsFile
#from numpy import *


Eintrag = 'ref01'
schreiben = 1
lesen = 0
darstellen = 0


tdms_file = TdmsFile.read('TDMS/BMI284_ref01.tdms')
datenbank = pd.read_csv("BMI284_database.csv")

Messwert = pd.DataFrame(tdms_file['Messungen']['Messwert'])
USNR = pd.DataFrame([tdms_file.properties['USNR']])
Nummer = pd.DataFrame([tdms_file.properties['Sensor Nr']])
Sensordata = pd.concat([USNR, Nummer, Messwert], ignore_index=True)
print(Sensordata)

if lesen == 1:
    print(datenbank)

if schreiben == 1:
    datenbank[Eintrag] = Sensordata[0:290]
    print(datenbank)
    datenbank.to_csv('BMI284_database_test.csv', index=False)

if darstellen == 1:
    daten = datenbank.apply(pd.to_numeric, errors='coerce')
    row = daten.iloc[5]
    print(row)
    ax = row.plot(style='o', title='wodrive')
    ax.axhline(y=2, color='red')
    ax.axhline(y=-2, color='red')

    plt.show()

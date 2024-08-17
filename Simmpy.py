import numpy as np
import sys
import os
import pandas as pd
import scipy.constants as sc
import matplotlib.pyplot as plt
import Unitconversions as cf
import Glidecharpy
import Ballisticpy
import requests
from geopy.distance import geodesic
from geopy.point import Point
import webbrowser

file_path = 'ESTUDO DE MERCADO UAS.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')  

#METAR AQUISITION

ICAO = 'LPPT'
Box = [39.15583333333333, -8.160277777777777, -7.897500000000019, -45]
Box = []
METARres = requests.get(f"https://aviationweather.gov/api/data/metar?ids={ICAO}&format=geojson&bbox=40,-90,45,-45")


print(METARres.content)

METAR = METARres.json()

TSL = METAR["features"][1]["properties"]["temp"]

PSL = METAR["features"][1]["properties"]["altim"]

windspd = METAR["features"][1]["properties"]["wspd"]

draft = 0

windheading = METAR["features"][1]["properties"]["wdir"]
if windheading == 'VRB' :

    windheading = 0



windspd = METAR["features"][1]["properties"]["wspd"]

timeretr = METAR["features"][1]["properties"]["obsTime"]

################################################################

copter = []
fixedwing = []

start_index = 91
end_index = min(119, df.shape[0]) 

for i in range(start_index, end_index):
    if pd.notna(df.iloc[i, 0]):  
        data_row = [
            df.iloc[i, 0], # Name
            df.iloc[i, 14],  # Ceiling
            df.iloc[i, 16],  # Endurance
            df.iloc[i, 22],  # MTOM
            df.iloc[i, 26],  # AR
            df.iloc[i, 28],  # Wing Area
            df.iloc[i, 40],  # Cd0
            df.iloc[i, 42], # Oswald efficiency factor  
        ]
        
        fixedwing.append(data_row)

start_index = 6
end_index = min(32, df.shape[0]) 

for i in range(start_index, end_index):
    if pd.notna(df.iloc[i, 0]):  
        data_rowquad = [
            df.iloc[i, 0], # Name
            df.iloc[i, 6],  # Max speed hor
            df.iloc[i, 10],  # Max wind resistance
            df.iloc[i, 14],  # Ceiling
            df.iloc[i, 16],  # Endurance hours
            df.iloc[i, 18],  # Endurance KM
            df.iloc[i, 22],  # MTOM(Kg)
            0.105+ float(df.iloc[i, 22])*0.087, # Cd
        ]
        
        copter.append(data_rowquad)




#AIRCRAFT POSTION AND ATTITUDE

aircrafthdg = 0
phi = 0
initial_latitude = 38.7800  
initial_longitude = -9.1342
initial_position = [initial_latitude, initial_longitude]



# print(fixedwing)
#print(fixedwing[1][1], fixedwing[1][3], fixedwing[1][4], fixedwing[1][5], fixedwing[1][6], fixedwing[1][7])

#print (PSL, TSL, aircrafthdg, windheading, windspd, draft, copter[0][1], copter[0][2], copter[0][3], copter[0][4], copter[0][5], copter[0][6], copter[0][7], phi)


resultfx = Glidecharpy.glide_characteristics(PSL, TSL, aircrafthdg, windheading, windspd, draft, fixedwing[0][1], fixedwing[0][3], fixedwing[0][4], fixedwing[0][5], fixedwing[0][6], fixedwing[0][7], phi)

resultquad = Ballisticpy.trajectoryprediction(PSL, TSL, aircrafthdg, windheading, windspd, draft, copter[0][1], copter[0][2], copter[0][3], copter[0][4], copter[0][5], copter[0][6], copter[0][7], phi)





initial_position = (initial_latitude, initial_longitude)

distance_traveledfx = resultfx[10]
distance_traveledquad = resultquad[2]

finalposition = []

print(distance_traveledquad, distance_traveledfx, 'DISTANCES TRAVELLED')

finalposition.append(geodesic(meters=distance_traveledfx).destination(initial_position, resultfx[8][1]))
finalposition.append(geodesic(meters=distance_traveledquad).destination(initial_position, resultquad[3]))


webbrowser.open(f"https://www.google.com/maps?q={initial_latitude},{initial_longitude}")
for pos in finalposition:
    final_latitude, final_longitude = pos.latitude, pos.longitude
    print(f"Latitude final: {final_latitude}, Longitude final: {final_longitude}")

    # Open Google Maps for initial and final positions
    
    webbrowser.open(f"https://www.google.com/maps?q={final_latitude},{final_longitude}")

#Formato decimal do wgs84
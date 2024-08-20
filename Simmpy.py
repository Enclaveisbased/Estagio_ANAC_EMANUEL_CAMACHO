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

    

def fix(TSL, PSL, initial_latitude, initial_longitude, aircrafthdg, windspd, windhdg, ceiling, MTOM, AR, WA, Cd0, oswald, phi) :
    Tslk = TSL + 273.15
    P = PSL * 100 * (1 - (ceiling * 0.0065 / 288.15))**5.25588
    Tk = Tslk - 0.0065 * ceiling
    A = 0.058*0.067
    a = 340.294 * np.sqrt(Tk / 288.15)
    rho = P / (287.052874 * Tk)
    phi = 0
    draft = 0
    if windhdg == 'VRB' :

         windheading = 0


        ################################################################
        #AIRCRAFT POSTION AND ATTITUDE

        
    initial_position = [initial_latitude, initial_longitude]


    resultfx = Glidecharpy.glide_characteristics(PSL, TSL, aircrafthdg, windhdg, windspd, draft, ceiling, MTOM, AR, WA, Cd0, oswald, phi)

    initial_position = (initial_latitude, initial_longitude)

    distance_traveledfx = resultfx[10]

    finalposition = geodesic(meters=distance_traveledfx).destination(initial_position, resultfx[8][1])
    


    webbrowser.open(f"https://www.google.com/maps?q={initial_latitude},{initial_longitude}")
            
    webbrowser.open(f"https://www.google.com/maps?q={finalposition[0]},{finalposition[1]}")

    #Formato decimal do wgs84
    return(finalposition[0], finalposition[1], resultfx)






def quad(PSL, TSL, aircrafthdg, initial_latitude, initial_longitude, windhdg, windspd, draft, vhor, ceiling, MTOM, Cd0, A):
    
    draft = 0

    initial_position = (initial_latitude, initial_longitude)
    
    resultquad = Ballisticpy.trajectoryprediction(PSL, TSL, aircrafthdg, windhdg, windspd, draft, vhor, ceiling, MTOM, Cd0, A)
    

    distance_traveledq = resultquad[2]
    
    
    finalposition = geodesic(meters=distance_traveledq).destination(initial_position, resultquad[2])
    webbrowser.open(f"https://www.google.com/maps?q={initial_latitude},{initial_longitude}")
            
    webbrowser.open(f"https://www.google.com/maps?q={finalposition[0]},{finalposition[1]}")
  
    return(finalposition[0], finalposition[1], resultquad)

    

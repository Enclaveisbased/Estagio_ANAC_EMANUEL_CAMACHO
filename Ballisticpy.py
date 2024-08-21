import numpy as np
from pyproj import Proj, Transformer
import scipy.constants as sc
import math
import matplotlib.pyplot as plt 
import scipy.integrate
import Unitconversions as cf
from scipy.optimize import fsolve
g = 9.81
def trajectoryprediction(Psl, Tsl, crafthdg, windhdg, Wspdkt, draft, vhor, hmax, M, Cd, A):

    if windhdg == 'VRB' :

         windhdg= 0

    # Atmospheric conditions calculation based on SL values
    Tslk = Tsl + 273.15
    P = Psl * 100 * (1 - (hmax * 0.0065 / 288.15))**5.25588
    Tk = Tslk - 0.0065 * hmax
    a = 340.294 * np.sqrt(Tk / 288.15)
    rho = P / (287.052874 * Tk)

    #print(P, Tk, a, rho)

    #Wind adjustment

    ex_craft = np.sin(np.deg2rad(crafthdg))
    ey_craft = np.cos(np.deg2rad(crafthdg))
    ez_craft = 0


    

    windspddrag = Wspdkt/2 #Calculate the terminal horizontal velocity with drag and approximate the movement for a constat speed
    
    x_wind = windspddrag * np.cos(np.pi/2 - np.deg2rad(windhdg))
    y_wind = windspddrag * np.sin(np.pi/2 - np.deg2rad(windhdg))
    z_wind = draft
    wind = np.array([x_wind, y_wind]) #All in knots

    

    #Initial conditions

    windm = cf.convvel(wind, 'kts', 'm/s')

    vx0 = ex_craft*vhor #m/s
    vy0 = ey_craft*vhor

    k = 0.5*rho*Cd*A

    ############## Motion quantities #####################################################################################################################
    
    falltime = np.arccosh(np.e**(hmax*k/M))*np.sqrt(M/(g*k))

    vhormax = 1/((1/vhor)+k*falltime)

    vzf = -np.sqrt(M*g/k)*np.tanh(np.sqrt(k*g/M)*falltime)

    vf = np.linalg.norm(vhormax+vzf)

    ############ Horizontal distance determination ########################################################################################################


    dhordragonly = np.array([ex_craft, ey_craft])*(np.log(k*vhor*falltime+1))/k

    dhorduetowind = windm*falltime

    dhor = dhordragonly - dhorduetowind # Seperate wind from initial speed drag effects to simplify equations, for headwinds this will mean a bigger ground track than in reality and vice-versa

    dhorval = np.linalg.norm(dhor)

    dx = dhor[0]

    dy = dhor[1]


    #Important quantities

    terminalv = -np.sqrt(M*g/k)
    

    

    Dxf = k*ex_craft*vhormax**2
    Dyf = k*ey_craft*vhormax**2
    Dzf = -k*terminalv**2


    Total_Forcef = [ex_craft*Dxf, ey_craft*Dyf, Dzf-g*M]

    Total_Force = np.linalg.norm([ex_craft*Dxf, ey_craft*Dyf, Dzf-g*M])

    velocity = [vhormax*ex_craft, vhormax*ey_craft, vzf]

    gshdg = np.rad2deg((np.pi / 2 - np.arctan2(dy, dx)))%360

    windhdg = np.rad2deg((np.pi / 2 - np.arctan2(y_wind, x_wind)))%360


    ############ DEBUG SECTION #####################################################################################################################
    
    print(dhor, gshdg, 'QUAD GS HDG')

    gsnwd = np.rad2deg((np.pi / 2 - np.arctan2(ey_craft, ex_craft)))%360

    print('GS copter', gshdg, windhdg, windhdg, terminalv, Dzf, cf.convvel(vhormax, 'm/s', 'kts'))


    tvec = np.linspace(0, falltime, 100)

    dxv = ex_craft * (np.log(k*vhor*tvec+1))/k - windm[0]*tvec
    dzv = -(M/k)*np.log(np.cosh(np.sqrt(k*g/M)*tvec))+hmax 
    dyv = ey_craft * (np.log(k*vhor*tvec+1))/k  - windm[1]*tvec
    print(dxv, dyv, dzv)

    return (terminalv, falltime, dxv, dyv, dzv, dhorval, gshdg, vf)
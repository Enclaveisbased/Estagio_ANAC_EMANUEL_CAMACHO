import numpy as np
from pyproj import Proj, Transformer
import scipy.constants as sc
import math
import matplotlib.pyplot as plt 
import scipy.integrate
import Unitconversions as cf
from scipy.optimize import fsolve
g = 9.81
def trajectoryprediction(Psl, Tsl, crafthdg, Whdg, Wspdkt, draft, maxhor, Windres, hmax, Endhours, Endkm, M, Cd, phi):

    

    # Atmospheric conditions calculation based on SL values
    Tslk = Tsl + 273.15
    P = Psl * 100 * (1 - (hmax * 0.0065 / 288.15))**5.25588
    Tk = Tslk - 0.0065 * hmax
    A = 0.020
    a = 340.294 * np.sqrt(Tk / 288.15)
    rho = P / (287.052874 * Tk)

    #print(P, Tk, a, rho)

    #Wind adjustment

    ex_craft = np.sin(np.deg2rad(crafthdg))
    ey_craft = np.cos(np.deg2rad(crafthdg))
    ez_craft = 0


    

    windspddrag = Wspdkt/2 #Calculate the terminal horizontal velocity with drag and approximate the movement for a constat speed
    
    x_wind = windspddrag * np.cos(np.pi/2 - np.deg2rad(Whdg))
    y_wind = windspddrag * np.sin(np.pi/2 - np.deg2rad(Whdg))
    z_wind = draft
    wind = np.array([x_wind, y_wind, draft]) #All in knots

    #Initial conditions

    windm = cf.convvel(wind, 'kts', 'm/s')

    vx0 = ex_craft*maxhor #m/s
    vy0 = ey_craft*maxhor

    k = 0.5*rho*Cd*A

    #Motion equations
    
    falltime = np.arccosh(np.e**(hmax*k/M))*np.sqrt(M/(g*k))

    #print('Falltime : ', falltime)

    tins = np.arange(0, 300, 0.5)

    #print('ACT WIND', Whdg, Wspdkt)

    vhormax = 1/((1/maxhor)+k*falltime)

    vzf = -np.sqrt(M*g/k)*np.tanh(np.sqrt(k*g/M)*falltime)

    dhor = (np.log(k*np.linalg.norm([vx0, vy0])*falltime))/k
    
    #print(k*np.linalg.norm([vx0, vy0])*falltime)

    dz = -(M/k)*np.log(np.cosh(np.sqrt(k*g/M)*falltime))+hmax
    dx = dhor*ex_craft - falltime*windm[0] #Approximation : Calculating the wind movement and "ballistic" movement separately and then adding them
    dy = dhor*ey_craft - falltime*windm[1]

    #print('METHOD CLASH', -falltime*windm[0], -falltime*windm[1], dhor*ex_craft, dhor*ey_craft)

    dhor = np.sqrt(dx**2 + dy**2)


    #Important quantities

    terminalv = -np.sqrt(M*g/k)

    

    Dxf = k*ex_craft*vhormax**2
    Dyf = k*ey_craft*vhormax**2
    Dzf = -k*terminalv**2


    Total_Forcef = [ex_craft*Dxf, ey_craft*Dyf, Dzf-g*M]

    Total_Force = np.linalg.norm([ex_craft*Dxf, ey_craft*Dyf, Dzf-g*M])

    velocity = [vhormax*ex_craft, vhormax*ey_craft, vzf]

    gshdg = np.rad2deg((np.pi / 2 - np.arctan2(dy, dx)))%360

    whdg = np.rad2deg((np.pi / 2 - np.arctan2(y_wind, x_wind)))%360

    dhorhdg = np.rad2deg((np.pi / 2 - np.arctan2( dhor*ey_craft, dhor*ex_craft)))%360

    #print(dhor, gshdg, 'QUAD GS HDG')

    #gsnwd = np.rad2deg((np.pi / 2 - np.arctan2(ey_craft, ex_craft)))%360

    #print('GS copter', gshdg, whdg, dhorhdg, Whdg, terminalv, Dzf, cf.convvel(vhormax, 'm/s', 'kts'))


    return (falltime, terminalv, dhor, gshdg)
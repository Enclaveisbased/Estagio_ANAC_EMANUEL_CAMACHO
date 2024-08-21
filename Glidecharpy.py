import numpy as np
import scipy.constants as sc
import matplotlib.pyplot as plt
import Unitconversions as cf

# Define the main function
def glide_characteristics(Psl, Tsl, crafthdg, Whdg, Wspdkt, draft, hm, M, A, Sm, C_D0, e, phi):
    # Quantities Definition
    

    Wm = M * sc.g  # weight, N
    W = cf.convforce(Wm, 'N', 'lbf')  # weight, lbf
    S = Sm / 0.09290304  # wing reference area, ft^2

    # Atmospheric conditions calculation based on SL values
    Tslk = Tsl + 273.15
    P = Psl * 100 * (1 - (hm * 0.0065 / 288.15))**5.25588
    Tk = Tslk - 0.0065 * hm
    a = 340.294 * np.sqrt(Tk / 288.15)
    rho = P / (287.052874 * Tk)
    rhosl = cf.convdensity(rho, 'kg/m^3', 'slug/ft^3')
    # Wind variables
    
    ex_craft = np.sin(np.deg2rad(crafthdg))
    ey_craft = np.cos(np.deg2rad(crafthdg))
    x_wind = Wspdkt * np.cos(np.pi/2 - np.deg2rad(Whdg)) #Transfering my 0 degrees origin to pi/2 or north, in this case, sin will represent horizontal distance
    y_wind = Wspdkt * np.sin(np.pi/2 - np.deg2rad(Whdg)) #Transfering my 0 degrees origin to pi/2 or north 
    z_wind = draft
    wind = np.array([x_wind, y_wind])
    wind = cf.convvel(wind, 'kts', 'ft/s')
    
    # Optimized glide TAS, CAS, and glide angle calculation
    TAS_bg = np.sqrt((2 * W) / (rhosl * S)) * ((1 / ((4 * C_D0**2) + (C_D0 * np.pi * e * A * (np.cos(np.deg2rad(phi))**2))))**0.25)
    KTAS_bg = cf.convvel(TAS_bg, 'ft/s', 'kts')

    print(f"TAS_bg (ft/s): {TAS_bg}")
    print(f"KTAS_bg (knots): {KTAS_bg}")

    KCAS_bg = cf.correctairspeed(KTAS_bg, a, P, 'TAS', 'CAS')
    gamma_bg_rad = -np.arctan(np.sqrt((4 * C_D0) / (np.pi * A * e)))
    gamma_bg = cf.convang(gamma_bg_rad, 'rad', 'deg')

    # Sink rate calculation
    fpstruevspeed = TAS_bg * np.sin(gamma_bg_rad)
    fpm = fpstruevspeed * 60
    G = 0.5 * rhosl * S * C_D0
    Hphi = 2 * (W**2) / (rhosl * S * np.pi * e * A * (np.cos(np.deg2rad(phi))**2))
    minfps = -4 * ((3 * G * Hphi**3)**0.25) / (3 * W)
    TASminskinrate_bg = (Hphi / (3 * G))**0.25
    KTASminsinkrate = cf.convvel(TASminskinrate_bg, 'ft/s', 'kts')
    print('FPM RATE', fpm)
    minfpm = minfps * 60

    # Ground speed calculation
    TAS_bgvec = TAS_bg * np.cos(gamma_bg_rad) * np.array([ex_craft, ey_craft]) #Calculate hor component of TAS and then x and y coords

    print(TAS_bgvec)
    #print(wind, np.linalg.norm(wind))
    GS_bgvec = TAS_bgvec - wind
    GS_hdg = np.rad2deg((np.pi / 2 - np.arctan2(GS_bgvec[1], GS_bgvec[0])))%360
    GS_reskthdg = [cf.convvel(np.linalg.norm(GS_bgvec), 'ft/s', 'kts'), GS_hdg]
    if not np.array_equal(wind, [0, 0]):
        gamma_bg = np.degrees(np.arcsin(fpstruevspeed / np.linalg.norm(TAS_bgvec - wind)))

    # Aerodynamic quantities calculation
    D_bg = -W * np.sin(gamma_bg_rad)
    D_m = cf.convforce(D_bg, 'lbf', 'N')
    L_bg = W * np.cos(gamma_bg_rad)
    L_m = cf.convforce(L_bg, 'lbf', 'N')
    qbar = qbar = cf.dpressure(np.array([[TAS_bg]]), rhosl) 
    qmet = cf.convpres(qbar, 'psf', 'Pa')
    C_D_bg = D_bg / (qbar * S)
    C_L_bg = L_bg / (qbar * S)
    C_D_met = D_m / (qmet * Sm)
    C_L_met = L_m / (qmet * Sm)

    # Verification of Drag minimization and L/D optimization
    TASver = np.arange(0.5*np.round(TAS_bg), 1.5*np.round(TAS_bg), 0.5)
    KTASver = cf.convvel(TASver, 'ft/s', 'kts')
    KCASver = cf.correctairspeed(KTASver, a, P, 'TAS', 'CAS')
    qbarver = cf.dpressure(np.column_stack([TASver, np.zeros((len(TASver), 2))]), rhosl)
    Dp = qbarver * S * C_D0
    Dpm = cf.convforce(Dp, 'lbf', 'N')
    Di = (2 * W**2) / (rhosl * S * np.pi * e * A) * (TASver**-2)
    Dim = cf.convforce(Di, 'lbf', 'N')
    D = Dp + Di
    Dm = cf.convforce(D, 'lbf', 'N')

    # Find max L/D
    L = Wm
    Maxx, Indd = np.max(L / Dm), np.argmax(L / Dm)
    MaxxLDTAS = KCASver[Indd]

    # Plotting
    plt.figure()
    plt.plot(KCASver, L / Dm, label='L/D')
    plt.plot(KCAS_bg, L_m / D_m, 'o', markerfacecolor='black', markeredgecolor='black', color='white', label='L_bg/D_bg')
    plt.plot(MaxxLDTAS, Maxx, 'o', markerfacecolor='red', markeredgecolor='black', color='white', label='L/D_max')
    plt.title('L/D vs. KCAS')
    plt.xlabel('KCAS in knots')
    plt.ylabel('L/D')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(KCASver, Dpm, label='Parasitic Drag')
    plt.plot(KCASver, Dim, label='Induced Drag')
    plt.plot(KCASver, Dm, label='Total Drag')
    plt.plot(KCAS_bg, D_m, 'o', markerfacecolor='black', markeredgecolor='black', color='white', label='D_bg')
    plt.plot(KCASver[Indd], Dm[Indd], 'o', markerfacecolor='red', markeredgecolor='black', color='white', label='D_min')
    plt.title('Parasitic, Induced, and Total Drag vs. KCAS')
    plt.xlabel('KCAS in knots')
    plt.ylabel('Drag, Newtons')
    plt.legend()
    plt.show()


    traveltime = hm/(cf.convvel(-fpstruevspeed, 'ft/s', 'm/s'))

    
    traveldistance = traveltime*cf.convvel(GS_reskthdg[0], 'kts', 'm/s')
    #print(traveltime, cf.convvel(GS_reskthdg[0], 'kts', 'm/s'), traveldistance)
    print('GS fixed wing', GS_reskthdg)

    tvec = np.linspace(0, traveltime, 100)
    dxv = tvec*cf.convvel(GS_reskthdg[0], 'kts', 'm/s') * np.cos(np.pi/2 - np.deg2rad(GS_reskthdg[1]))
    dzv = hm+tvec*cf.convvel(fpstruevspeed, 'ft/s', 'm/s') 
    dyv = tvec*cf.convvel(GS_reskthdg[0], 'kts', 'm/s') * np.sin(np.pi/2 - np.deg2rad(GS_reskthdg[1]))
    
    print(dxv, dyv, dzv)


    TAS_m = cf.convvel(TAS_bg, 'ft/s', 'm/s')

    return [TAS_m, traveltime, dxv, dyv, dzv, KTASminsinkrate, KCAS_bg, KCASver[Indd], KTASver[Indd], GS_reskthdg, traveldistance]


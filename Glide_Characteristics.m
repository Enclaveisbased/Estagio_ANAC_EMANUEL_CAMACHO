function res = Glide_Characteristics(Psl, Tsl, crafthdg, Whdg, Wspdkt, draft)

%% Quantities Definition

hm = 4000*0.3048; % altitude, m
C_D0 = 0.037; % flaps up parasite drag coefficient
M = 757; %1089.36020408; %Mass in kg
Sm = 15; %16.1651
A = 6.7; %7.38; % wing aspect ratio
e = 0.72; % airplane efficiency factor
phi = 0; % bank angle, deg



Wm = M*9.81; % weight, N
W = convforce(Wm, 'N', 'lbf'); % weight, lbf
S = Sm/0.09290304;  % wing reference area, ft^2;


%% Atmospheric conditions calculation based on SL values

Tslk = Tsl + 273.15;

P = Psl*100*(1-(hm*0.0065/288.15)).^(5.25588);

Tk = Tslk - 0.0065*hm;

a = 340.294 * sqrt(Tk/288.15);

rho = (P/(287.052874*Tk));

rhosl = convdensity(rho, 'kg/m^3','slug/ft^3');


%% Wind variables


ex_craft = sind(crafthdg);
ey_craft = cosd(crafthdg);

x_wind = Wspdkt * sind(Whdg);
y_wind = Wspdkt * cosd(Whdg);
z_wind = draft;


wind = [x_wind, y_wind];




%% Optimized glide TAS,CAS and glide angle calculation method 1

% Note that the formulas used return values in British Gravitational Units
% for easier access to rates in fpm

TAS_bg = sqrt( (2*W)/(rhosl*S) )*( 1./( (4*C_D0.^2) + (C_D0.*pi*e*A*(cos(phi)^2)) )).^(1/4); %Deduced by hand check notes and addition made via the book

%Note that this equation includes the small angle approximation

KTAS_bg = convvel(TAS_bg,'ft/s','kts')';


KCAS_bg = correctairspeed(KTAS_bg, a, P,'TAS','CAS')';


gamma_bg_rad = -atan(sqrt((4*C_D0)/(pi*A*e))); %Deduced by hand check notes


gamma_bg = convang(gamma_bg_rad,'rad','deg');





%% SINK RATE CALCULATION

% For optimized glide distance

fpstruevspeed = TAS_bg * sin(gamma_bg_rad);

fpm = fpstruevspeed * 60;

%For maximum air time or minimum sink rate

%Book method

G = 0.5*rhosl*S*C_D0;

Hphi = 2*(W^2)/((rhosl*S*pi*e*A*(cos (phi)).^2));

minfps = -4*((3*G*Hphi^3).^(1/4))/(3*W); %Note that this equation is an approximation valid up until 50 knots of headwind (60 blows up the values) source: pg.310

TASminskinrate_bg = ((Hphi/(3*G)).^(1/4));

KTASminsinkrate = convvel(TASminskinrate_bg, 'ft/s', 'kts');

minfpm = minfps*60;

%% GROUND SPEED CALCULATION 

%Made manually still not verified

TAS_bgvec = TAS_bg*[ex_craft, ey_craft];


GS_bgvec = TAS_bgvec-wind; %Note that this is a subtraction due to how wind is presented in METAR data

GS_hdg = (pi/2-atan2(GS_bgvec(2), GS_bgvec(1)))*(180/pi);

if GS_hdg < 0
    GS_hdg = GS_hdg + 360;
end

GS_reskthdg = [convvel(norm(GS_bgvec), 'ft/s','kts'), GS_hdg];

if wind ~= [0, 0] %Checks for wind in order to avoid any issues with changing the glide angle

  disp('WIND DETECTED')

gamma_bg = asind(fpstruevspeed/(norm(TAS_bgvec-wind))); % Glide angle correction based on tail/head wind
end

%% AERODYNAMIC QUANTITIES CALCULATION

D_bg = -W*sin(gamma_bg_rad);    % Constant speed implies that Drag is countered only by the weight component in the velocity vector's direction

D_m = convforce(D_bg, 'lbf', 'N'); 

L_bg =  W*cos(gamma_bg_rad);

L_m = convforce(L_bg, 'lbf', 'N');

qbar = dpressure([TAS_bg zeros(size(TAS_bg,1),2)], rhosl);

qmet = convpres(qbar, 'psf', 'Pa');

C_D_bg = D_bg./(qbar*S);

%C_L_bgalt = sqrt(C_D0*pi*e*A) % Verification of calculation (qbar)

C_L_bg = L_bg./(qbar*S);


C_D_met = D_m./(qmet*Sm);


C_L_met = L_m./(qmet*Sm);

%disp(['C_D_bg (Imperial): ', num2str(C_D_bg)]);   DEBUG
%disp(['C_L_bg (Imperial): ', num2str(C_L_bg)]);
%disp(['C_D_met (Metric): ', num2str(C_D_met)]);
%disp(['C_L_met (Metric): ', num2str(C_L_met)]);

%% Verification of the Drag minimization and L/D optimization for the best glide


TASver = (30:0.5:300)'; % true airspeed, km/h
KTASver = convvel(TASver,'ft/s','kts')'; % true airspeed, kts
KCASver = correctairspeed(KTASver,a,P,'TAS','CAS')'; % corrected airspeed, kts
qbarver = dpressure([TASver zeros(size(TASver,1),2)], rhosl);
Dp = qbarver*S.*C_D0;
Dpm = convforce(Dp, 'lbf', 'N');
Di = (2*W^2)/(rhosl*S*pi*e*A).*(TASver.^-2);
Dim = convforce(Di, 'lbf', 'N');
D = Dp + Di;
Dm = convforce(D, 'lbf', 'N');

%% Verification section

L = Wm; %Basic assumption still the same

%Calculating the L/D max

[Maxx, Indd] = max(L./Dm);

MaxxLDTAS = KCASver(Indd);


% Graph for L/D vs KCAS

h1 = figure;
plot(KCASver, L./Dm);
title('L/D vs. KCAS');
xlabel('KCAS in knots'); ylabel('L/D');
hold on
plot(KCAS_bg, L_m/D_m,'Marker','o','MarkerFaceColor','black',... % Plotting the calculated values to verify how close they are to the graph maximum
    'MarkerEdgeColor','black','Color','white');
plot(MaxxLDTAS, Maxx,'Marker','o','MarkerFaceColor','red',... % Plotting the calculated value via iteration
    'MarkerEdgeColor','black','Color','white');
hold off
legend('L/D','L_{bg}/D_{bg}','L/D_{max}','Location','Best');

%Graph for induced, parasitic and total Drag vs KCAS

h2 = figure;
plot(KCASver,Dpm,KCASver,Dim,KCASver,Dm); 
title('Parasitic, induced, and total drag curves');
xlabel('KCAS in knots'); ylabel('Drag, Newtons'); 
hold on
plot(KCAS_bg, D_m,'Marker','o','MarkerFaceColor','black',... % Once again plotting the calculated values
    'MarkerEdgeColor','black','Color','white');
plot(KCASver(Indd), Dm(Indd),'Marker','o','MarkerFaceColor','red',... % Once again plotting the calculated values
    'MarkerEdgeColor','black','Color','white');
hold off
legend('Parasitic, D_p','Induced, D_i','Total, D','D_{bg}','D_{min}','Location','Best');



res = [fpm, minfpm, gamma_bg, KTAS_bg, KTASminsinkrate, KCAS_bg, KCASver(Indd),  KTASver(Indd), GS_reskthdg, L_m, D_m, qmet, C_L_met, C_D_met, ];



% Script by: Kithmin Wickremasinghe, 2022
% kithminr@ece.ubc.ca
  
% This script is used to model the principles of a non-intrusive calorimetric 
% flow rate sensor. 

% Acknowledgements - Samantha M. Grist (Calc_Dimensionless_ANT.m)

% Reference - Ahmed Tashfin Iftekhar, Jenny Che-Ting Ho, Axel Mellinger, and 
% Tolga Kaya , "3D modeling and characterization of a calorimetric flow rate 
% sensor for sweat rate sensing applications", Journal of Applied Physics 121, 
% 094505 (2017)s​

clc;
close all;
clear all;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Constants
rho = 997;      % Density of water (kg/m^3)
Cp = 4184;      % Specific heat capacity of water (J/kg*K)
lf = 0.598;     % Thermal conductivity of water (W/m*K)
kSiO2 = 1.1;      % Thermal conductivity of SiO2 (W/m*K)
aFl = lf/(rho*Cp);  % Thermal diffusivity of water (m^2/s)
v_kin = 1.0023e-6;  % kinematic viscosity of water (m^2/s)
T_ambient = 25; % Ambient temperature (C)
T_initial = 20; % Initial temperature of fluid (C)

% ANT Process parameters
PECVD_Oxide = (2.2+0.3)*1e-6;
TiW_Heater_h = 200e-9;
TiW_Heater_Rs = 3.04; % (Ohm/square) - R = Rs*L/W
TiW_Heater_L = 580e-6; % (m)
TiW_Heater_W = 3e-6; % (m)
TiW_Heater_R = TiW_Heater_Rs*TiW_Heater_L/TiW_Heater_W; % (Ohm)
Voltage = 1; % (V)
P = Voltage^2/TiW_Heater_R;     % Constant heater power - V^2/R (W)
fprintf('The constant heater power is %f mW.\n',P*1e3);

% Sensor parameters
bh = 80e-6;     % Width of the heater (m)
dm = 100e-9;    % Thickness of PECVD SiO2 cladding layer (m)
lh = 60e-6;     % Length of heater (m)
lu = 65e-6;     % Distance from heater to upstream sensor (m)
ld = 65e-6;     % Distance from heater to downstream sensor (m)
Ws = 22e-6;     % Sensor width, perpendicular to flow (m)
L = 220e-9;     % Sensor height, along flow direction (m)

% Channel parameters
Wc = 250e-6;    % channel width (m)
h = 500e-6;     % channel height (m)
Dh = 4*Wc*h/(2*(Wc+h)); % channel hydraulic diameter (m)
dx = 1e-7;
lX = 1000e-6; 

k = 0.5+kSiO2*dm/(lf*h); % Dimensionless factor (we can set it to 1/2)
fprintf('The dimensionless factor is %f.\n',k);

c = 60/1e-9;    % Conversion factor from (m^3/s) to (uL/min)
cx = 1e-9/60;   % Conversion factor from (uL/min) to (m^3/s) 

% Simulation parameters
Q1 = 0;         % Fluid flow rate (uL/min)
Q2 = 20;        % Fluid flow rate (uL/min)
Q3 = 80;        % Fluid flow rate (uL/min)

% Conversion for simulation
v1 = Q1*cx/(Wc*h); % Average linear fluid velocity in channel (m/s)
Re = v1*Dh/v_kin; % Reynolds Number
disp(['v1 = ', num2str(v1*1e3), ' mm/s; Re = ', num2str(Re)]);
v2 = Q2*cx/(Wc*h); % Average linear fluid velocity in channel (m/s)
Re = v2*Dh/v_kin; % Reynolds Number
disp(['v2 = ', num2str(v2*1e3), ' mm/s; Re = ', num2str(Re)]);
v3 = Q3*cx/(Wc*h); % Average linear fluid velocity in channel (m/s)
Re = v3*Dh/v_kin; % Reynolds Number
disp(['v3 = ', num2str(v3*1e3), ' mm/s; Re = ', num2str(Re)]);

% Flow with reynolds number (Re)
% i)   Re < 2000: Laminar flow
% ii)  2000 < Re < 4000: Transition Flow
% iii) Re > 4000: Turbulent flow

%%

% The heat distribution along the heater length was assumed to be uniform 
% and constant (not a good assumption), which in real case is dynamic in nature.

% We have 3 cases;
% i)   For when x< -lh/2
% ii)  For when -lh/2 <= x <= lh/2
% iii) For when x > lh/2
x_u = -lX:dx:-lh/2;
x_h = -lh/2:dx:+lh/2;
x_d = +lh/2:dx:lX;

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/h+sqrt(4*k + (v1.^2*h^2)/(4*aFl^2))));
fprintf('The heater temperature for Q1 is %f.\n',T0+T_ambient);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v1 + sqrt(v1.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)
gamma_2 = (v1 - sqrt(v1.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2)));
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
figure;
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X*1e6,T+T_ambient,'LineWidth',2,'Color','k');
hold on;

%%%%%%%%%%%%%%

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/h+sqrt(4*k + (v2.^2*h^2)/(4*aFl^2))));
fprintf('The heater temperature for Q2 is %f.\n',T0+T_ambient);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v2 + sqrt(v2.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)
gamma_2 = (v2 - sqrt(v2.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2))); 
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X*1e6,T+T_ambient,'LineWidth',2,'Color',[0 0.4470 0.7410]);

%%%%%%%%%%%%%%

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/h+sqrt(4*k + (v3.^2*h^2)/(4*aFl^2))));
fprintf('The heater temperature for Q3 is %f.\n',T0+T_ambient);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v3 + sqrt(v3.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)
gamma_2 = (v3 - sqrt(v3.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2)));
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X*1e6,T+T_ambient,'LineWidth',2,'Color',[0.8500 0.3250 0.0980]);
xlabel('Displacement (\mum)','FontSize',12);
ylabel('T (degC)', 'FontSize', 15);
legend('Q = 0 \muL/min', 'Q = 20 \muL/min', 'Q = 80 \muL/min');
grid on;

%%
%Considering the range 
%Considering the range 
Q = 0.1:0.1:3000;
v = Q*cx/(Wc*h);

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/h+sqrt(4*k + (v.^2*h^2)/(4*aFl^2))));

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v + sqrt(v.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)
gamma_2 = (v - sqrt(v.^2 + (16*(aFl^2)*(k))/h^2))/(4*aFl*k); % (1/m)

% Finally, temperature difference between the two sensors can be calculated as
deltaT = -T0.*((exp(gamma_2.*(ld-lh/2))) - (exp(gamma_1.*(-lu+lh/2))));

figure;
semilogx(Q,T0+T_ambient,'r-','LineWidth', 2)
xlabel('Flow Rate (\muL/min)','FontSize',12);
ylabel('Heater T (degC)', 'FontSize', 15);
grid on;

figure;
semilogx(Q,deltaT,'r-','LineWidth', 2)
xlabel('Flow Rate (\muL/min)','FontSize',12);
ylabel('\Delta T (degC)', 'FontSize', 15);
grid on;
% Script by: Kithmin Wickremasinghe, 2022
% kithminr@ece.ubc.ca
  
% This script is used to model the principles of a non-intrusive calorimetric 
% flow rate sensor.

% Reference - Ahmed Tashfin Iftekhar, Jenny Che-Ting Ho, Axel Mellinger, and 
% Tolga Kaya , "3D modeling and characterization of a calorimetric flow rate 
% sensor for sweat rate sensing applications", Journal of Applied Physics 121, 
% 094505 (2017)s​

clc;
close all;
clear all;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Constants
rho = 1000;     % Density of fluid (kg/m^3)
Cp = 4182;      % Specific heat capacity of fluid (J/kg*K)
lf = 0.591;     % Thermal conductivity of fluid (W/m*K)
aFl = 0.143e-6; % Diffusivity of the fluid (m2/s)
v_kin = 1.0023e-6;  % kinematic viscosity of water (m^2/s)
k = 0.5;        % Dimensionless factor (we can set it to 1/2)
P = 60e-3;      % Constant heater power - V^2/R (W)
T_ambient = 25; % Ambient temperature (C)
T_initial = 20; % Initial temperature of fluid (C)

% Sensor parameters
bh = 1.6e-3;   % Width of the heater (m)
dm = 1.05e-3;  % Thickness of the tube/diaphragm (m)
dx = 0.0001;
lh = 0.001;    % Length of heater (m)
lu = 0.004;    % Distance from heater to upstream sensor (m)
ld = 0.004;    % Distance from heater to downstream sensor (m)
lX = 0.01;    

% Channel parameters
d = 0.003;       % Diameter of pipe (m)
A = pi*(d/2)^2; % Cross-sectional area of pipe (m^2)
c = 60/1e-9;    % Conversion factor from (m^3/s) to (uL/min)
cx = 1e-9/60;   % Conversion factor from (uL/min) to (m^3/s)

% Simulation parameters
Q1 = 0;         % Fluid flow rate (uL/min)
Q2 = 20;        % Fluid flow rate (uL/min)
Q3 = 80;        % Fluid flow rate (uL/min)

% Conversion for simulation
v1 = Q1*cx/A; % Average linear fluid velocity in channel (m/s)
Re = v1*d/v_kin; % Reynolds Number
disp(['v1 = ', num2str(v1*1e3), ' mm/s; Re = ', num2str(Re)]);
v2 = Q2*cx/A; % Average linear fluid velocity in channel (m/s)
Re = v2*d/v_kin; % Reynolds Number
disp(['v2 = ', num2str(v2*1e3), ' mm/s; Re = ', num2str(Re)]);
v3 = Q3*cx/A; % Average linear fluid velocity in channel (m/s)
Re = v3*d/v_kin; % Reynolds Number
disp(['v3 = ', num2str(v3*1e3), ' mm/s; Re = ', num2str(Re)]);

% Flow with reynolds number (Re)
% i)   Re < 2000: Laminar flow
% ii)  2000 < Re < 4000: Transition Flow
% iii) Re > 4000: Turbulent flow

%%

% The heat distribution along the heater length was assumed to be uniform 
% and constant (not a good assumption), which in real case is dynamic in nature.

% We have 3 cases;
% i)  For when x< -lh/2
% ii) For when -lh/2 <= x <= lh/2
% ii) For when x > lh/2
x_u = -lX:dx:-lh/2;
x_h = -lh/2:dx:+lh/2;
x_d = +lh/2:dx:lX;

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/dm+sqrt(4*k + (v1.^2*dm^2)/(4*aFl^2))));
fprintf('The heater temperature for Q1 is %f.\n',T0);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v1 + sqrt(v1.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)
gamma_2 = (v1 - sqrt(v1.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2)));
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
figure;
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X,T,'LineWidth',2,'Color','k');
hold on;

%%%%%%%%%%%%%%

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/dm+sqrt(4*k + (v2.^2*dm^2)/(4*aFl^2))));
fprintf('The heater temperature for Q2 is %f.\n',T0);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v2 + sqrt(v2.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)
gamma_2 = (v2 - sqrt(v2.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2))); 
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X,T,'LineWidth',2,'Color',[0 0.4470 0.7410]);

%%%%%%%%%%%%%%

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/dm+sqrt(4*k + (v3.^2*dm^2)/(4*aFl^2))));
fprintf('The heater temperature for Q3 is %f.\n',T0);

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v3 + sqrt(v3.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)
gamma_2 = (v3 - sqrt(v3.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)

% The temperature distribution for each of the above cases is given by
T_d = T0.*(exp(gamma_2*(x_d-lh/2)));
T_h = T0.*ones(1,length(x_h));
T_u = T0.*(exp(gamma_1*(x_u+lh/2)));

%Plot the temperature distribution for different flow rates
X = [x_u x_h x_d];
T = [T_u T_h T_d];
plot(X,T,'LineWidth',2,'Color',[0.8500 0.3250 0.0980]);
xlabel('Displacement (m)','FontSize',12);
ylabel('T (degC)', 'FontSize', 15);
legend('Q = 0 \muL/min', 'Q = 20 \muL/min', 'Q = 80 \muL/min');
grid on;

%%
%Considering the range 
Q = 0:0.5:3000;
v = Q*cx/A;

% The heater temperature T0 can be calculated for constant heat power P
T0 = P./(lf*bh*(lh/dm+sqrt(4*k + (v.^2*dm^2)/(4*aFl^2))));

% The eigenvalue of the second order diff. equation solution are given by
gamma_1 = (v + sqrt(v.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)
gamma_2 = (v - sqrt(v.^2 + (16*(aFl^2)*(k))/dm^2))/(4*aFl*k); % (1/m)

% Finally, temperature difference between the two sensors can be calculated as
deltaT = -T0.*((exp(gamma_2.*(ld-lh/2))) - (exp(gamma_1.*(-lu+lh/2))));

figure;
semilogx(Q,T0,'r-','LineWidth', 2)
xlabel('Flow Rate (\muL/min)','FontSize',12);
ylabel('Heater T (degC)', 'FontSize', 15);
grid on;

figure;
semilogx(Q,deltaT,'r-','LineWidth', 2)
xlabel('Flow Rate (\muL/min)','FontSize',12);
ylabel('\Delta T (degC)', 'FontSize', 15);
grid on;
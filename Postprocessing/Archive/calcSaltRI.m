% Data from https://www.intechopen.com/chapters/64768 and Betancur-Ochoa,
% et al. 2017 https://ieeexplore.ieee.org/abstract/document/8063863
C = [0, 0.2, 0.4, 0.6, 0.8, 1]; % [M]
n = [1.30864, 1.31104, 1.31339, 1.31569, 1.31794, 1.32014];

% convert to g/L
CW = C*58.44; % [mol/L]*[g/mol] = [g/L]
% set up wavelength and fit parameters from Li, et al. https://journals.sagepub.com/doi/full/10.1366/14-07769R
lam = 1550;
a0 = 0.385;
a1 = 1.32;
a2 = 1;
a3 = 0.0244;
a4 = 2.07E-5;
a5 = 1.75E-7;
lam1sq = 8.79E3;
lam2sq = 1.1E8;
lam3sq = 6.09E4;

% calculate the refractive index function
nfit = sqrt(a0 + (a1*lam^2/(lam^2-lam1sq)) + (a2*lam^2/(lam^2-lam2sq)) + ...
    (a3*lam^2/(lam^2-lam3sq))) + a4.*CW - a5*CW.^2;

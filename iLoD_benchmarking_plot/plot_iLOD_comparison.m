

expS=[298	575	579.5	129.84	586	270	490	580	429.7	91	200	160	340	38	142	133	59	113	26	76	106];
WL = [1550	1550	1550	1495	1545.5	1535	1550	1550	1550	1310	1515	1554	1530	1550	1543	1550	1517	1310	1547	1268	1310];
expSnormal = expS./WL;
expQ= [330.66	1540	2585.96	3008.34	4172.47	4472.83	6927.8	7800	9767.08	9847.29	9968.83	10996.74	14821.74	14882.47	15823.86	23817.43	26925.87	32899.19	32899.19	44404.78	75453.25];
expLegend={'Slot ring-TE'	'SOE SWG'	'Multi-box ring'	'PHC-TE'	'SWG PHC'	'Thin ring-TM'	'SWG ring-TE'	'Multi-box Bragg'	'SWG ring-TM'	'Ring-TE-1310'	'Ring-TM'	'PHC ring'	'Slot Bragg'	'Ring-TE'	'Disk-TM'	'Thin ring-TE'	'Bragg-TE'	'Ring-TM-1310'	'Disk-TE'	'Segmented SWG TE-1310'	'Bragg-1310'};    

expQ_iLOD = linspace(1e2, 1e5, 1000);
iLOD = [1e-2 1e-3 1e-4];


figure(2)
clf
PLOT_MARKER = ["s","x","s",	">","o"	,"v","d","+","^","s","p","h","<","<","o","v","h","^","o","r*","<"];PLOT_MARKER=[PLOT_MARKER ,PLOT_MARKER];
PLOT_COLOR = ["k","c","y","m","b","y","g","b","k","b","b","r","b","k","y","c","k","k","b","r","y"]; PLOT_COLOR=[PLOT_COLOR, PLOT_COLOR];
EDGE_COLOR = ["k","c","k","m","b","k","g","b","k","b","b","r","b","k","k","c","k","k","b","r","k"]; PLOT_COLOR=[PLOT_COLOR, PLOT_COLOR];
loglog(expQ, expS, "*",'linewidth',2)
for i=1:length(expS)
loglog(expQ(i),expSnormal(i),PLOT_MARKER(i),'MarkerSize',14,'MarkerFaceColor',PLOT_COLOR(i), 'MarkerEdgeColor',EDGE_COLOR(i),'linewidth', 2); hold on;
end
for j=1:length(iLOD)
loglog(expQ_iLOD, 1310./(iLOD(j).*expQ_iLOD) , "k:",'linewidth',2)
end

for j=1:length(iLOD)
loglog(expQ_iLOD, 1550./(iLOD(j).*expQ_iLOD) , "k--",'linewidth',2)
end
grid on

h_legend=legend (expLegend,'Location','NorthEastOutside');
%ylim([10 1e3])
%xlim([])
legend()
xlabel('Quality Factor')
ylabel('Bulk Sensitivity (nm/RIU)')
set(gca , 'fontsize', 20)

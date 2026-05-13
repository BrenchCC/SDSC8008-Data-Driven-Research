load('data_for_figures_2a_and_3a.mat')
regret1 = output;
load('data_for_figures_2b_and_3b.mat')
regret2 = output;

subplot 121
plot(1:t_max,regret1,'-k','linewidth',2)
ylim([0 350])
% xlabel('x','position',[10700 10])
% ylabel('y','position',[0 360],'rotation',0)
% title('titlea')
xticks([0 2 4 6 8 10]*1000)
% xticklabels({'x1','x2','x3','x4','x5','x6'})
yticks([0 1 2 3]*100)
% yticklabels({'y1','y2','y3','y4'})
box off

subplot 122
plot(1:t_max,regret2,'-k','linewidth',2)
ylim([0 350])
% xlabel('x','position',[10700 10])
% ylabel('y','position',[0 360],'rotation',0)
% title('titleb')
xticks([0 2 4 6 8 10]*1000)
% xticklabels({'x1','x2','x3','x4','x5','x6'})
yticks([0 1 2 3]*100)
% yticklabels({'y1','y2','y3','y4'})
box off
load('data_for_figures_4_and_5b.mat')

subplot 121
plot(1:increment:t_max,ref_price_paths(1:increment:t_max,:),'linewidth',2)
hold on
plot(1:increment:t_max,p_star*ones(size(1:increment:t_max)),':k','linewidth',2)
ylim([0.5 1.5])
% xlabel('x','position',[10700 0.55])
% ylabel('ya','position',[0 1.52],'rotation',0)
% title('titlea')
xticks([0 2 4 6 8 10]*1000)
% xticklabels({'x1','x2','x3','x4','x5','x6'})
yticks([0.5 0.7 0.9 1.1 1.3 1.5])
% yticklabels({'y1','y2','y3','y4','y5','y6'})
box off
hold off

subplot 122
plot(4:increment:t_max,price_paths(1:increment:(t_max-3),:),'linewidth',2)
hold on
plot(1:increment:t_max,p_star*ones(size(1:increment:t_max)),':k','linewidth',2)
ylim([0.5 1.5])
% xlabel('x','position',[10700 0.55])
% ylabel('yb','position',[0 1.52],'rotation',0)
% title('titleb')
xticks([0 2 4 6 8 10]*1000)
% xticklabels({'x1','x2','x3','x4','x5','x6'})
yticks([0.5 0.7 0.9 1.1 1.3 1.5])
% yticklabels({'y1','y2','y3','y4','y5','y6'})
box off
hold off
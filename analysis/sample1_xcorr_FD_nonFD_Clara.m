% activity=Results(:,3:4:end);
for c=1:size(activity,2)
    activity(:,c)=activity(:,c)-activity(:,36);
end

figure;
for i=1:size(activity,2)
    plot(activity(:,i)-10*i);
    hold on;
end
figure;
stackedplot(activity);


%% list of cells
cells=1:size(activity,2);
pairwise_combinations=nchoosek(cells,2);

%% xcorr
for pair=1:size(pairwise_combinations,1)
    a=activity(:,pairwise_combinations(pair,1));
    b=activity(:,pairwise_combinations(pair,2));
    [c(:,pair),lags]=xcov(a,b,100,'coeff');
    pearson(pair)=c(101,pair);
end
figure;plot(pearson);
% figure;imagesc(cells,cells,pearson) %does not work yet, make a colourful
% plot

result=pairwise_combinations(find(pearson>0.5),:)
result(:,3)=pearson(find(pearson>0.5))
figure;plot(lags,c(:,(find(pearson>0.5))));

%% change analysis window
activity1=activity(1:detection_frame,:);
activity2=activity(detection_frame:end,:);
clear a b
for pair=1:size(pairwise_combinations,1)
    a=activity1(:,pairwise_combinations(pair,1));
    b=activity1(:,pairwise_combinations(pair,2));
    [c1(:,pair),lags]=xcov(a,b,100,'coeff');
    pearson1(pair)=c1(101,pair);
end

for pair=1:size(pairwise_combinations,1)
    a=activity2(:,pairwise_combinations(pair,1));
    b=activity2(:,pairwise_combinations(pair,2));
    [c2(:,pair),lags]=xcov(a,b,100,'coeff');
    pearson2(pair)=c2(101,pair);
end

figure;
scatter(pearson1,pearson2);hold on;
plot([min([pearson1 pearson2]) max([pearson1 pearson2])],[min([pearson1 pearson2]) max([pearson1 pearson2])]);
xlabel('bsl')
ylabel('after detection')
% figure;plot(pearson1);
delta=pearson2-pearson1;
pairwise_combinations(find(delta>0.5),:)





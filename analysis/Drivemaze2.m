%Drivemaze etho and ca imaging plotter
%2022Jan 
close all, clear all
%animals=table(['94331472'; '328340178184'; '335490249236']);%
animals='94331472';
'94331472 grin1 female';
f1=figure;
f2=figure;
f3=figure;
% f4=figure;
% f5=figure;
% for 
a=1%:3
clearvars -except a f1 f2 f3 f4 f5 animals binned b_trials b_dur binned_exp
% animal=cellstr(table2cell(animals(a,1)));
animal=animals;
% filename=['C:\Data\Drivemaze\Drivemaze_imaging_grin1' animal{1, 1} '_events.csv'];
filename=['C:\Data\Drivemaze\Drivemaze_imaging_grin1\' animal '_events.csv'];
%% Import csv
opts = delimitedTextImportOptions("NumVariables", 4);
opts.DataLines = [1, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["Date_Time", "amount_consumed", "latency_to_consumption", "Type"];
opts.VariableTypes = ["string", "double", "double", "categorical"];
opts = setvaropts(opts, 1, "WhitespaceRule", "preserve");
opts = setvaropts(opts, [1, 4], "EmptyFieldRule", "auto");
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
events = readtable(filename, opts);
clear opts

x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(isnat(x)==1),:)=[];
x(find(isnat(x)==1))=[];
event_type=events.(4);
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
%% chop
chop_from=datetime('2022-Feb-06 20:10:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
chop_to=datetime('2022-Feb-06 20:55:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');

x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x<chop_from),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x>chop_to),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(isnat(x)==1),:)=[];
x(find(isnat(x)==1))=[];
event_type=events.(4);
%% cleanup

% find imaging starts
u1=find(event_type=='frame');
f_num=events.(3);
imaging_starts=u1(find(f_num(u1)==1));
imaging_ends=[];%accumulator
for i=2:size(imaging_starts,1)
u2=u1(find(u1<imaging_starts(i)));
imaging_ends=[imaging_ends; u2(end)];
end
imaging_ends=[imaging_ends; u1(end)];

%% plot
x=datetime(events.(1),'Format','yyyy-MM-dd HH:mm:ss.SSS');
y=NaN(size(x));
frameplot=NaN(size(x));
frameplot(find(event_type=='frame'))=f_num(find(event_type=='frame'));
%enter
y(find(event_type=='leave_nest'))=2;
y(find(event_type=='block_start'))=3.5; %change this to 2 before 28.1.22
y(find(event_type=='enter_feed'))=4; %food entry
enter(3).e=x(find(event_type=='enter_feed'));
y(find(event_type=='enter_run'))=3; %wheel entry
enter(2).e=x(find(event_type=='enter_run'));
y(find(event_type=='enter_social'))=4.5; %
enter(4).e=x(find(event_type=='enter_social'));
y(find(event_type=='enter_drink'))=2.5; %
enter(5).e=x(find(event_type=='enter_drink'));
y(find(event_type=='enter_explore'))=5; 
enter(1).e=x(find(event_type=='enter_explore'));
enter_all=x(find(event_type=='enter_explore' | event_type=='enter_run' | event_type=='enter_feed' | event_type=='enter_social' | event_type=='enter_drink'));

%consume
y(find(event_type=='retrieve_pellet'))=4;%pellet retrieval
y(find(event_type=='drink'))=2.5; %
y(find(event_type=='run'))=3; %wheel entry
pel=x(find(event_type=='retrieve_pellet'));
drink=x(find(event_type=='drink'));
run=x(find(event_type=='run'));
%exit
y(find(event_type=='block_end'))=2;
y(find(event_type=='block_available'))=2;
y(find(event_type=='exit_feed'))=3.5;
exit(3).e=x(find(event_type=='exit_feed'));
y(find(event_type=='exit_drink'))=3.5;
exit(5).e=x(find(event_type=='exit_drink'));
y(find(event_type=='exit_run'))=3.5;
exit(2).e=x(find(event_type=='exit_run'));
y(find(event_type=='exit_social'))=3.5;
exit(4).e=x(find(event_type=='exit_social'));
y(find(event_type=='exit_explore'))=3.5;
exit(1).e=x(find(event_type=='exit_explore'));
exit_all=x(find(event_type=='exit_explore' | event_type=='exit_run' | event_type=='exit_feed' | event_type=='exit_social' | event_type=='exit_drink'));

session_starts=find(event_type=='initialize');
%session_ends=find(event_type=='end session');
yy=fillmissing(y,'linear');

figure(f1);
subplot(1,1,a),plot([x(1) x(end)],[3.5 3.5],'b');hold on%decisionpoint
subplot(1,1,a),plot([x(1) x(end)],[2 2],'b');%nest
subplot(1,1,a),plot(x,yy,'k');hold on
subplot(1,1,a),plot(x,y,'ko');hold on
%subplot(1,1,a),plot(x,fed_pos,'b');
subplot(1,1,a),plot(x,frameplot/1000,'g');hold on

title(animal);
yticks([0.5 1.5 2 2.5 3 3.5 4 4.5 5]);
yticklabels({'frames','frames','nest','drink','run','decision point','food','social','explore'});
ylabel('area');
ylim([-40 5.5]);

for i=1:1:length(pel)
    subplot(1,1,a),plot([pel(i) pel(i)],[3.8 4.2],'y','LineWidth',3);
end
for i=1:1:length(drink)
    subplot(1,1,a),plot([drink(i) drink(i)],[2.4 2.8],'c','LineWidth',3);
end
for i=1:1:length(run)
    subplot(1,1,a),plot([run(i) run(i)],[2.8 3.2],'m','LineWidth',3);
end
%% imaging data
%select sessions with analysed raw data
imaging_datasets=table(['20_13_56';'20_22_41';'20_39_15']);%;'';'';''
imaging_sessions=1:3;%12:14; %list in order from first file
x_imaging_cum=[];%cumulators for averaging
raw_f_cum=[];
z_scored_bsub_cum=[];
for s=1:length(imaging_sessions)
stack=cellstr(table2cell(imaging_datasets(s,1)));
stack_path=['C:\Data\Drivemaze\Drivemaze_imaging_grin1\2022_02_06toanalyse\' stack{1, 1} '\My_V4_Miniscope\Results.csv'];
opts = delimitedTextImportOptions("NumVariables", 121);
opts.DataLines = [2, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["VarName1", "Area1", "Mean1", "Min1", "Max1", "Area2", "Mean2", "Min2", "Max2", "Area3", "Mean3", "Min3", "Max3", "Area4", "Mean4", "Min4", "Max4", "Area5", "Mean5", "Min5", "Max5", "Area6", "Mean6", "Min6", "Max6", "Area7", "Mean7", "Min7", "Max7", "Area8", "Mean8", "Min8", "Max8", "Area9", "Mean9", "Min9", "Max9", "Area10", "Mean10", "Min10", "Max10", "Area11", "Mean11", "Min11", "Max11", "Area12", "Mean12", "Min12", "Max12", "Area13", "Mean13", "Min13", "Max13", "Area14", "Mean14", "Min14", "Max14", "Area15", "Mean15", "Min15", "Max15", "Area16", "Mean16", "Min16", "Max16", "Area17", "Mean17", "Min17", "Max17", "Area18", "Mean18", "Min18", "Max18", "Area19", "Mean19", "Min19", "Max19", "Area20", "Mean20", "Min20", "Max20", "Area21", "Mean21", "Min21", "Max21", "Area22", "Mean22", "Min22", "Max22", "Area23", "Mean23", "Min23", "Max23", "Area24", "Mean24", "Min24", "Max24", "Area25", "Mean25", "Min25", "Max25", "Area26", "Mean26", "Min26", "Max26", "Area27", "Mean27", "Min27", "Max27", "Area28", "Mean28", "Min28", "Max28", "Area29", "Mean29", "Min29", "Max29", "Area30", "Mean30", "Min30", "Max30"];
opts.VariableTypes = ["double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double"];
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
raw_f = readtable(stack_path, opts);
raw_f = table2array(raw_f);
clear opts
raw_f=raw_f(:,3:4:end);

%refine only good cells
good_cells=[5 6 10 12 14 17 25 26];

%make an x-axis
%import miniscope timestamps
miniscope_timestamps_path=['C:\Data\Drivemaze\Drivemaze_imaging_grin1\2022_02_06toanalyse\' stack{1, 1} '\My_V4_Miniscope\timeStamps.csv'];
opts = delimitedTextImportOptions("NumVariables", 3);
opts.DataLines = [2, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["Var1", "TimeStampms", "Var3"];
opts.SelectedVariableNames = "TimeStampms";
opts.VariableTypes = ["string", "double", "string"];
opts = setvaropts(opts, [1, 3], "WhitespaceRule", "preserve");
opts = setvaropts(opts, [1, 3], "EmptyFieldRule", "auto");
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
tbl = readtable(miniscope_timestamps_path, opts);
miniscope_timestamps = tbl.TimeStampms;
clear opts tbl
%check timestamps match the start and end in events
beh_len=milliseconds(x(imaging_ends(imaging_sessions(s)))-x(imaging_starts(imaging_sessions(s))))
im_len=miniscope_timestamps(end)-miniscope_timestamps(1)
t_delta=im_len-beh_len

f_dur_adhoc=milliseconds(x(imaging_ends(imaging_sessions(s)))-x(imaging_starts(imaging_sessions(s))))/size(raw_f,1)
x_imaging=[x(imaging_starts(imaging_sessions(s)))];
for i=1:size(raw_f,1)-2
    x_imaging=[x_imaging ; x(imaging_starts(imaging_sessions(s)))+duration(0,0,0,floor(i*f_dur_adhoc))];
end
x_imaging=[x_imaging ; x(imaging_ends(imaging_sessions(s)))];
z_scored_raw=zscore(raw_f,1,1);
%bsub
f_bsub=raw_f;
for c=1:size(raw_f,2)
f_bsub(:,c)=raw_f(:,c)-mean(raw_f(:,28:30),2);
end
z_scored_bsub=zscore(f_bsub,1,1);
a=1;
figure(f1);
j=0;
for i=good_cells%1:size(raw_f,2)
    j=j+1;
    subplot(1,1,a),plot(x_imaging,smooth(z_scored_bsub(:,i)/7-j,1),'Color',[i/size(raw_f,2) 1-i/size(raw_f,2) i/size(raw_f,2)]);hold on;
end

% figure;
% figure;stackedplot(z_scored_bsub);

x_imaging_cum=[x_imaging_cum;x_imaging];
raw_f_cum=[raw_f_cum;raw_f];
z_scored_bsub_cum=[z_scored_bsub_cum;z_scored_bsub];
end
%% average plots
win=200;
m=1;
n=5;
plottitle(1:5)=["pel","drink","run","enter_all","exit_all"];
for p=1:5;
    clear snips snips_bslined
    if p==1
        target=pel;      
    elseif p==2
        target=drink;   
    elseif p==3
        target=run;
    elseif p==4
        target=enter_all;   
    elseif p==5
        target=exit_all;
    end
    trigs=target(find(target>x_imaging_cum(1) & target<x_imaging_cum(end)));
    for i=1:size(trigs,1)
        temp=find(x_imaging_cum>trigs(i));
        trig=temp(1);
        if x_imaging_cum(trig)>trigs(i)+duration(0,0,1)
            'warning! trig is more than 1s off'
            i
        end
        if trig>win+1 && trig<size(raw_f_cum,1)-(win+1)
            snips(:,:,i)=z_scored_bsub_cum(trig-win:trig+win,:);
            snips_bslined(:,:,i)=snips(:,:,i)-mean(snips(win-50:win,:,i),1);
        end
    end
% response_mean=nanmean(snips_bslined,3);
response_mean=nanmean(snips,3);
figure(f2);
subplot(m,n,p),imagesc([-win:win],[1:size(response_mean,2)],response_mean');
title([plottitle(p),' trials',num2str(size(snips,3))]);
end
%% entry and exit averages    
m=2;
n=5;
for p=1:5;
    clear snips snips_bslined
    target=enter(p).e;      
    trigs=target(find(target>x_imaging_cum(1) & target<x_imaging_cum(end)));
    if size(trigs,1)==0
        p=p+1;
    else
        for i=1:size(trigs,1)
            temp=find(x_imaging_cum>trigs(i));
            trig=temp(1);
            if x_imaging_cum(trig)>trigs(i)+duration(0,0,1)
                'warning! trig is more than 1s off'
                i
            end
            if trig>win+1
                snips(:,:,i)=z_scored_bsub_cum(trig-win:trig+win,:);
                snips_bslined(:,:,i)=snips(:,:,i)-mean(snips(win-50:win,:,i),1);
            end
        end
%         response_mean=nanmean(snips_bslined,3);
        response_mean=nanmean(snips,3);
        figure(f3);
        subplot(m,n,p),imagesc([-win:win],[1:size(response_mean,2)],response_mean');
        title(['enter',num2str(p),' trials',num2str(size(snips,3))]);
    end
end

for p=1:5;
    clear snips snips_bslined
    target=exit(p).e;      
    trigs=target(find(target>x_imaging_cum(1) & target<x_imaging_cum(end)));
    if size(trigs,1)==0
        p=p+1;
    else
        for i=1:size(trigs,1)
            temp=find(x_imaging_cum>trigs(i));
            trig=temp(1);
            if x_imaging_cum(trig)>trigs(i)+duration(0,0,1)
                'warning! trig is more than 1s off'
                i
            end
            if trig>win+1 && trig<size(raw_f_cum,1)-(win+1)
                snips(:,:,i)=z_scored_bsub_cum(trig-win:trig+win,:);
                snips_bslined(:,:,i)=snips(:,:,i)-mean(snips(win-50:win,:,i),1);
            end
        end
%         response_mean=nanmean(snips_bslined,3);
        response_mean=nanmean(snips,3);
        figure(f3);
        subplot(m,n,p+5),imagesc([-win:win],[1:size(response_mean,2)],response_mean');
        title(['exit',num2str(p),' trials',num2str(size(snips,3))]);
    end
end




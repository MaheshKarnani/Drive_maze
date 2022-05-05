close all, clear all
animals={'141821018271';'141821018303';'141821018137';'2006010389'};
'3 have pfc->lh dreadd 141821018271 is ctrl';
f1=figure;
f2=figure;
f3=figure;
f4=figure;
f5=figure;
for a=1:4
clearvars -except a f1 f2 f3 f4 f5 animals binned b_trials b_dur binned_exp
animal=animals{a, 1};
filename=['C:\Data\Tmaze\' animal '_events.csv'];
%% Import csv
opts = delimitedTextImportOptions("NumVariables", 3);
opts.DataLines = [2, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["Date_Time", "Rotation", "Pellet_Retrieval", "Type", "Wheel_Position", "FED_Position"];
opts.VariableTypes = ["string", "categorical", "categorical", "categorical", "categorical", "categorical"];
opts = setvaropts(opts, 1, "WhitespaceRule", "preserve");
opts = setvaropts(opts, [1, 2, 4, 5, 6], "EmptyFieldRule", "auto");
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
events = readtable(filename, opts); 
events(find(events.Type=={'end session'}),:)%read out list of events
opts.VariableTypes = ["string", "categorical", "double", "categorical", "categorical", "categorical"];
events = readtable(filename, opts);
clear opts
%% chop
chop_from=datetime('2022-Apr-27 10:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% chop_from=datetime('2021-Dec-15 11:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
chop_to=datetime('2022-May-04 19:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% chop_from=datetime('2021-Sep-20 12:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% chop_to=datetime('2021-Sep-24 22:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
bin=hours(1);

%generic exp
bsl_from=datetime('2022-May-02 11:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
dreadd_from=datetime('2022-May-03 11:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
wo_from=datetime('2022-May-04 11:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
effect_window=hours(7);

% % dreadd bsl exp 0.5mg/kg
% bsl_from=datetime('2022-Mar-10 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% dreadd_from=datetime('2022-Mar-11 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% wo_from=datetime('2022-Mar-12 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% effect_window=hours(6);

% % dreadd bsl exp high 5mg/kg
% bsl_from=datetime('2022-Mar-24 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% dreadd_from=datetime('2022-Mar-25 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% wo_from=datetime('2022-Mar-26 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% effect_window=hours(6);

% % dreadd switch exp
% bsl_from=datetime('2022-Mar-15 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% dreadd_from=datetime('2022-Mar-18 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% wo_from=datetime('2022-Mar-21 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% effect_window=hours(6);

% % dreadd no FED3 exp
% bsl_from=datetime('2022-Mar-13 15:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% dreadd_from=datetime('2022-Mar-16 15:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% wo_from=datetime('2022-Mar-17 15:00:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% effect_window=hours(6);

% %dreadd hungry refeeding exp
% bsl_from=datetime('2022-Mar-14 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% dreadd_from=datetime('2022-Mar-17 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% wo_from=datetime('2022-Mar-20 11:30:00.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
% effect_window=hours(6);


x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x<chop_from),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x>chop_to),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(isnat(x)==1),:)=[];
x(find(isnat(x)==1))=[];
event_type=events.(4);
%% cleanup
water_time_was=events.Pellet_Retrieval(find(event_type=='begin session',1))
wheel_time_was=events.Rotation(find(event_type=='begin session',1))
clean_rows=[find(event_type=='begin session');find(event_type=='end session');find(event_type=='room door opened');find(event_type=='room door closed');];
events.Pellet_Retrieval(clean_rows)=NaN;
events.Rotation(clean_rows)='NaN';

%% plot
x=datetime(events.(1),'Format','yyyy-MM-dd HH:mm:ss.SSS');
y=NaN(size(x));
y(find(event_type=='BB4'))=4; %food entry
y(find(event_type=='BB3'))=3; %wheel entry
% y(find(event_type=='Food_retrieval'))=4;%pellet retrieval
y(find(event_type=='BB2'))=3.5; %decision point logs
y(find(event_type=='Food_log_BB2'))=3.5;
y(find(event_type=='Run_log_BB2'))=3.5;
y(find(event_type=='exit_drink'))=3.5;
fed_pos=grp2idx(events.(6))-0.5;
pel=events.(3);
pel(find(event_type=='drink'))=NaN;
pel(find(event_type=='Run_log_BB2'))=NaN;
pel(find(event_type=='exit_drink'))=NaN;
lick_contact=events.(3);
lick_contact(find(event_type=='Food_retrieval'))=NaN;
wheel=str2mat(string(events.(2)));
wheel(find(event_type=='drink'),:)=NaN;
wheel(find(event_type=='exit_drink'),:)=NaN;
room_door_open=find(event_type=='room door opened');
room_door_close=find(event_type=='room door closed');
starts=find(event_type=='START');
ends=find(event_type=='END');

%refine ends
ends(find(ends<starts(1)))=[]; %clean ends before first start
for i=1:size(starts,1)-1
    next_start=starts(i+1);
    next_end=ends(find(ends>starts(i),1));
    if next_start<next_end
        refined_ends(i)=next_start-1;
    else
        refined_ends(i)=next_end;
    end
end
if ends(end)>starts(end)
    refined_ends(end+1)=ends(end);
else
    starts(end)=[];
end
clear ends
ends=refined_ends';

first_lick=find(event_type=='drink');
attempts=find(event_type=='ENTRY DENIED');
attempts_crowd=find(event_type=='ENTRY DENIED MULTIPLE ANIMALS');
session_starts=find(event_type=='begin session');
session_ends=find(event_type=='end session');
y([starts; ends])=2;
yy=fillmissing(y,'linear');

figure(f1);
m=size(animals,1);
n=1;
p=a;
subplot(m,n,p),plot(x,yy,'k');hold on
subplot(size(animals,1),1,a),plot(x,y,'ko');hold on
subplot(size(animals,1),1,a),plot(x,fed_pos,'b');
title(animal);
yticks([0.5 1.5 2 2.6 3 3.5 4]);
yticklabels({'goals switched','goals normal','nest','first_lick','run-wheel/water','decision point','food area'});
ylabel('area');

for i=1:length(starts)
    subplot(size(animals,1),1,a),plot([x(starts(i)) x(starts(i))],[1 5],'g');
end
for i=1:length(ends)
    subplot(size(animals,1),1,a),plot([x(ends(i)) x(ends(i))],[1 5],'r');
end
for i=1:1:length(first_lick)
    subplot(size(animals,1),1,a),plot([x(first_lick(i)) x(first_lick(i))],[2.4 2.8],'c');
end
for i=1:length(attempts)
    subplot(size(animals,1),1,a),plot([x(attempts(i)) x(attempts(i))],[1.5 4.5],'k--');
end
for i=1:length(attempts_crowd)
    subplot(size(animals,1),1,a),plot([x(attempts_crowd(i)) x(attempts_crowd(i))],[1.5 4.5],'k');
end
for i=1:length(session_starts)
    subplot(size(animals,1),1,a),plot([x(session_starts(i)) x(session_starts(i))],[0 6],'m','LineWidth',3);
end
for i=1:length(session_ends)
    subplot(size(animals,1),1,a),plot([x(session_ends(i)) x(session_ends(i))],[0 6],'m','LineWidth',6);
end
for i=1:length(room_door_open)
    subplot(size(animals,1),1,a),plot([x(room_door_open(i)) x(room_door_open(i))],[0 6],'b--','LineWidth',2);
end
for i=1:length(room_door_close)
    subplot(size(animals,1),1,a),plot([x(room_door_close(i)) x(room_door_close(i))],[0 6],'b','LineWidth',2);
end

revolutions=zeros(size(events,1),1);
for i=1:length(fed_pos)   
    if isnan(pel(i))==0
        subplot(size(animals,1),1,a),plot(x(i),4.0,'y*','MarkerSize',10,'LineWidth',3);
    end
    if str2double(wheel(i,:))>0.3
        subplot(size(animals,1),1,a),plot(x(i-1),3.0,'g*','MarkerSize',10,'LineWidth',3);
        revolutions(i)=str2double(wheel(i,:));
    end
end

if a==3
    h(1)=plot(x(end),1,'y*','MarkerSize',10,'LineWidth',3);
    h(2)=plot(x(end),1,'g*','MarkerSize',10,'LineWidth',3);
    plot(x(end),1,'w*','MarkerSize',10,'LineWidth',4);
    legend(h,'eat 14mg pellet','run >1 wheel rev','Location','South');
end
%% summary stats

%prep figure landmarks
        figure(f2);
        subplot(size(animals,1),1,a),plot(x,fed_pos,'b');hold on
        for i=1:length(starts)
            subplot(size(animals,1),1,a),plot([x(starts(i)) x(starts(i))],[1 50],'g');
        end
        for i=1:length(ends)
            subplot(size(animals,1),1,a),plot([x(ends(i)) x(ends(i))],[1 50],'r');
        end
        for i=1:length(attempts)
            subplot(size(animals,1),1,a),plot([x(attempts(i)) x(attempts(i))],[1.5 4.5],'k--');
        end
        for i=1:length(attempts_crowd)
            subplot(size(animals,1),1,a),plot([x(attempts_crowd(i)) x(attempts_crowd(i))],[1.5 4.5],'k');
        end
        for i=1:length(session_starts)
            subplot(size(animals,1),1,a),plot([x(session_starts(i)) x(session_starts(i))],[0 50],'m','LineWidth',3);
        end
        for i=1:length(session_ends)
            subplot(size(animals,1),1,a),plot([x(session_ends(i)) x(session_ends(i))],[0 50],'m','LineWidth',6);
        end
        for i=1:length(room_door_open)
            subplot(size(animals,1),1,a),plot([x(room_door_open(i)) x(room_door_open(i))],[0 50],'b--','LineWidth',2);
        end
        for i=1:length(room_door_close)
            subplot(size(animals,1),1,a),plot([x(room_door_close(i)) x(room_door_close(i))],[0 50],'b','LineWidth',2);
        end
    
%block duration and trial number
for i=1:size(starts,1)-1 %clean up
    if size(starts,1)>i
        if ends(i)>starts(i+1)
            starts(i)=[];
        end
    end
end
for i=1:size(ends,1)-1 %clean up
    if starts(i)>ends(i)
        ends(i)=[];
    end
end

for i=1:size(ends,1) %blocks
    b_dur(a).dur(i)=x(ends(i))-x(starts(i));
    events_block=events(starts(i):ends(i),:);
    event_type_block=events_block.(4);
    b_trials(a).w(i)=length(find(event_type_block=='BB3'));   
    b_trials(a).f(i)=length(find(event_type_block=='BB4'));    
    b_trials(a).total(i)=b_trials(a).w(i)+b_trials(a).f(i);
    
    %high res analyses
    b_trials_water=find(event_type_block=='BB3');
    b_trials_water_end=find(event_type_block=='Run_log_BB2');
    if length(b_trials_water) ~= length(b_trials_water_end)
        'problem inconsistent water trials in this block'
        'correcting by adding next read'
        b_trials_water_end=[b_trials_water_end; b_trials_water(end)+2];
    end
    b_trials_food=find(event_type_block=='BB4');
    b_trials_food_end=find(event_type_block=='Food_log_BB2');
    if length(b_trials_food) ~= length(b_trials_food_end)
        'problem inconsistent food trials in this block'
        'correcting by adding next read'
        b_trials_food_end=[b_trials_food_end;b_trials_food(end)+2];
    end
    b_trials_total=sort([b_trials_water;b_trials_food]);
    b_trials_total_end=sort([b_trials_water_end;b_trials_food_end]);
    if size(b_trials_total,1)>1
        j=0;%switch counter
        clear exploit
        ex_ind=1;
        exploit(ex_ind)=0; %exploit counter
        b_trial_dur=[];%trial duration accumulator
        b_choice_dur=[];%choice duration accumulator
        for e=2:size(b_trials_total,1)
            if find(b_trials_water==b_trials_total(e)) & find(b_trials_food==b_trials_total(e-1))
                j=j+1;
                ex_ind=ex_ind+1;
                exploit(ex_ind)=0;
            elseif find(b_trials_water==b_trials_total(e-1)) & find(b_trials_food==b_trials_total(e))
                j=j+1;
                ex_ind=ex_ind+1;
                exploit(ex_ind)=0;
            else %it was the same then
                exploit(ex_ind)=exploit(ex_ind)+1;
            end
            b_trial_dur=[b_trial_dur; milliseconds(x(b_trials_total_end(e))-x(b_trials_total(e)))];
            b_choice_dur=[b_choice_dur; milliseconds(x(b_trials_total(e))-x(b_trials_total_end(e-1)))];
        end
        b_trials(a).mean_choice_dur(i)=nanmean(b_choice_dur);
        b_trials(a).mean_trial_dur(i)=nanmean(b_trial_dur);
    else
        j=NaN;
        exploit=NaN;
        b_trials(a).mean_trial_dur(i)=NaN;
        b_trials(a).mean_choice_dur(i)=NaN;
    end
    b_trials(a).switch_index(i)=j/size(b_trials_total,1);
    b_trials(a).exploit_index_max(i)=max(exploit);
    b_trials(a).exploit_index_mean(i)=mean(exploit);
    b_trials(a).exploit_index_min(i)=min(exploit);
    b_trials(a).start_time(i)=x(starts(i));
    b_trials(a).revolutions(i)=sum(revolutions(starts(i):ends(i)));
    
end

figure(f2);
xx=x(ends);
subplot(size(animals,1),1,a),plot(xx,b_trials(a).total,'ko','MarkerFaceColor','k');hold on
plot(xx,b_trials(a).w,'co','MarkerFaceColor','c');
plot(xx,b_trials(a).f,'yo','MarkerFaceColor','y');

%weight
filename=['C:\Data\Tmaze\' animal '_weight.csv'];
opts = delimitedTextImportOptions("NumVariables", 5);
opts.DataLines = [2, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["Weight_Mean", "Weight_Median", "Weight_Mode", "Weight_Max_Mode", "Date_Time"];
opts.VariableTypes = ["double", "double", "double", "categorical", "string"];
opts = setvaropts(opts, 5, "WhitespaceRule", "preserve");
opts = setvaropts(opts, [4, 5], "EmptyFieldRule", "auto");
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
weight = readtable(filename, opts);
clear opts
xw=datetime(weight.(5),'Format','yyyy-MM-dd HH:mm:ss.SSS');
% chop
weight(find(xw<chop_from),:)=[];
xw=datetime(weight.(5),'Format','yyyy-MM-dd HH:mm:ss.SSS');
yw=weight.(1);
subplot(size(animals,1),1,a),plot(xw,yw,'ks-');
title(animal);
ylabel('sq=w,g circles=trials/block');
(set(gca, 'YGrid', 'on', 'XGrid', 'off'));


%% per h plots
%manual binning

decisions=find(event_type=='BB2' | event_type=='Food_log_BB2' | event_type=='Run_log_BB2');
food_trials=find(event_type=='BB4');
water_trials=find(event_type=='BB3');
pellets=find(pel>0);
j=1;
for i=1:length(wheel)   
    if str2num(wheel(i))>0
        wheel_use(j)=i;
        revolutions(j)=str2double(wheel(i,:));
        j=j+1;
    end
end

exploratory_trials_f=[];
exploratory_trials_w=[];
j=1;
for i=food_trials'   
    if events.Type(i+1)=={'Food_retrieval'}
    else
        exploratory_trials_f(j)=i;
        j=j+1;
    end
end
j=1;k=1;
for i=water_trials'   
    if events.Type(i+1)=={'drink'}
    elseif find(wheel_use==i)
        wheel_only_trials(k)=i;
        k=k+1;
    else
        exploratory_trials_w(j)=i;
        j=j+1;
    end
end

j=1;%index counter
k=1;%block counter, blocks with wheel use in bin
l=1;%block counter all blocks in bin
for t=chop_from:bin:chop_to
    binned(a).starts(j)=size(find(x(starts)>t & x(starts)<t+bin),1);
    binned(a).ends(j)=size(find(x(ends)>t & x(ends)<t+bin),1);
    binned(a).decisions(j)=size(find(x(decisions)>t & x(decisions)<t+bin),1);       
    binned(a).food_trials(j)=size(find(x(food_trials)>t & x(food_trials)<t+bin),1);
    binned(a).water_trials(j)=size(find(x(water_trials)>t & x(water_trials)<t+bin),1);    
    binned(a).first_lick(j)=size(find(x(first_lick)>t & x(first_lick)<t+bin),1);
    binned(a).pellets(j)=size(find(x(pellets)>t & x(pellets)<t+bin),1);
    binned(a).wheel_use_trials(j)=size(find(x(wheel_use)>t & x(wheel_use)<t+bin),1);
    if binned(a).wheel_use_trials(j)>0
        binned(a).revolutions(j)=sum(revolutions(k:k+binned(a).wheel_use_trials(j)-1));
        k=k+binned(a).wheel_use_trials(j);
    else
        binned(a).revolutions(j)=0;
    end
    binned(a).exploratory_trials_f(j)=size(find(x(exploratory_trials_f)>t & x(exploratory_trials_f)<t+bin),1);
    binned(a).exploratory_trials_w(j)=size(find(x(exploratory_trials_w)>t & x(exploratory_trials_w)<t+bin),1);
    binned(a).switch_index(j)=nanmean(b_trials(a).switch_index(l:l+binned(a).starts(j)-1));
    binned(a).trial_dur(j)=nanmean(b_trials(a).mean_trial_dur(l:l+binned(a).starts(j)-1));
    binned(a).block_dur(j)=nanmean(b_dur(a).dur(l:l+binned(a).starts(j)-1));
    binned(a).choice_dur(j)=nanmean(b_trials(a).mean_choice_dur(l:l+binned(a).starts(j)-1));
    %duty cycle;   
    bin_starts=x(starts(find(x(starts)>t & x(starts)<t+bin)));
    bin_ends=x(ends(find(x(ends)>t & x(ends)<t+bin)));
    if isempty(bin_ends) && isempty(bin_starts)
        binned(a).duty_cycle(j)=0;
    elseif isempty(bin_starts)
        bin_starts=[t];
    elseif isempty(bin_ends)
        bin_ends=[t+bin];
    elseif  bin_starts(1) > bin_ends(1) %started in maze
        bin_starts=[t; bin_starts];
    elseif bin_starts(end)>bin_ends(end) %stopped in maze
        bin_ends=[bin_ends; t+bin];
    else
        binned(a).duty_cycle(j)= sum(bin_ends-bin_starts)/bin;
    end
    
    l=l+binned(a).starts(j);
    j=j+1;
end

figure(f3);
subplot(size(animals,1),4,1),plot([chop_from:bin:chop_to],binned(a).starts,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('starts');
subplot(size(animals,1),4,2),plot([chop_from:bin:chop_to],binned(a).ends,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('ends');
subplot(size(animals,1),4,3),plot([chop_from:bin:chop_to],binned(a).decisions,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('decisions');
subplot(size(animals,1),4,4),plot([chop_from:bin:chop_to],binned(a).food_trials,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('food trials');
subplot(size(animals,1),4,5),plot([chop_from:bin:chop_to],binned(a).water_trials,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('water trials');
subplot(size(animals,1),4,6),plot([chop_from:bin:chop_to],binned(a).first_lick,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('first_lick');
subplot(size(animals,1),4,7),plot([chop_from:bin:chop_to],binned(a).pellets,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('pellets');
subplot(size(animals,1),4,8),plot([chop_from:bin:chop_to],binned(a).wheel_use_trials,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('wheel use trials');
subplot(size(animals,1),4,9),plot([chop_from:bin:chop_to],binned(a).revolutions,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('revolutions');
subplot(size(animals,1),4,10),plot([chop_from:bin:chop_to],binned(a).exploratory_trials_f,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('exploratory trials f');
subplot(size(animals,1),4,11),plot([chop_from:bin:chop_to],binned(a).exploratory_trials_w,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('exploratory trials w');
subplot(size(animals,1),4,12),plot([chop_from:bin:chop_to],binned(a).duty_cycle,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('duty cycle');

figure(f4);
subplot(size(animals,1),2,1),plot([chop_from:bin:chop_to],binned(a).switch_index,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('switch index');ylim([0 1]);
subplot(size(animals,1),2,2),plot([chop_from:bin:chop_to],binned(a).block_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('block duration');
subplot(size(animals,1),2,3),plot([chop_from:bin:chop_to],binned(a).trial_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('trial duration');ylabel('t,ms');
subplot(size(animals,1),2,4),plot([chop_from:bin:chop_to],binned(a).choice_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('choice duration');ylabel('t,ms');

% comparison of dreadd effect
figure(f5);
j=1;%index counter
k=1;%block counter, blocks with wheel use in bin
l=1;%block counter all blocks in bin - not used in this?
for t=[bsl_from, dreadd_from, wo_from]
%     if t==wo_from
%         effect_window=hours(14);
%     end
    binned_exp(a).starts(j)=size(find(x(starts)>t & x(starts)<t+effect_window),1);
    binned_exp(a).ends(j)=size(find(x(ends)>t & x(ends)<t+effect_window),1);
    binned_exp(a).decisions(j)=size(find(x(decisions)>t & x(decisions)<t+effect_window),1);       
    binned_exp(a).food_trials(j)=size(find(x(food_trials)>t & x(food_trials)<t+effect_window),1);
    binned_exp(a).water_trials(j)=size(find(x(water_trials)>t & x(water_trials)<t+effect_window),1);    
    binned_exp(a).first_lick(j)=size(find(x(first_lick)>t & x(first_lick)<t+effect_window),1);
    binned_exp(a).pellets(j)=size(find(x(pellets)>t & x(pellets)<t+effect_window),1);
    binned_exp(a).revolutions(j)=sum(b_trials(a).revolutions(find(b_trials(a).start_time>t,1):find(b_trials(a).start_time<t+effect_window,1,'last')));
    binned_exp(a).exploratory_trials_f(j)=size(find(x(exploratory_trials_f)>t & x(exploratory_trials_f)<t+effect_window),1);
    binned_exp(a).exploratory_trials_w(j)=size(find(x(exploratory_trials_w)>t & x(exploratory_trials_w)<t+effect_window),1);
    binned_exp(a).switch_index(j)=nanmean(b_trials(a).switch_index(find(b_trials(a).start_time>t,1):find(b_trials(a).start_time<t+effect_window,1,'last')));
    binned_exp(a).trial_dur(j)=nanmean(b_trials(a).mean_trial_dur(find(b_trials(a).start_time>t,1):find(b_trials(a).start_time<t+effect_window,1,'last')));
    binned_exp(a).block_dur(j)=nanmean(b_dur(a).dur(find(b_trials(a).start_time>t,1):find(b_trials(a).start_time<t+effect_window,1,'last')));
    binned_exp(a).choice_dur(j)=nanmean(b_trials(a).mean_choice_dur(find(b_trials(a).start_time>t,1):find(b_trials(a).start_time<t+effect_window,1,'last')));
    l=l+binned_exp(a).starts(j);
    j=j+1;
end

subplot(size(animals,1),4,1),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).starts,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('maze entries (blocks)');
subplot(size(animals,1),4,2),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).decisions,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('decisions');
subplot(size(animals,1),4,3),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).food_trials,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('food trials');
subplot(size(animals,1),4,4),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).water_trials,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('water trials');
subplot(size(animals,1),4,5),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).first_lick,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('first_lick');
subplot(size(animals,1),4,6),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).pellets,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('pellets');
subplot(size(animals,1),4,7),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).revolutions,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('revolutions');
subplot(size(animals,1),4,8),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).exploratory_trials_f+binned_exp(a).exploratory_trials_w,'Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a);
hold on;title('exploratory trials');
subplot(size(animals,1),4,9),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).switch_index,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('switch index');ylim([0 1]);xticks([bsl_from, dreadd_from, wo_from]);xticklabels({'bsl','dreaddLH','wash out'});
subplot(size(animals,1),4,10),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).block_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('block duration');xticks([bsl_from, dreadd_from, wo_from]);xticklabels({'bsl','dreaddLH','wash out'});
subplot(size(animals,1),4,11),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).trial_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('trial duration');ylabel('t,ms');xticks([bsl_from, dreadd_from, wo_from]);xticklabels({'bsl','dreaddLH','wash out'});
subplot(size(animals,1),4,12),plot([bsl_from, dreadd_from, wo_from],binned_exp(a).choice_dur,'s-','Color',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'LineWidth',size(animals,1)/a,'MarkerFaceColor',[a/size(animals,1) 1-a/size(animals,1) a/size(animals,1)],'MarkerSize',8);
hold on;title('choice duration');ylabel('t,ms');xticks([bsl_from, dreadd_from, wo_from]);xticklabels({'bsl','dreaddLH','wash out'});

end
figure(f1);
linkaxes
ylim([0 4.5]);

figure(f2);
linkaxes
ylim([0 max([b_trials(:).total])]);

figure(f3);
legend(animals,'Location','northoutside');
subplot(size(animals,1),4,12),plot([chop_from:bin:chop_to],(binned(1).duty_cycle+binned(2).duty_cycle+binned(3).duty_cycle+binned(4).duty_cycle),'k','LineWidth',4);%
ylim([0 1]);

figure(f4);
legend(animals,'Location','North');
figure(f5);
legend(animals,'Location','North');
axis tight

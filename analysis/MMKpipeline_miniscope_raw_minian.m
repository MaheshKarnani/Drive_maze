clear all; close all;
%% import data
imaging_datasets=table(['14_45_51';'14_48_41';'14_56_33']);%;'';'';''
f3=figure;
for s=1%:3
%name paths and import
stack=cellstr(table2cell(imaging_datasets(s,1)));
stack_path=['C:\Data\Drivemaze\Drivemaze_imaging_grin2\2022_05_06\' stack{1, 1} '\My_V4_Miniscope\Results.csv'];
list_path=['C:\Data\Drivemaze\Drivemaze_imaging_grin2\2022_05_06\' stack{1, 1} '\My_V4_Miniscope\timeStamps.csv'];
events_path=['C:\Data\Drivemaze\Drivemaze_imaging_grin2\328340226232_events_from2022-04-26to2022-05-07.csv'];
frame_list=import_framelist(list_path);
events=import_events(events_path);
raw_f=import_raw(stack_path);

%% refine events
%chop
if s==1
    chop_from=datetime('2022-May-06 14:45:45.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
    chop_to=datetime('2022-May-06 14:48:30.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
    elseif s==2
    chop_from=datetime('2022-May-06 14:48:39.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
    chop_to=datetime('2022-May-06 14:56:30.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
    elseif s==3
    chop_from=datetime('2022-May-06 14:56:31.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
    chop_to=datetime('2022-May-06 15:00:04.000','InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
end

events=sortrows(events,1); %spliced in some events from accidental save in different subject
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(isnat(x)==1),:)=[];
x(find(isnat(x)==1))=[];
event_type=events.(4);
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x<chop_from),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(x>chop_to),:)=[];
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
events(find(isnat(x)==1),:)=[];
x(find(isnat(x)==1))=[];
event_type=events.(4);

%% find dropped frames
frame=frame_list.(1);
time_stamp=frame_list.(2);
figure;subplot(2,1,1),plot(frame(2:end),diff(time_stamp),'ko-');
title('before');

fd=median(diff(time_stamp));
fake_time_stamps=time_stamp;
missed_frames=[];

miss=find(diff(fake_time_stamps)>1.5*fd,1);
while isnan(miss)==0
    f=miss+1;
    missed_frames=[missed_frames f];
    new_stamp=fake_time_stamps(f-1)+fd;
    fake_time_stamps=[fake_time_stamps(1:f-1); new_stamp; fake_time_stamps(f:end)];
    miss=find(diff(fake_time_stamps)>1.5*fd,1);
end
subplot(2,1,2),plot(diff(fake_time_stamps),'ko-');
title('after');
missed_frames

%% correct event list for dropped frames
event_frames=events.(5);
new_event_frames=events.(5);
for i=1:length(missed_frames)
    to_shift=find(event_frames>missed_frames(i));
    new_event_frames(to_shift)=new_event_frames(to_shift)-1;
end
events.(5)=new_event_frames;

%% imaging data
figure;stackedplot(raw_f);
size(raw_f)
win=30;
m=3;
n=2;
for p=1:2;
    clear snips snips_bslined  
    if p==1
        t='enter_drink';
    elseif p==2
        t='enter_feed';
    end
    trigs=new_event_frames(find(event_type==t));
    if size(trigs,1)==0
        p=p+1;
    else
        for i=1:size(trigs,1)
            trig=trigs(i);
            if trig>win+1
                snips(:,:,i)=raw_f(trig-win:trig+win,:);
                snips_bslined(:,:,i)=snips(:,:,i)-mean(snips(win-10:win,:,i),1);
            end
        end
%         response_mean=nanmean(snips_bslined,3);
        response_mean=nanmean(snips,3);
        figure(f3);hold on;
        subplot(m,n,p+s*2-2),imagesc([-win:win],[1:size(response_mean,2)],response_mean');
        title([t,' trials:',num2str(size(snips,3))]);
        %         data(s).data=snips; %something like this to save and append over
%         sessions
    end
end


end

function raw_f=import_raw(filename)
    %% Import csv
    opts = delimitedTextImportOptions("NumVariables", 4);
    opts.DataLines = [2, Inf];
    opts.Delimiter = ",";
    opts.VariableNames = ["VarName1", "unit_id", "frame", "YrA"];
    opts.VariableTypes = ["double", "double", "double", "double"];
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";
    Results = readtable(filename, opts);
    Results = table2array(Results);
    clear opts
    cells=unique(Results(:,2));
    for i=1:length(cells)
        raw_f(:,i)=Results(find(Results(:,2)==cells(i)),4);
    end
end
function events=import_events(filename)
    %% Import csv
    opts = delimitedTextImportOptions("NumVariables", 6);
    opts.DataLines = [2, Inf];
    opts.Delimiter = ",";
    opts.VariableNames = ["Date_Time", "amount_consumed", "latency_to_consumption", "Type", "frame", "hardware_time"];
    opts.VariableTypes = ["string", "double", "double", "categorical", "double", "double"];
    opts = setvaropts(opts, 1, "WhitespaceRule", "preserve");
    opts = setvaropts(opts, [1, 4], "EmptyFieldRule", "auto");
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";
    events = readtable(filename, opts);
    clear opts
end
function frame_list=import_framelist(list_path)
    %% Import csv
    opts = delimitedTextImportOptions("NumVariables", 3);
    opts.DataLines = [2, Inf];
    opts.Delimiter = ",";
    opts.VariableNames = ["FrameNumber", "TimeStampms", "BufferIndex"];
    opts.VariableTypes = ["double", "double", "double"];
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";
    frame_list = readtable(list_path, opts);
    clear opts
end

close all
clear all

filename=['C:\Data\MMK\32_events.csv'];
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
x=datetime(events.(1),'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
y=x-x;
y(find(events.(4)=='frame'))=10;
figure;plot(x,y,'ko-');


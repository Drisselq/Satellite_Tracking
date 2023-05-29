%%%%%%%%%%%%%%%%%%%%%%
%    EL Qaisy Driss
%    19/05/2023
%%%%%%%%%%%%%%%%%%%%%%

close all; clear all; clc;
% Example code for satellite prediciton 
% Required Libraries: GPS_CoordinateXforms, SPG4, IGRF, utilities 
addpath 'C:\Users\32494\OneDrive\Bureau\cubesat\Needed'

% First load the TLE : (Here we use a random TLE for the example)
longstr1='1 25544U 96067A   08264.51782528 -.00002182  00000-0 -11606-4 0 2927';
longstr2= '2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
fprintf('USING 2-Line Elements: \n')
fprintf('%s \n',longstr1)
fprintf('%s \n',longstr2)
% Printing to see check

% Defining some constants
mpd = 24*60 ; % Minute per Day
deg2rad = pi/180; % Degrees to radians
rad2de = 180/pi; % Radians to Degrees
dt=10/60;  %10 sec (Discretization)
npts=5000; % nbr of point for the iteration
tsince_offset=10000;

% ULB Station parameters
latitude = 50.850340; % Latitude in degrees
longitude = 4.351710; % Longitude in degrees
altitude = 58; % Altitude in m 
origin_llh = [latitude*deg2rad;longitude*deg2rad;altitude];
rx_name = 'Bruxelles';

% SGP4 Initialization
satrec = twoline2rvMOD(longstr1,longstr2); %longstr1, longstr2 are TLE lines in string
fprintf('\n')
fprintf('Satellite ID %5i \n',satrec.satnum)
fprintf('Station %s: Lon=%6.4f Lat %6.4f Alt=%6.2f m \n',...
            rx_name,origin_llh(2)/deg2rad,origin_llh(1)/deg2rad,origin_llh(3))
        
% Starting the SGP4 propagation
tsince=tsince_offset+[0:npts-1]*dt; % Defining the propagation period

if (satrec.epochyr < 57)          % Extracting the year from the TLE ; TLE can't handle more than 2057
    year= satrec.epochyr + 2000; 
else
    year= satrec.epochyr + 1900;
end
days = satrec.epochdays;  % Extracting the days from the TLE
[mon,day,hr,min,sec] = days2mdh(years,days); % Converting the days into Month/Day/Min/Sec 
UTC_sec = hr*3600+ min*60+ sec; % Getting the nbr of sec of day instead of Hour + Min + Sec
fprintf("The epoch is (Year, Month, Day, Day's second) : \n")
fprintf('%5i %2s %2i %2s %4i %2s %5.2f \n\n',year, '/', mon, '/', day, '/', UTC_sec);

% Initializing the position and velocity vector in ECF coordinates 
% The dimension are 3 x 5000 : 3 dimensions for x,y,z and 5k points precision
position_sat_ecf=zeros(3,npts); 
velocity_sat_ecf=zeros(3,npts);   

% Propagating the SGP4 model for the wanted duration  
for n=1:npts
   [satrec, position_sat_ecf(:,n), velocity_sat_ecf(:,n)]=spg4_ecf(satrec,tsince(n));
end
% Scale state vectors to m units
position_sat_ecf=position_sat_ecf*1000;  %m
velocity_sat_ecf=velocity_sat_ecf*1000;  %m/s

% Converting the unity from ecf to tcs
sat_llh=ecf2llhT(position_sat_ecf);                                 %ECF to geodetic (llh)  
sat_tcs=llh2tcsT(sat_llh,origin_llh);                               %llh to tcs at origin_llh
sat_elev=atan2(sat_tcs(3,:),sqrt(sat_tcs(1,:).^2+sat_tcs(2,:).^2)); % Getting the satellite elevation 
sat_elev = sat_elev * rad2de ; 

%Identify visible segments: 
% Considering that the satellite is visible if elevation > 5 degree
not_visible = find( sat_elev  < 5); 
visible = setdiff([1:npts],not_visible);
inter_sat_elev = sat_elev;
inter_sat_elev(not_visible)=NaN;
%Extract start and end times for visible segement and generating a visibility list 
t_start = tsince(not_visible(diff(not_visible)>1));
t_end  = tsince(visible(diff(visible)>1));
if length(t_end)<length(t_start)
   t_end  =[t_end,tsince(visible(end))];
elseif length(t_start)<length(t_end)
   t_start=[tsince(not_visible(1)),t_end];
end

t_mid  =(t_start(1:length(t_end)) +t_end(1:length(t_end))/2);

y_end = 5*ones(1,length(t_end));
y_start = 5*ones(1,length(t_start));

figure
plot(tsince(:)/mpd,sat_elev(:),'r')
hold on
plot(t_start/mpd,y_start ,'b^')
hold on
plot(t_end/mpd,y_end ,'b^')


for npass=1:length(t_mid)
    hold on
    npass_str=num2str(npass);
    text(t_end(npass)/mpd,10,npass_str)
    [Emon,Eday,Ehr,Emin,Esec] = days2mdh(year,satrec.epochdays+t_start(npass)/mpd);
    fprintf('PASS#%3i START: %5i %2i %4i %5.2f ',npass,Emon,Eday,Ehr,Emin);
    [Emon,Eday,Ehr,Emin,Esec] = days2mdh(year,satrec.epochdays+t_end(npass)/mpd);
    fprintf('END: %5i %2i %4i %5.2f \n',Emon,Eday,Ehr,Emin);
end
grid on
xlabel('UT--days')
ylabel('elevation--deg')
title(['Satellite ID: ',num2str(satrec.satnum),'--Station: ',rx_name])


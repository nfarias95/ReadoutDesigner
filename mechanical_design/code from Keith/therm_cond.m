function lambda = therm_cond(T,RRR)
% function lambda = therm_cond(T,RRR)
% thermal conductivity from NIST data; v1.2 extrapolate T^1 below 4K
%
% calculate thermal conductivity at a temperature from NIST data
%
% v1.0 20140917 KLT, copper only
% v1.1 20150116 comment out printf, plots
%      20151106 started to allow T to be array, but quit and reverted
% v1.2 20200810 extrap to low T from 4K; looks poor w/just equation; 
%                  use T^1, looks good enough, maybe underest a hair
%               create versionthing
% v1.3 20230620 extrap lambda outside of the NIST RRR range with linear 
%                fit (poly order 1), not just keeping the order 4 polyfit
%                used inside -- lambda(R) for fixed T is very nearly 
%                linear (in fact affine, lambda/R ~ constant)

    versionthing = 1.3;
 	

% RRR = 50 100 150 300 500
% UNITS	W/(m-K)	W/(m-K)	W/(m-K)	W/(m-K)	W/(m-K)
% a	1.8743	2.2154	2.3797	1.357	2.8075
% b	-0.41538	-0.47461	-0.4918	0.3981	-0.54074
% c	-0.6018	-0.88068	-0.98615	2.669	-1.2777
% d	0.13294	0.13871	0.13942	-0.1346	0.15362
% e	0.26426	0.29505	0.30475	-0.6683	0.36444
% f	-0.0219	-0.02043	-0.019713	0.01342	-0.02105
% g	-0.051276	-0.04831	-0.046897	0.05773	-0.051727
% h	0.0014871	0.001281	0.0011969	0.0002147	0.0012226
% i	0.003723	0.003207	0.0029988	0	0.0030964
% low range
% 4K	4K	4K	4K	4K
% high range
% 300K	300K	300K	300K	300K


    copper_RRR = [50, 100, 150, 300, 500];
    data_copper = [1.8743  2.2154  2.3797  1.357  2.8075                % a
                  -0.41538  -0.47461  -0.4918  0.3981  -0.54074         % b
                  -0.6018  -0.88068  -0.98615  2.669  -1.2777           % c
                  0.13294  0.13871  0.13942  -0.1346  0.15362           % d
                  0.26426  0.29505  0.30475  -0.6683  0.36444           % e
                  -0.0219  -0.02043  -0.019713  0.01342  -0.02105       % f
                  -0.051276  -0.04831  -0.046897  0.05773  -0.051727    % g
                  0.0014871  0.001281  0.0011969  0.0002147  0.0012226  % h
                  0.003723  0.003207  0.0029988  0  0.0030964];         % i
    % equation: k(T) = 10^(X/Y)
    %           X = a + c*T^0.5 + e*T + g*T^1.5 + i*T^2
    %           Y = 1 + b*T^0.5 + d*T + f*T^1.5 + h*T^2

    % note the data for a particular RRR value is in column, data_copper[:,i]

    % calculate lambda for each RRR value, then interpolate
    lambdas = zeros(length(copper_RRR),1);
    %lambdas = zeros(length(copper_RRR),numel(T));
    Ttrueval = -999;
    if T < 4
        Ttrueval = T;
        T = 4;     % now lambda calculated will just be lambda(4K)
                   % and Ttrueval will retain the input temperature
    end
    for ii=1:length(copper_RRR)
        xxx = [1.0, T^(0.5), T, T^(1.5), T^2]*data_copper(1:2:9,ii);
        yyy = [1.0, T^(0.5), T, T^(1.5), T^2]*[1.0; data_copper(2:2:9,ii)];
        %xxx = (zeros(numel(T),1) + 1.0)*data_copper(1,ii);
        %xxx = xxx + (T(:).^(0.5))*data_copper(3,ii);
        %xxx = xxx + T(:)*data_copper(5,ii);
        %xxx = xxx + (T(:).^1.5)*data_copper(7,ii);
        %xxx = xxx + (T(:).^8)*data_copper(9,ii);
        %yyy = (zeros(numel(T),1) + 1.0);
        %yyy = yyy + (T(:).^0.5)*data_copper(2,ii);
        %yyy = yyy + (T(:))*data_copper(4,ii);
        %yyy = yyy + (T(:).^1.5)*data_copper(6,ii);
        %yyy = yyy + (T(:).^2)*data_copper(8,ii);
        %lambdas(ii,:) = 10.0^(xxx./yyy);
        lambdas(ii,:) = 10.0^(xxx/yyy);
        %fprintf('RRR = %3.0f  lambdas=%g\n',copper_RRR(ii),lambdas(ii));
    end

    % fit quadratic
    % plot
    %hold off
    %plot(copper_RRR, lambdas,'o');
    %size(copper_RRR)
    %size(lambdas)
    pterms = polyfit(log(copper_RRR'), lambdas,4);
    %hold on
    %plot(50:500,polyval(pterms,log(50:500)));

    lambda = polyval(pterms, log(RRR));

    % extrapolate with linear in RRR, not this funky fit
    Routset = find((RRR < min(copper_RRR)) + (RRR > max(copper_RRR)));
    if numel(Routset) > 0
        pterms = polyfit(copper_RRR(:), lambdas(:), 1);
        for ii=1:numel(Routset)
            lambda(Routset(ii)) = polyval(pterms, RRR(Routset(ii)));
        end
    end

    if Ttrueval > 0        % Ttrueval contains the input temp, T=4
        lambda = lambda*(Ttrueval/T)^1;      % T^1 dependence about right 
               % for low T
    end

end



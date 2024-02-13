function k = therm_conduct(T,material,varargin)
% k = therm_conduct(T,material,varargin)
%  return thermal conductivity (W/m/K) of a materal at temperature T
%  other value might be RRR
%  
% T             in Kelvin
% material      "copper","stainless" or "SS", "aluminum" or "6061", 
%               "aluminum 1100" or "1100", "A95083" or "aluminum 5083"
%               "manganin", 
%               "tungsten", "mylar", "kevlar" (49), "lead", "5083" (Aluminum),
%               "brass" (UNS C26000), "G10" or "G-10" or "g10" or "g-10",
%               "nylon", "invar", "kapton", "kevlar49composite"
%               "macor" (0.1 - 4K), "NbTi" (~4-8.5K), 
%               "Ti-6-4" (UNS R56400) (20-300K), no interp
%               "Ti-15-3-3-3" (14.88% V, 3.13% Cr, 2.88% Sn, 3.00% Al)
%                  1.4-300; interp lin to 0, note pure Ti supercond Tc=0.39K 
%                  probably overest... may drop like T^3 or something, might 
%                  be going superconductive at higher T, like NbTi or TiN
%                  and this one is turning over already by 1.4K
%               "polyurethane" (4 types, all foam, "othervalue" = 1,2,3,4)
%               "PET" polyethylene terephthlate; othervalue is powerlaw 
%               below 2K, except == 1 (linear) if othervalue == 0 (so if 
%               really want constant below 2K, give something tiny but !=0)
%               "CFRP", Runyan and Jones 2008, 0.3 < T < 4.2K,
%               "PTFE" or "Teflon" (NIST), extrap below 4K w/lin in log-log, 
%               probably overestimate by up to factor of 2 by 1K
%               "indium"
%               "phosphorbronze" - Lakeshore vals, but extrap below 1K 
%               just a guess based on last couple points (alpha=1.5)
%               Kapton: NIST, or Benford if othervalue == 1, or 
%                Barucci if othervalue == 2 (note othervalue is not interp 
%                as power law index below 4K, NIST extrap is set at T^1)
% othervalue    RRR for copper (either keyword,value pair, or if it is 
%               a numeric following the material, will assumed to be 
%               "othervalue") 
% other variables
% force         value = alpha, forced power law index to extrapolate below 
%               lowest T in data (usually 4K for NIST data)
%
%
% v1.0  20150701 KLT; added other materials w/o incrementing versions
%           latest: aluminum 20150711
% v1.1  20151106: put copper in loop over T values; rest should already be OK
% v1.2  20170809 add nargin()==0 check, run help on this file if so
% v1.3  20171110 add kapton, from Benford et al 1999 (othervalue==1) and NIST
% v1.4  20180515 extrap SS below 4K w/T^1.3
% v1.5  20180801 add Kevlar49 composite
%           note check out Ventura, et al 2000 for 0.1 - 2.5K Kevlar 49
% v1.6  20180910 add macor, NbTi
% v1.7  20181004 add Ti-6-4 UNS R56400 --- screwy numbers
% v1.8  20190331 add polyurethane (4 varietes, from NIST)
% v1.9  20191025,28 add PET polyethylene terephthalate from NIST
%                 change version variable -> versionthing
% v2.0  20191120 add aluminum 1100
% v2.1  20191127 add aluminum 5083
% v2.2  20200220 add CFRP
% v2.3  20200318 add PTFE/Teflon
% v2.4  20200923 debugged Ti-6-4 (hadn't taken exponent after solving poly)
%                added Ti 15-3-3-3
% v2.5  20210306 add force, add varargin, allow legacy simple numeric 
%                   for othervalue (RRR) following material name w/o keyword
%                force implemented for copper, brass (note copper calls 
%                   therm_cond.m, which already has forced T^1 extrap, <4K, 
%                   but we can override that here)
%                implemented with new function extrap_lower(), generic, 
%                   passes vararg so can get k(Tlowest), only need to set 
%                   value of Tlowest and execute this func (note need to be 
%                   careful not to recurse more than once to get k(Tlowest))
% v2.51 20211025 add indium
% v2.52 20221108 add phosphor bronze from Lakeshore
% v2.6  20230706 add Barucci et al 2000 data for Kapton, T^1 extrap < 4K for 
%                        NIST data for Kapton

    versionthing = 2.6;

    if nargin() == 0
        help therm_conduct
        return
    end

    RRR = 0;
    powerindex = nan;

    if nargin > 2
        ii = 1;
        if isnumeric(varargin{ii})
            othervalue = varargin{ii++};  % legacy 3rd arg=value, no keyword
        end
        while ii<=length(varargin)
            switch (lower (varargin{ii}))
                case 'othervalue', othervalue = varargin{++ii};
                case 'force', powerindex = varargin{++ii};
                otherwise
                    fprintf(...  
                       'therm_conduct(): varargin = %s not recognized (%d)\n',...
                       varargin{ii},ii);
            end
            ii++;
        end

    end


    switch material
        case "copper"
            mat = 1;
            RRR = othervalue;
        case {"stainless" "SS"}
            mat = 2;
        case {"aluminum" "6061"}
            mat = 3;
        case {"aluminum 1100" "1100"}
            mat = 21;
        case {"A95083", "aluminum 5083"}
            mat = 22;
        case "manganin"
            mat = 4;
        case "tungsten"
            mat = 5;
        case "mylar"
            mat = 6;
        case "kevlar"
            mat = 7;
        case "lead"
            mat = 8;
        case "5083"
            mat = 9;
        case "brass"
            mat = 10;
        case {"G10" "G-10" "g10" "g-10"}
            mat = 11;
        case {"nylon" "Nylon"}
            mat = 12;
        case "invar"
            mat = 13;
        case {"kapton" "Kapton"}
            mat = 14;
        case {"kevlar49composite"}
            mat = 15;
        case {"macor"}
            mat = 16;
        case {"NbTi"}
            mat = 17;
        case {"Ti-6-4"}
            mat = 18;
        case {"polyurethane"}
            mat = 19;
            ptype = othervalue;
        case {"PET", "pet"}
            mat = 20;
            extrap_power = 1;
            if othervalue != 0
                extrap_power = othervalue;
            end
        % mat == 21,22 taken -- aluminum 5083, 1100, above
        case {"CFRP"}
            mat = 23;
        case {"PTFE","Teflon"}
            mat = 24;
        case {'Ti-15-3-3-3'}
            mat = 25;
        case {'Indium','indium','INDIUM'}
            mat = 26;
        case {'phosphorbronze','phosphor bronze'}
            mat = 27;
        otherwise
            mat = 0;
    endswitch



    if mat == 0
        fprintf("material '%s' not implemented\n",material);
        k = 0;
        return;
    end

    if mat == 1    % copper
        % send to therm_cond()
        k = T*0;
        for ii=1:numel(T)
            k(ii) = therm_cond(T(ii),RRR);
        end
        Tlowest = 4.0;
        k = extrap_lower(k,T,Tlowest, powerindex,material,varargin);
        return;
    end
    if mat == 2      % stainless
        % therm conductivity and specific heat
        % a -1.4087 22.0061
        % b 1.3982 -127.5528
        % c 0.2543 303.647
        % d -0.6260 -381.0098
        % e 0.2334 274.0328
        % f 0.4256 -112.9212
        % g -0.4658 24.7593
        % h 0.1650 -2.239153
        % i -0.0199 0
        % data range 4-300 4-300
        % equation range 1-300 4-300
        % curve fit % error relative to data 2 5
        thdata = [ -1.4087 22.0061
                    1.3982 -127.5528
                    0.2543 303.647
                    -0.6260 -381.0098
                    0.2334 274.0328
                    0.4256 -112.9212
                    -0.4658 24.7593
                    0.1650 -2.239153
                    -0.0199 0];
        % use thdata(:,1) for thermal conductivity
        % equation is y = 10^( a + b*LT + c*LT^2 + d*LT^3... i*LT^8 )
        % where LT == log10(T)
        LT = log10(T);
        k = 0.0;
        for ii=1:9
            k = k + thdata(ii,1)*LT.^(ii-1);
        end
        k = 10.^k;
        % NOTE: T ~ 4:20K looks like T^1.3, so extrap low 
        % with that from 4K value
        if min(T) < 4
            k4 = therm_conduct(4.0,'SS');
            for ii=find(T < 4)
                k(ii) = k4*(T(ii)/4.0)^1.3;
            end
        end
    end
    if (mat == 3)           % aluminum
        % aluminum 6061
        % a 0.07918 46.6467
        % b 1.0957 -314.292
        % c -0.07277 866.662
        % d 0.08084 -1298.3
        % e 0.02803 1162.27
        % f -0.09464 -637.795
        % g 0.04179 210.351
        % h -0.00571 -38.3094
        % i 0 2.96344
        % data range 4-300 4-300
        % equation range 1-300 4-300
        % curve fit % error relative to data 0.5 5
        % first column thermal conductivity, 2nd column specific heat
        thdata = [0.07918 46.6467
                   1.0957 -314.292
                   -0.07277 866.662
                   0.08084 -1298.3
                   0.02803 1162.27
                   -0.09464 -637.795
                   0.04179 210.351
                   -0.00571 -38.3094
                   0 2.96344];
        % standard curve
        LT = log10(T);
        k = 0.0;
        for ii=1:numel(thdata(:,1))
            k = k + thdata(ii,1)*(LT.^(ii-1));
        end
        k = 10.^k;
    end
    if (mat == 21)           % AL 1100
        % Thermal Conductivity
        % UNITS   W/(m-K)
        % a   23.39172
        % b   -148.5733
        % c   422.1917
        % d   -653.6664
        % e   607.0402
        % f   -346.152
        % g   118.4276
        % h   -22.2781
        % i   1.770187
        % data range 4-300
        % equation range 4-300
        % curve fit % error relative to data 2
        thdata = [ 23.39172
                   -148.5733
                   422.1917
                   -653.6664
                   607.0402
                   -346.152
                   118.4276
                   -22.2781
                   1.770187];
        % standard log10(T) poly
        LT = log10(T);
        k = 0.0;
        for ii=1:numel(thdata)
            k = k + thdata(ii)*(LT.^(ii-1));
        end
        k = 10.^k;
    end
    if mat == 22        % Al 5083
        % Thermal Conductivity        Specific Heat
        % UNITS  W/(m-K)  J/(kg-K)
        % a  -0.90933  46.6467
        % b  5.751  -314.292
        % c  -11.112  866.662
        % d  13.612  -1298.3
        % e  -9.3977  1162.27
        % f  3.6873  -637.795
        % g  -0.77295  210.351
        % h  0.067336  -38.3094
        % i  0  2.96344
        % data range
        % 4-300  4-300
        % equation range
        % 1-300  4-300
        % curve fit % error relative to data  1  5
        thdata = [ -0.90933  46.6467
                  5.751  -314.292
                  -11.112  866.662
                  13.612  -1298.3
                  -9.3977  1162.27
                  3.6873  -637.795
                  -0.77295  210.351
                  0.067336  -38.3094
                  0  2.96344];
        % want first column: is standard 10^poly(log10(T))
        tdat2 = thdata(end:-1:1,1);
        LT = log10(T);
        k = 10.0.^polyval(tdat2,LT);
        %k = 0.0;
        %for ii=1:numel(tdat2)
        %    k += tdat2(ii)*(LT.^(ii-1));
        %end
        %k = 10.^k;
    end
    if (mat == 4) || (mat == 5)
        % manganin, tungsten (99.99+%),  
        % from CRC 58th edition, 1977-1978, p. E-10
        % table, interpolate -- 1st column T (Kelvin), 2nd in W/cm/K
        thdata = [0, 0.0,     0.0
                  1, 0.0007, 14.4
                  2, 0.0018, 28.7
                  3, 0.0031, 42.6
                  4, 0.0046, 55.6
                  5, 0.0062, 67.1
                  6, 0.0078, 76.2
                  7, 0.0095, 82.4
                  8, 0.0111, 85.3
                  9, 0.0128, 85.1
                  10, 0.0145, 82.4
                  11, 0.0162, 77.9
                  12, 0.0180, 72.4
                  13, 0.0197, 66.4
                  14, 0.0215, 60.4
                  15, 0.0232, 54.8
                  16, 0.0250, 49.3
                  18, 0.0285, 40.0
                  20, 0.0322, 32.6
                  25, 0.0410, 20.4
                  30, 0.0497, 13.1
                  35, 0.0583, 8.9
                  40, 0.067, 6.5
                  45, 0.075, 5.07
                  50, 0.082, 4.17
                  60, 0.097, 3.18
                  70, 0.110, 2.76
                  80, 0.120, 2.56
                  90, 0.127, 2.44
                 100, 0.133, 2.35
                 150, 0.156, 2.10
                 200, 0.172, 1.97
                 250, 0.193, 1.86
                 273, 0.206, 1.82
                 300, 0.222, 1.78
                 350, 0.250, 1.70];
        % interpolate
        % NOTE the lowest 2 points (or lowest several) of manganin do not 
        % represent a T^1 power law, a bit steeper than that though seems 
        % to be flattening as one goes lower
        %% REM: these are W/cm/K, not W/m/K, so need to mult by 100
        if mat == 4
            k = interp1(thdata(:,1),thdata(:,2),T,"spline")*100;
        end
        if mat == 5
            k = interp1(thdata(:,1),thdata(:,3),T,"spline")*100;
            %loglog(thdata(:,1),thdata(:,3),"+");
            %loglog(T,k);
        end
        return;
    end
    if mat == 6     % mylar
        % a -1.37737
        % b -3.40668
        % c 20.5842
        % d -53.1244
        % e 73.2476
        % f -57.6546
        % g 26.1192
        % h -6.34790
        % i 0.640331
        % data range 1-83
        % equation range 2-80
        % curve fit % error relative to data 1
        thdata = [ -1.37737
                   -3.40668
                   20.5842
                   -53.1244
                   73.2476
                   -57.6546
                   26.1192
                   -6.34790
                   0.640331];
        % equation: y = 10^(a + b*LT + c*LT^2 +...)
        LT = log10(T);
        k = 0.0;
        for ii = 1:numel(thdata)
            k = k + thdata(ii)*LT.^(ii-1);
        end
        k = 10.^k;
    end
    if mat == 7          % Kevlar kevlar
        % a -2.4219
        % b 1.986637
        % c 1.257441
        % d 0.961209
        % e -9.6106
        % f 0.777857
        % data range 0.1-291
        % equation range 0-350
        % curve fit standard error relative to data 3.1
        thdata = [-2.4219
                   1.986637
                   1.257441
                   0.961209
                   -9.6106
                   0.777857];
        % equation:
        % log10(k) = ( (a + b*LT)*(1 - erf(2*(LT-c)))/2 
        %              + (d + e*exp(-LT/f))*(1 + erf(2*(LT-c)))/2 )
        % REM erf(x) = (2/sqrt(pi))*INTEGRAL{e^(-t^2) dt}[0,x]
        LT = log10(T);
        k = (thdata(1) + thdata(2)*LT).*(1 - erf(2*(LT-thdata(3))))/2;
        k = k + (thdata(4) + thdata(5)*exp(-LT/thdata(6))).*(1+erf(2*(LT-thdata(3))))/2;
        k = 10.^k;

    end
    if mat == 8        % lead
        %%% NOTE: equation range down to 5K, Tc = 7.19 and don't even see 
        %%% a turnover there, so probably suspect below Tc
        % a 38.963479
        % b -221.40505
        % c 597.56622
        % d -900.93831
        % e 816.40461
        % f -455.08342
        % g 152.94025
        % h -28.451163
        % i 2.2516244
        % data range 4-296
        % equation range 5-295
        % curve fit % error relative to data 2
        thdata = [38.963479
                 -221.40505
                 597.56622
                 -900.93831
                 816.40461
                 -455.08342
                 152.94025
                 -28.451163
                 2.2516244];
        % 10^(SUM(d_i*(log10(T)^(i-1))
        LT = log10(T);
        k = 0.0;
        for ii=1:numel(thdata)
            k = k + thdata(ii)*LT.^(ii-1);
        end
        k = 10.^k;
    end
    if mat == 9        % AL 5083
        % first column thermal conductivity, 2nd specific heat
        % a -0.90933 46.6467
        % b 5.751 -314.292
        % c -11.112 866.662
        % d 13.612 -1298.3
        % e -9.3977 1162.27
        % f 3.6873 -637.795
        % g -0.77295 210.351
        % h 0.067336 -38.3094
        % i 0 2.96344
        % data range
        % 4-300 4-300
        % equation range
        % 1-300 4-300
        % curve fit % error relative to data 1 5
        thdata = [ -0.90933 46.6467
                     5.751 -314.292
                     -11.112 866.662
                     13.612 -1298.3
                     -9.3977 1162.27
                     3.6873 -637.795
                     -0.77295 210.351
                     0.067336 -38.3094
                     0 2.96344];
        % standard log10(T) poly
        LT = log10(T);
        k = 0.0;
        for ii=1:numel(thdata(:,1))
            k = k + thdata(ii,1)*LT.^(ii-1);
        end
        k = 10.^k;
    end
    if mat == 10     % brass
        % brass
        % thermal conductivity W/K/m
        % UNITS W/(m•K)
        % a 0.021035
        % b -1.01835
        % c 4.54083
        % d -5.03374
        % e 3.20536
        % f -1.12933
        % g 0.174057
        % h -0.0038151
        % i 0
        % data range
        % 5-116
        % equation range
        % 5-110
        % curve fit % error relative to data 1.5
        thdata = [0.021035
                -1.01835
                4.54083
                -5.03374
                3.20536
                -1.12933
                0.174057
                -0.0038151
                0];
        % standard log10(T) poly
        Tlowest = 5.0;
        LTlowest = log10(Tlowest);
        LT = log10(T);
        k = 0.0;
        klowest = 0.0;
        for ii=1:numel(thdata(:,1))
            k = k + thdata(ii,1)*LT.^(ii-1);
        end
        k = 10.^k;
        k = extrap_lower(k,T,Tlowest, powerindex,material,varargin);
    end
    if mat == 11       % G-10
        %           
        % Thermal Conductivity
        % (Normal Direction)
        % 
        % Thermal Conductivity
        % (Warp Direction)
        % Specific Heat
        % 
        % UNITS W/(m-K) W/(m-K) J/(kg•K)
        % a -4.1236 -2.64827 -2.4083
        % b 13.788 8.80228 7.6006
        % c -26.068 -24.8998 -8.2982
        % d 26.272 41.1625 7.3301
        % e -14.663 -39.8754 -4.2386
        % f 4.4954 23.1778 1.4294
        % g -0.6905 -7.95635 -0.24396
        % h 0.0397 1.48806 0.015236
        % i 0 -0.11701 0
        % data range
        % 4-300 4-300 4-300
        % equation range
        % 10-300 12-300 4-300
        % curve fit % error relative to data
        % 5 5 2
        % equation:
        % log10(y) = a + b*log10(T) + c*log10(T)^2 ...
        thdata = [-4.1236 -2.64827 -2.4083
                    13.788 8.80228 7.6006
                    -26.068 -24.8998 -8.2982
                    26.272 41.1625 7.3301
                    -14.663 -39.8754 -4.2386
                    4.4954 23.1778 1.4294
                    -0.6905 -7.95635 -0.24396
                     0.0397 1.48806 0.015236
                    0 -0.11701 0];
        % so want warp direction, thdata(:,2)
        k = T*0.0;
        LT = log10(T);
        for ii=1:numel(thdata(:,2))
            k = k + thdata(ii,2)*(LT.^(ii-1));
        end
        k = power(10.0,k);
    end
    if mat == 12        % Nylon
        %  
        % Thermal Conductivity
        % Specific Heat
        % UNITS W/(m-K) J/(kg-K)
        % a -2.6135 -5.2929
        % b 2.3239 25.301
        % c -4.7586 -54.874
        % d 7.1602 71.061
        % e -4.9155 -52.236
        % f 1.6324 21.648
        % g -0.2507 -4.7317
        % h 0.0131 0.42518
        % i 0 0
        % data range
        % 4-300 4-300
        % equation range
        % 1-300 4-300
        % curve fit % error relative to data
        % 2 4
        % equation:
        % log10(y) = a + b*log10(T) + c*log10(T)^2 ...
        thdata = [ -2.6135 -5.2929
                    2.3239 25.301
                    -4.7586 -54.874
                    7.1602 71.061
                    -4.9155 -52.236
                    1.6324 21.648
                    -0.2507 -4.7317
                    0.0131 0.42518
                    0 0];
        %k = T*0.0;
        %LT = log10(T);
        %for ii=1:numel(thdata(:,1))
        %    k = k + thdata(ii,1)*(LT.^(ii-1));
        %end
        %k = power(10.0,k);
        k = power_law_thing(T, thdata(:,1), 1, 4, 1.304);
    end
    if mat == 13         % invar
        % Thermal Conductivity
        % Specific Heat
        % UNITS W/(m-K) J/(kg-K)
        % a -2.7064 28.08
        % b 8.5191 -228.23
        % c -15.923 777.587
        % d 18.276 -1448.423
        % e -11.9116 1596.567
        % f 4.40318 -1040.294
        % g -0.86018 371.2125
        % h 0.068508 -56.004
        % i 0 0
        % data range
        % 4-300 4-20
        % equation range
        % 4-300 4-27
        % curve fit % error relative to data 2 2
        thdata = [-2.7064 28.08
                  8.5191 -228.23
                  -15.923 777.587
                  18.276 -1448.423
                  -11.9116 1596.567
                  4.40318 -1040.294
                  -0.86018 371.2125
                  0.068508 -56.004];
        k = T*0.0;
        LT = log10(T);
        for ii=1:numel(thdata(:,1))
            k = k + thdata(ii,1)*(LT.^(ii-1));
        end
        k = power(10.0,k);
    end
    if mat == 14
        % Kapton
        % see Benford et al discussion; their number is for tape, not 
        % having removed the adhesive, and values up to factor of 2 larger 
        % than other film meas. in literature; Rule et al measured 
        % 2 different grades, got different answers; the NIST value looks 
        % lower than anything referenced in Benford 
        % note added 2023-07-06: Barucci, et al 2000 Kapton HN, 
        %   6.5 +/- 0.2 x 10^-5  T^(1+/-0.02) W/cm K   0.1 - 9K, though 
        %   looks like the data for Kapton only goes to ~0.18K not 0.10K
        if othervalue == 1
            % from Benford, et al. 1999, Cryogenics, 39, 93-95
            % give equation for lambda(T) ~ 5.24e-3 T^1.02 W/m/K
            k = (5.24e-3)*T.^1.02;
        elseif othervalue == 2
            % Barucci et al 2000; 0.1-9K
            k = 6.5e-3*T;
        else
            % NIST
            % a 5.73101 -1.3684
            % b -39.5199 0.65892
            % c 79.9313 2.8719
            % d -83.8572 0.42651
            % e 50.9157 -3.0088
            % f -17.9835 1.9558
            % g 3.42413 -0.51998
            % h -0.27133 0.051574
            % i 0 0
            % data range
            % 4-300 4-300
            % equation range
            % 4-300 4-300
            % curve fit % error relative to data 2 3
            % so need 1st column
            thdata = [5.73101 -1.3684
                      -39.5199 0.65892
                      79.9313 2.8719
                       -83.8572 0.42651
                       50.9157 -3.0088
                      -17.9835 1.9558
                      3.42413 -0.51998
                      -0.27133 0.051574];
            % equation is k = 10^(a + b*(log10(T))^1 + c*(log10(T))^2 +...
            k = 0.0;         % sum the exponent first
            for nn=1:numel(thdata(:,1))
                k += thdata(nn,1)*(log10(T).^(nn-1));
            end
            k = 10.^k;
            lowTset = find(T < 4);
            if numel(lowTset) > 0
                % extrapolate w/ T^1
                k4 = therm_conduct(4,"Kapton",0);
                k(lowTset) = k4*(T(lowTset)/4).^1;
            end
        end
    end
    if mat == 15      % Kevlar 49 composite
        % NIST
        % Thermal Conductivity
        % UNITSW/(m-K)
        % a -2.65
        % b 1.986637
        % c 1.24851
        % d 0.57
        % e -8
        % f 0.777857
        % data range 6-302
        % equation range 0-350
        % curve fit standard error relative to data 7.4
        kdat = [-2.65, 1.986637, 1.24851, 0.57, -8, 0.777857];
        % eqn:
        % x = log10(T)
        % y = (a + b*x)*(1 - erf(2*(x-c)))/2 + 
        %            (d + e*exp(-x/f)))*(1 + erf(2*(x-c)))/2
        % k = 10^y
        x = log10(T);
        y = (kdat(1) + kdat(2)*x).*(1 - erf(2*(x-kdat(3))))/2;
        y += (kdat(4) + kdat(5)*exp(-x/kdat(6))).*(1 + erf(2*(x-kdat(3))))/2;
        k = 10.^y;
    end
    if mat == 16      % macor, Runyan + Jones 2008, 0.1 - 4K only
        alpha = 4e-3;    % R&J use 4.00 mW/m/K
        beta = 2.55; 
        gamma = -0.140;
        nnn = -0.142;
        k = alpha*T.^(beta + gamma*T.^nnn);
    end
    if mat == 17    % NbTi, Schmidt 1979, ~4 - 8.5K only (superconducting)
                    % probably OK below that, nice power law
        alpha = 0.075;       % mW/cm/K
        beta = 1.85;
        alpha = alpha*0.001/0.01;    % mW/cm -> W/m
        k = alpha*T.^beta;
    end
    if mat == 18     % Ti-6-4 (UNS R56400)   titanium
        % Thermal Conductivity 
        % UNITS units:W/(m•K)
        % a -5107.8774
        % b 19240.422
        % c -30789.064
        % d 27134.756
        % e -14226.379
        % f 4438.2154
        % g -763.07767
        % h 55.796592
        % i 0
        % data range
        % 23-300
        % equation range
        % 20-300
        % curve fit % error relative to data
        % 2
        datTi = [-5107.8774
                19240.422
                -30789.064
                27134.756
               -14226.379
                4438.2154
                -763.07767
                55.796592
                0];
        k = polyval(datTi(end:-1:1), log10(T));
        k = power(10.0,k);
        Tlow = 23;
        cset = find(T < Tlow);
        %%% FIXED -- needs 10^poly()  (was just poly())
        % NOTE: NIST's clam of equation OK to 20K, it is already negative 
        % there, SO, will use 23K and extrapolate down with T^1 law, 
        % But note this will go bad at least at the transition T (~0.39K)
        % and might be a poor approximation above that -- 
        % and given the funkiness of the curve, probably shouldn't even 
        % trust the NIST formula parameters to 23K; OK to 60 or 70K, even?
        % NOTE that matweb claims Ti6Al4V i.e. Ti-6-4 has therm. conduct 
        % of 6.7 W/m/C, no T given, but this NIST equation at 296K gives 
        % 0.87 W/m/K - almost an order of mag off... 
        if numel(cset) > 0
            k(cset) = polyval(datTi(end:-1:1), log10(Tlow))*(T(cset)/Tlow);
            k(cset) = power(10.0,k(cset));
        end
        %fprintf('WARNING: therm_conduct(): Ti-6-4 data bad, nearly order \n');
        %fprintf('   of mag off at room T, no telling how far off at low T\n');
    end
    if mat == 19       % polyurethane foam, from NIST, 4 types
        % Thermal Conductivity density: 31.88 kg/m3 (=1.99 lb/ft3 Freon filled )
        % Thermal Conductivity density: 32.04 kg/m3 (=2.0 lb/ft3 % CO2 Filled)
        % Thermal Conductivity density: 49.02 kg/m3 (=3.06 lb/ft3 He Filled )
        % Thermal Conductivity density: 64.08 kg/m3 (=4.00 lb/ft3 Freon filled)
        % UNITS W/(m-K) W/(m-K) W/(m-K) W/(m-K))
        % a -3218.679 3788.43 -33.898 789.79
        % b 9201.61 -7642.66 117.81 -2347.94
        % c -10956.66 4592.448 -178.376 3024.61
        % d 6950.102 778.8423 142.038 -2206.76
        % e -2476.94 -2214.434 -63.034 989.238
        % f 470.284 1090.293 14.958 -273.18
        % g -37.1669 -235.6349 -1.5468 43.065
        % h 0 19.66088 0.020625 -2.9863
        % i 0 0 0 0
        % data range
        % 76-300 100-300 30-300 88-300
        % equation range
        % 60-300 85-300 20-300 55-300
        % curve fit % error relative to data 2 1 1 2
        pudata = [ -3218.679 3788.43 -33.898 789.79
                    9201.61 -7642.66 117.81 -2347.94
                    -10956.66 4592.448 -178.376 3024.61
                    6950.102 778.8423 142.038 -2206.76
                    -2476.94 -2214.434 -63.034 989.238
                    470.284 1090.293 14.958 -273.18
                    -37.1669 -235.6349 -1.5468 43.065
                    0 19.66088 0.020625 -2.9863 ];
        if ptype == 0 
            k = 0;
        else
            k = polyval(pudata(end:-1:1,ptype), log10(T));
            k = power(10.0,k);
        end
    end
    if mat == 20    % PET from NIST
        % Thermal Conductivity
        % UNITS     W/(m•K)
        % a     -1.37737
        % b     -3.40668
        % c     20.5842
        % d     -53.1244
        % e     73.2476
        % f     -57.6546
        % g     26.1192
        % h     -6.34790
        % i     0.640331
        % data range 1-83
        % equation range  2-80
        % curve fit % error relative to data    1
        %% equation: log10(y) = a + b*log10(T) + c*log10(T)^2 + ...
        petdata = [-1.37737, -3.40668, 20.5842, -53.1244, 73.2476,... 
                       -57.6546, 26.1192, -6.34790, 0.640331];
        k = polyval(petdata(end:-1:1), log10(T));
        k = power(10.0, k);
        % equation range 2 - 80K
        % override: linear below 2K, worst-case, and linear to the 
        % 0.199 "average value" for PET unreinforced from matweb: 
        %% 0.0150 - 0.290 W/m-K  0.104 - 2.01 BTU-in/hr-ft²-°F  
        %%          Average value: 0.199 W/m-K Grade Count:21
        % future: use powerlaw index "extrap_power" below 2K
        tset = find(T > 80.0);
        if numel(tset) > 0
            TVALS = [80, 293];
            KVALS = [therm_conduct(80.0, 'PET'), 0.199];
            k(tset) = interp1(TVALS, KVALS, T(tset), 'linear');
        end
        tset = find(T < 2);
        if numel(tset) > 0
            TVALS = [0.2, 2];
            KVALS = [10.0^(-extrap_power),1]*therm_conduct(2.0,'PET');
            k(tset) = interp1(TVALS, KVALS, T(tset), 'linear','extrap');
        end
    end
    if mat == 23       % CFRP, Runyan and Jones 2008
        % 0.3 < T < 4.2K, at mercy of extrapolation beyond those limits
        % Runyan/Jones has Graphlite carbon fiber
        mW = 0.001;
        alpha = 8.39*mW;
        beta = 2.12;
        gamma = -1.05;
        n = 0.181;
        betaEff = beta + gamma*(T.^n);
        k = alpha*(T.^betaEff);
    end
    if mat == 24 % PTFE/Teflon, NIST
        %     Thermal Conductivity Specific Heat
        % UNITS   W/(m-K)   J/(kg-K)
        % a   2.7380   31.88256
        % b   -30.677   -166.51949
        % c   89.430   352.01879
        % d   -136.99   -393.44232
        % e   124.69   259.98072
        % f   -69.556   -104.61429
        % g   23.320   24.99276
        % h   -4.3135   -3.20792
        % i   0.33829   0.16503
        % data range  4-300   4-300
        % equation range  4-300   4-300
        % curve fit % error relative to data       1.5
        ptfedata = [ 2.7380,  31.88256
                    -30.677,  -166.51949
                    89.430 , 352.01879
                    -136.99,  -393.44232
                    124.69 , 259.98072
                    -69.556,  -104.61429
                    23.320 , 24.99276
                    -4.3135,  -3.20792
                    0.33829,  0.16503];
        k = polyval(ptfedata(end:-1:1,1), log10(T));
        k = power(10.0, k);
        % override: use 4,5K points to linearly extrapolate low side in 
        % log-log space
        set_tlow = find(T < 4.0);
        if numel(set_tlow) > 0
            Tset = [4.0,5.0];
            logkset = polyval(ptfedata(end:-1:1,1), log10(Tset));
            k(set_tlow) = power(10.0, ...
                interp1(log10(Tset),logkset,...
                log10(T(set_tlow)),'linear','extrap'));
        end 
    end
    if mat == 25      % Ti-15-3-3-3    14.88% V, 3.13% Cr, 2.88% Sn, 3.00% Al
        %    Thermal Conductivity
        % UNITS W/(m-K)
        % a  -2.398794842
        % b  8.970743802
        % c  -29.19286973
        % d  54.87139779
        % e  -59.67137228
        % f  38.89321714
        % g  -14.94175848
        % h  3.111616089
        % i  -0.270452768
        % data range 1.4-300
        % equation range 1.4-300
        % curve fit % error relative to data 3
        Ti15333data = [-2.398794842
                        8.970743802
                        -29.19286973
                        54.87139779
                        -59.67137228
                        38.89321714
                        -14.94175848
                        3.111616089
                        -0.270452768];
        k = polyval(Ti15333data(end:-1:1), log10(T));
        k = power(10.0,k);
        set_tlow = find(T < 1.4);
        if numel(set_tlow) > 0
            % interp lin to 0,0
            klow = power(10.0,polyval(Ti15333data(end:-1:1),log10(1.4)));
            k(set_tlow) = klow*(T(set_tlow)/1.4);
        end
    end
    if mat == 26      % indium
        % BNL_crygenic_data_handbook_Section7.pdf, p. VII-E-3, W/cm/K
        % found in ~/Data5b/Materials/Reference/
        % no date, editor names, looks like lost a page or few at top
        % this is table of values, so do spline interp
        % extrapolated above 30K... 
        In_data = [ 4, 8.4
                    6, 8.2
                    8, 6.3
                   10, 4.4
                   15, 2.4
                   20, 1.8
                   25, 1.45
                   30, 1.2
                   35, 1.1
                   40, 1.0
                   50, 0.9
                   60, 0.84
                   70, 0.8
                   76, 0.79
                   80, 0.77
                   90, 0.73
                  100, 0.72
                  120, 0.70
                  140, 0.69
                  160, 0.68
                  180,  0.67
                  200,  0.66
                  250,  0.66
                  300,  0.66];
        % note Matweb has 83.7 W/m/K, or 0.837 W/cm/K for 0C = 273K
        In_data(:,2) = In_data(:,2)*100.0;
        k = spline(In_data(:,1), In_data(:,2), T);

    end
    if mat == 27   % phosphor bronze
        PB_data = [1, 0.22
                   4, 1.6
                   10, 4.6
                   20, 10
                   80, 25
                   150, 34
                   300, 48];    % W/m/K
        k = spline(PB_data(:,1), PB_data(:,2), T);
        set_Tlow = find(T < 1.0);
        if numel(set_Tlow) > 0
            k(set_Tlow) = PB_data(1,2)*(T(set_Tlow)/1.0).^1.5;   % alpha=1
            % power law 1.5 just a guess based on extrap.
        end

    end


end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function kval = power_law_thing(T,polydata, plaw_extract=0, Tlow, alpha)
    % take care of everything, assuming standard 
    if plaw_extract == 1
        tsetlow = find(T < Tlow);
        tsethigh = find(T >= Tlow);
    else 
        tsetlow = [];
        tsethigh = 1:numel(T);
    end
    kval = T*0;
    if numel(tsethigh) > 0
        kval(tsethigh) = polyval(polydata(end:-1:1), log10(T(tsethigh)));
        kval(tsethigh) = power(10.0,kval(tsethigh));
    end
    if numel(tsetlow) > 0
        kval(tsetlow) = polyval(polydata(end:-1:1), log10(Tlow));
        kval(tsetlow) = power(10.0, kval(tsetlow));
        kval(tsetlow) = kval(tsetlow).*(T(tsetlow)/Tlow).^alpha;
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function kvals = extrap_lower(kvals_in,T,Tlowest,powerindex,material,varargin2)
    % extrapolate, if desired, to T lower than Tlowest
    if isnan(powerindex)   
        kvals = kvals_in;
        return;
    end
    % note could get infinite loop if this function decided, due to 
    % round-off error, that a T value was < Tlowest even though it was 
    % actually equal to Tlowest -- thus when trying to get k(Tlowest) 
    % in the main therm_conduct() function, it would keep getting 
    % kicked into this subfunction 
    lowTset = find(T < (Tlowest - 1e-6));
    kvals = kvals_in;
    if numel(lowTset) > 0
        klowest = therm_conduct(Tlowest, material,varargin2{:});
        kvals(lowTset) = klowest*(T(lowTset)/Tlowest).^powerindex;
    end
end


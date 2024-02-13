function result = therm_conduct_integ(Trange,material,othervalue=0)
% function result = therm_conduct_integ(Trange,material,othervalue=0)
% integrate therm_conduct(T) from Trange(1) to Trange(2)
% 
% Trange        limits of integration, 1st two values used 
% material      passed straight to therm_conduct()
% othervalue    passed straight to therm_conduct()
%
% v1.0 20200623 KLT
%

    versionthing = 1.0;

    if numel(Trange) < 2
        fprintf('WARNING: Trange() must be at least 2-vector\n');
        result = 0;
        return
    end

    afunc234 = @(T) therm_conduct(T,material,othervalue);

    result = quadgk(afunc234, Trange(1), Trange(2));


end

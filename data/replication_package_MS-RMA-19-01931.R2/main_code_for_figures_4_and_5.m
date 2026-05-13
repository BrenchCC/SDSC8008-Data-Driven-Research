clc; clear all; close all;
rng('default');

alpha = 1.1; %unknown intercept
beta = -0.5; %unknown slope
sigma = 0.1; %unknown std of noise
t_max = 10000; %time horizon
increment = 10; %time increment for plots
n_sim = 10;%number of simulations

zeta = 0.1; %exponential smoothing parameter

% eta_plus = 0; eta_min = 0;   %reference parameters
eta_plus = 0.1; eta_min = 0.3; %reference parameters

p_min = 0.5; %lowest admissible price
p_max = 1.5;
p_star = alpha / (-2*beta); %assumed in (pmin, pmax)

p = zeros(t_max,1); %prices
d = zeros(t_max,1); %demand
price_paths = zeros(t_max-3,n_sim); %price paths
ref_price_paths = zeros(t_max,n_sim); %reference price paths
regret = zeros(t_max,n_sim); %regret

c_0 = (p_max-p_min)/10;

for sim = 1:n_sim
    sim
    
    epsilon = sigma * randn(1, t_max); %noise terms
    r1 = p_min + (p_max-p_min) * rand(); %initial reference_price
    reference_price = r1;
    cycle_begin = 0;
    n = 2;
    p_star_hat = 1;
    delta = c_0*2^(-0.25);
    
    for t = 1 : t_max
        if t <= cycle_begin + n
            p(t) = max(p_min, min(p_max, p_star_hat-delta ));
        elseif t <= cycle_begin + 2*n
            p(t) = max(p_min, min(p_max, p_star_hat+delta ));
        end
        
        d(t)      = alpha + beta * p(t) + eta_plus * max(0, reference_price - p(t)) - eta_min * max(0, p(t) - reference_price) + epsilon(t); %demand
        rev       = p(t) * (d(t) - epsilon(t)); %revenue
        benchmark = p_star * (alpha + beta * p_star + eta_plus * max(0,r1 - p_star) * zeta^(t-1) - eta_min * max(0, p_star - r1) * zeta^(t-1)); 
        if t==1
            regret(t, sim) = benchmark - rev;
        else
            regret(t, sim) = regret(t-1, sim) + benchmark - rev; 
        end
        reference_price = zeta * reference_price + (1 - zeta) * p(t); %update reference price
        
        if t == cycle_begin + 2*n
           cycle_begin  =  cycle_begin + 2*n;
           n = 2*n;
           par_hat = regress(d(1:t-1), [ones(t-1,1), p(1:t-1)]);
           alpha_hat = par_hat(1); beta_hat = par_hat(2);
           p_star_hat = alpha_hat / (-2 * beta_hat);
           delta = delta*2^(-0.25);
        end
        
        if t > 3
            price_paths(t-3, sim) = max(p_min, min(p_max,  alpha_hat / (-2 * beta_hat) ));
        end
        ref_price_paths(t, sim) = reference_price;
    end
end

output = mean(regret, 2)';
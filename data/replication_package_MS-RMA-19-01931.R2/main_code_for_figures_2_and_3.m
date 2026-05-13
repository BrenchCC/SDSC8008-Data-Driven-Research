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
p_star = alpha / (-2 * beta); %assumed in (pmin, pmax)

p = zeros(t_max,1); %prices
d = zeros(t_max,1); %demand
price_paths = zeros(t_max-2,n_sim); %price paths
ref_price_paths = zeros(t_max,n_sim); %reference price paths
regret = zeros(t_max, n_sim); %regret

for sim = 1: n_sim
    sim
    
    epsilon = sigma * randn(1, t_max); %noise terms
    r1 = p_min + (p_max-p_min) * rand(); %initial reference_price
    reference_price = r1; 
    cycle = 0; %policy counter for BR
    for t = 1 : t_max
            if t == 1 + 2*cycle + cycle * (cycle + 1) / 2
                cycle = cycle + 1;
                p(t) = (p_max - p_min)* 1/3  + p_min; %first exploration price
            elseif t == 2 + 2*(cycle - 1) + (cycle - 1) * cycle / 2
                p(t) = (p_max - p_min)* 2/3  + p_min; %2nd exploration price
            else %exploit
                par_hat = regress(d(1:t-1), [ones(t-1,1), p(1:t-1)]);
                alpha_hat = par_hat(1); beta_hat = par_hat(2);
                p(t) = max(p_min, min(p_max,  alpha_hat / (-2 * beta_hat) ));
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
        
        if t > 2
            price_paths(t-2, sim) = max(p_min, min(p_max,  alpha_hat / (-2 * beta_hat) ));
        end
        ref_price_paths(t, sim) = reference_price;
    end
end

output = mean(regret, 2)';
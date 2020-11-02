from scipy import stats
import matplotlib.pyplot as plt
import numpy as np 

def count_success_failure(arr):
    success = arr.sum()
    failure = len(arr) - success
    return success, failure

def plot_with_fill(ax, x, y, label, color="#D55E00"):
    lines = ax.plot(x, y, label=label, lw=2, color=color)
    ax.fill_between(x, 0, y, alpha=0.2, color=color)
    ax.legend()

def graph_bayes(arr_a, arr_b, legend_a, legend_b, plot_title, color_a='#D55E00', color_b="#0072B2", xmax=0.5):
    
    success_a, failure_a = count_success_failure(arr_a)
    success_b, failure_b = count_success_failure(arr_b)

    # Assuming uniform prior 
    dist_a = stats.beta(a =1+success_a, b =1+failure_a)
    dist_b = stats.beta(a =1+success_b, b =1+failure_b)
    
    a_95_high = dist_a.ppf(.975)
    a_95_low = dist_a.ppf(.025)
    b_95_high = dist_b.ppf(.975)
    b_95_low = dist_b.ppf(.025)

    x = np.arange(0,1, 0.001)
    y_a = dist_a.pdf(x)
    y_b = dist_b.pdf(x)

    fig, ax = plt.subplots(figsize=(10,4))
    plot_with_fill(ax, x, y_a, legend_a, color=color_a)
    plot_with_fill(ax, x, y_b, legend_b, color=color_b)
    ax.axvline(a_95_high, ymin=.05, label=f"{legend_a}: 95% credible interval", linestyle='--', color="#666666")
    ax.axvline(a_95_low, ymin=.05, color="#666666", linestyle='--')
    ax.axvline(b_95_high, ymin=.05, label=f"{legend_b}: 95% credible interval", color="#666666", linestyle=':')
    ax.axvline(b_95_low, ymin=.05, color="#666666", linestyle=':')
    ax.legend()
    ax.set_ylabel('Probability Density')
    ax.set_title(plot_title, fontsize=15)
    ax.set_xlim(0,xmax)
    
    return dist_a, dist_b, fig


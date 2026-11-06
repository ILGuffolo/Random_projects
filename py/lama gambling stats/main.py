import matplotlib.pyplot as plt
import math
import numpy as np

def p(n, k, p):
        return math.factorial(n) / (math.factorial(n-k) * math.factorial(k)) * p**k * (1 - p)**(n - k)

Dtn = range(1, 25 +1)
Dp = range(1, 5 +1)
B = range(0, 25 +1)

def outcome(D, b):
    sum = 0
    for j in range(b, D):
        sum += p(D, j, 1/3)
    return sum

def plot_3d(x_array, y_array):
    """
    Plots a 3D surface for z = z_func(x, y)
    
    Parameters:
    x_array: array-like of x values
    y_array: array-like of y values
    """
    # Create a meshgrid of all x, y combinations
    X, Y = np.meshgrid(x_array, y_array)
    
    # Compute Z values for each (x, y)
    Z = np.zeros_like(X, dtype=float)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = outcome(X[i, j], Y[i, j])
    
    # Contour plot
    plt.contourf(X, Y, Z, levels=np.linspace(0,1,11), cmap='viridis')
    plt.colorbar(label='Probability')
    
    # Add grid
    plt.grid(True, color='white', linestyle='--', linewidth=0.5)
    
    # Highlight the z = 0.5 line
    contour = plt.contour(X, Y, Z, levels=[0.5], colors='red', linewidths=2)
    plt.clabel(contour, fmt='z=0.5', inline=True, fontsize=10)

    plt.xlabel('x (trials)')
    plt.ylabel('y (successes ≥)')
    plt.title('Probability of at least y successes in x trials')
    plt.show()
    
    
plot_3d(Dtn, B)


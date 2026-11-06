import numpy as np
import matplotlib.pyplot as plt

def f(z):
    return z**2

# domain
x = np.linspace(-2, 2, 200)
y = np.linspace(-2, 2, 200)

X, Y = np.meshgrid(x, y)

Z = X + 1j*Y

W = f(Z)

surface = W.imag   # selectable

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, surface)

plt.show()


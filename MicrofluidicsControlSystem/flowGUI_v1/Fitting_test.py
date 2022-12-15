import numpy as np
from sympy import *
from scipy.optimize import curve_fit
from sympy.utilities.lambdify import lambdify
import matplotlib.pyplot as plt
from IPython.display import display

x = Symbol("x")
xs = [0, -1, 1, .5, -.5]
ys = [.5, .269, .731, .622, .378]

L,k,x0,x = symbols('L k x_0 x')
f = L/(1+(exp(-k*(x-x0))))
display(f)

syms = list(f.free_symbols)
syms.remove(x)
syms.insert(0,x)
py_f = lambdify(syms,f)

popt, pcov = curve_fit(py_f, xs, ys, maxfev = 4 * (10**5))

syms.pop(0)
subs_arg = dict(list(zip(syms, popt)))

f1 = f.subs(subs_arg)
display(f1)

f2 = lambdify([x],f1)

# plot input data points
plt.scatter(np.array(xs),np.array(ys),color="red")

# plot fitted function
xp = np.arange(min(xs), max(xs)+1, 0.05)
yp = f2(xp)
plt.plot(xp,yp,color="blue")
plt.show()
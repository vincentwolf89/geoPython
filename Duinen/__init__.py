import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np

x = np.arange(0, 10)
y = np.exp(-x/3.0)
f = interpolate.interp1d(x, y)

a = np.array([1,2,3,4,5,6])
test = np.interp(a, (a.min(), a.max()), (-1, +1))

# print test
# xnew = np.arange(0, 9, 0.1)
# ynew = f(xnew)   # use interpolation function returned by `interp1d`
# plt.plot(x, y, 'o', xnew, ynew, 'o')
# plt.show()





a = [1,2,3,4,5,6,7,8,9,10]
b = [1,4.5,6.9]
order = 0  # To determine a and b.

if len(b) > len(a):
    a, b = b, a  # swap the values so that 'a' is always larger.
    order = 1

div = len(a) / len(b)  # In Python2, this already gives the floor.
a = a[::div][:len(b)]

if order:
    print b
    print a
else:
    print a
    print b
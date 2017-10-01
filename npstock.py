import numpy as np 
import matplotlib.pyplot as plt

N=10
C=20
assets = np.zeros((N,C));
returns = np.zeros((N,C));

R_1= np.random.normal(1.01,0.03,C)
returns[0]=R_1
assets[0]=np.cumprod(R_1)

for i in range(1,N):
	R_i = R_1 + np.random.normal(0.001,0.02,C)
	returns[i] = R_i
	assets[i] = np.cumprod(R_i)

mean_returns=[(np.mean(R)-1)*C for R in returns]
retur_volatilities = [np.std(R) for R in returns] 

for R in returns:
	print(R)
	print('-------------------------')

plt.bar(np.arange(len(mean_returns)),mean_returns)
plt.xlabel('stock')
plt.ylabel('meanReturns')
plt.title('{0} random assets return'.format(N))
plt.show()

print("ok")



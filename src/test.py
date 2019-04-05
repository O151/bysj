# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 20:16:27 2018

@author:  
"""

import matplotlib.pyplot as plt
import numpy as np

A = [[1.1994	,	0.4343	,	0.3712	,	0.3478	,	0.3395	,	0.3336],
[0.7851	,	0.3309	,	0.3297	,	0.3104	,	0.2641	,	0.2486],
[0.3634	,	0.1933	,	0.1797	,	0.1683	,	0.1503	,	0.1488],
[0.203	,	0.113	,	0.1098	,	0.1006	,	0.1064	,	0.1002]]
a = np.array(A)
plt.figure()
line = ['-o','-d','-s','-x']
for i in range(4):
    plt.plot(A[i],line[i])
plt.legend(['NINO1+2','NINO3','NINO3+4','NINO4'])
plt.xlabel('M')
plt.ylabel('MSE')
plt.grid()

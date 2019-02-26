#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 20:34:41 2018

@author: deepak
"""


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import lines
import scipy.integrate as integrate
import scipy.optimize as optimize
import scipy.stats as stats
import cmocean
plt.close("all")


#------------------------------------------------------------------------------
# System parameters
#------------------------------------------------------------------------------
tol = 1e-6
#------------------------------------------------------------------------------
W = 3e-3
N = 100 
nu = 1e-6
q = 2 # Aspect ratio of the object


lc = W
tc = W**2/nu
uc = lc/tc
ac = uc/tc

W_nd = W/lc

#maxAcc=1000 step.s-2 equilalent to 0.0276 m.s-2
#maxSpeed=1000 step.s-1 equilalent to 0.0276 m.s-2
#a0=0.0276
a0 = 0.0001
Umax = 1e-3 # Max organism speed in m/s
#a0 =0.01
tau = Umax/a0

tau_nd = tau/tc
a0_nd = a0/ac

print(50*'-')
print('Length scale: {} m'.format(W))
print('Time scale: {} s'.format(tc))

print('Velocity scale: {} mm/s'.format(uc*1000))
print('Accln scale: {} mm/s^2'.format(ac*1000))
print(50*'-')

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Defining coefficients for the Velocity expansion
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
def A_n(n):    
    return -4*np.pi**(-1)*(2*n+1)**(-1)

def k_n2(n):
    return (2*n+1)**2*np.pi**2

def F_n(n,t):
    return np.exp(-k_n2(n)*t)

def V_n(y,n):
    return np.sin((2*n+1)*np.pi*y)

def V_n_dy(y,n):
    return (2*n+1)*np.pi*(np.cos((2*n+1)*np.pi*y))

def V(y,t):
    
    V_sum = 0
    
    
    for nn in range(N):
            
        V_sum += A_n(nn)*F_n(nn,t)*V_n(y,nn)
            
    return 1 + V_sum


def ShearRate_y(y,t):
    
    ShearRate_y_sum = 0
    
   
    for nn in range(N):
            
        ShearRate_y_sum += A_n(nn)*F_n(nn,t)*V_n_dy(y,nn)
            
    return ShearRate_y_sum
    
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      Position, velocity and acceleration of the Stage
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''


print(50*'-')
print('Dimensionless ramp time: {} '.format(tau_nd))
print('Dimensionless stage acceleration{} '.format(a0_nd))
print(50*'-')

def q1(t,tau_nd, a0_nd):                             #Position
    q=0
    if (t>0) and (t<tau_nd):
        q=0.5*a0_nd*t**2
    elif (t>=tau_nd):
        q=0.5*a0_nd*tau_nd**2+a0_nd*tau_nd*(t-tau_nd)
    return q

def dtq1(t,tau_nd, a0_nd):                           #Velocity
    dtq=0
    if (t>0) and (t<tau_nd):
        dtq=a0_nd*t
    elif (t>=tau_nd):
        dtq=a0_nd*tau_nd
    return dtq

def dttq1(t,tau_nd, a0_nd):                          #acceleration
    dttq=0
    if (t>=0) and (t<tau_nd):
        dttq=a0_nd
    return dttq

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      Velocity of fluid due to the stage velocity
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
def integrand(tt,t,tau,x,y):
    return dttq1(tt,tau)*V(x,y,t-tt)

def U(y,t,tau_nd,a0_nd):                #analytic calculation
    U=0
    if (t>=0) and (t<tau_nd):
        U=a0_nd*t
        U_sum = 0
        for nn in range(N):
            addTerm = a0_nd*A_n(nn)*V_n(y,nn)*(1 - np.exp(-k_n2(nn)*t))/(k_n2(nn))
            
            if(U_sum != 0):
                if(np.abs(addTerm/U_sum) <=tol):
                    break
            U_sum += addTerm
            
        print('Series converged in {} terms'.format(nn))

               
    elif (t>=tau_nd):
        
        U=a0_nd*tau_nd

        U_sum = 0   
        for nn in range(N):
            addTerm = a0_nd*A_n(nn)*V_n(y,nn)*(np.exp(-k_n2(nn)*(t - tau_nd))-np.exp(-k_n2(nn)*t))/(k_n2(nn))
            if(U_sum != 0):
                if(np.abs(addTerm/U_sum) <=tol):
                    break
            U_sum += addTerm
#    print(U)
        print('Series converged in {} terms'.format(nn))
    return U + U_sum


def U_dy(y,t,tau_nd,a0_nd):                #analytic calculation
    U_dy=0
    if (t>=0) and (t<tau_nd):
       
        for nn in range(N):
            addTerm = a0_nd*A_n(nn)*V_n_dy(y,nn)*(1 - np.exp(-k_n2(nn)*t))/(k_n2(nn))
            if(U_dy != 0):
                if(np.abs(addTerm/U_dy) <=tol):
                    break
                
            U_dy += addTerm
        
        print('Series converged in {} terms'.format(nn))
               
    elif (t>=tau_nd):
        
        for nn in range(N):
            addTerm = a0_nd*A_n(nn)*V_n_dy(y,nn)*(np.exp(-k_n2(nn)*(t - tau_nd))-np.exp(-k_n2(nn)*t))/(k_n2(nn))
            if(U_dy != 0):
                if(np.abs(addTerm/U_dy) <=tol):
                    break
            U_dy += addTerm
            
        print('Series converged in {} terms'.format(nn))

    return U_dy

def Unum(x,y,t):            ##numeric calculation
    U=0
    U=integrate.quad(integrand,0,t,args=(t,tau,x,y))[0]
    return U

def getMaxShearRate(y_pos, T, tau_nd, a0_nd):
    
    print('Non-dimensional acceleration : {}'.format(a0_nd))
    ShearRate_y_list = [U_dy(y = y_pos,t = t,tau_nd = tau_nd,a0_nd = a0_nd) for t in T]
    
    ShearRate_y = np.array(ShearRate_y_list)
    
    ShearRate_mag = (ShearRate_y**2)**(1/2)

    maxShear_Time = T[np.argmax(ShearRate_mag)]
    
    maxShear = np.max(ShearRate_mag)
    
    return maxShear, maxShear_Time

def ShearRate_vs_accln(y_pos, U_max_nd, a0_array):
    
    tau_nd_array = U_max_nd/a0_array
    
    maxShear = np.zeros_like(a0_array)
    maxShear_Time = np.zeros_like(a0_array)
    
    for ii in range(len(a0_array)):
        
        tau_nd, a0_nd = (tau_nd_array[ii], a0_array[ii])
        
        T_max_nd = max(1,tau_nd*2)

        # For each acceleration we need to specify the T vector to use
        T = np.concatenate((np.linspace(0,tau_nd,100),np.linspace(tau_nd,T_max_nd,50)), axis = 0)

#        print('Max velocity: {}'.format(tau_nd*a0_nd))
        
#        print('Ramp time: {}'.format(tau_nd))
        maxShear[ii], maxShear_Time[ii] = getMaxShearRate(y_pos=y_pos, T=T,tau_nd=tau_nd,a0_nd = a0_nd)
        
    idx = np.isfinite(maxShear)

    
    plt.figure()

    ax = plt.plot(np.log10(a0_array[idx]), np.log10(maxShear[idx]), marker = 'o')
#    plt.yscale('log')
#    plt.xscale('log')
    plt.xlabel('Dimensionless Stage acceleration')
    plt.ylabel('Dimensionless Max Shear rate')
    
    
    p =np.polyfit(np.log10(a0_array[idx]),np.log10(maxShear[idx]),deg = 1)
    
    print('Slope from polynomial fit : {}'.format(p[1]))
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.log10(a0_array[idx]),np.log10(maxShear[idx]))
    
    print('Slope of the linear fit: {} with R-value: {}'.format(slope, r_value ))
    
    plt.figure()

    ax = plt.plot(a0_array, maxShear_Time,marker = 'o', color = 'r')

    plt.xlabel('Dimensionless Stage acceleration')
    plt.ylabel('Delay in Max Shear rate peak time')



'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
              Velocity in the middle of the channel
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''


T_max_nd = max(1,tau_nd*2)

print(30*'#')
print('Max dimensionless time: {}'.format(T_max_nd))
print(30*'#')
      
T = np.concatenate((np.linspace(0,tau_nd,100),np.linspace(tau_nd,T_max_nd,50)), axis = 0)

#T = np.linspace(0,T_max_nd,400)

DTQ = [dtq1(t,tau_nd,a0_nd) for t in T]
U_list = [U(W_nd/2,t,tau_nd,a0_nd) for t in T]

ShearRate = [U_dy(0,t,tau_nd,a0_nd) for t in T]

ShearRate = np.array(ShearRate)
ShearRate_mag = (ShearRate**2)**(1/2)

maxShear_Time = T[np.argmax(ShearRate_mag)]

print(50*'=')
print('Dimensionless max shear rate: {}'.format(np.max(ShearRate_mag)))
print('Dimensionless Ramp Time : {}'.format(tau_nd))
print('Dimensionless Time of Max Shear Rate : {}'.format(maxShear_Time))
print(50*'=')
#U_list = [Unum(L/2,W/2,t) for t in T]


y_pos = 0

stage_accln = 0.0276 # Max accln of Z stage in m/s^2 (1000 full steps/s)

a_max = 0.01
a_min = 0.00001

U_max = 1e-3    # Max organism speed that can be tracked

U_max_nd = U_max/uc

a_min_nd = a_min/ac
a_max_nd = a_max/ac

a0_array = np.logspace(-5,0,100)/ac

tau_nd_array = U_max_nd/a0_array

#ShearRate_vs_accln(y_pos = y_pos, U_max_nd = U_max_nd, a0_array = a0_array)

#------------------------------------------------------------------------------
# Stage Speed vs Fluid center line Speed
#------------------------------------------------------------------------------

plt.figure()
plt.plot(T,DTQ,label="Velocity of the walls",linewidth=2)
plt.plot(T,U_list,label="Fluid's velocity in y=0 (analytic)",linewidth=2)
plt.axvline(x = tau_nd, color ='r',linestyle='--')

#plt.plot(T[0:int(len(T)/2)],DTQ[0:int(len(T)/2)],label="Velocity of the walls",linewidth=0.8)
#plt.plot(T[0:int(len(T)/2)],U_list[0:int(len(T)/2)],label="Fluid's velocity in y=0 (analytic)",linewidth=0.8)
#plt.plot(T,UNUM,label="Fluid's velocity in y=0 (numeric)")
plt.xlabel("Dimensionless time")
plt.ylabel("Dimensionless velocity")
#plt.title("Velocity of the walls vs. minimal velocity of the fluid")
plt.legend()
#plt.savefig("C:/Users/Francois/Desktop/minimal_velocity.svg")
plt.show()


#------------------------------------------------------------------------------
# Shear Rate In the Channel vs Time
#------------------------------------------------------------------------------

plt.figure()
plt.plot(T,ShearRate,label="Shear Rate in the channel",linewidth=2)
plt.axvline(x = tau_nd, color ='r',linestyle='--')

#plt.plot(T[0:int(len(T)/2)],DTQ[0:int(len(T)/2)],label="Velocity of the walls",linewidth=0.8)
#plt.plot(T[0:int(len(T)/2)],U_list[0:int(len(T)/2)],label="Fluid's velocity in y=0 (analytic)",linewidth=0.8)
#plt.plot(T,UNUM,label="Fluid's velocity in y=0 (numeric)")
plt.xlabel("Dimensionless time")
plt.ylabel("Dimensionless Shear Rate")
#plt.title("Velocity of the walls vs. minimal velocity of the fluid")
plt.legend()
#plt.savefig("C:/Users/Francois/Desktop/minimal_velocity.svg")
plt.show()
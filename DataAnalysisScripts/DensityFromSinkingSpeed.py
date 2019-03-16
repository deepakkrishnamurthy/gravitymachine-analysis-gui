#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:17:39 2019

@author: deepak
"""

U = 0.127*1e-3

mu = 1e-3

g = 9.81

r = (1e-6)*137/2

delta_rho = 9*mu*U/(2*g*r**2)

print(delta_rho)
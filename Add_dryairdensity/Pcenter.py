#!/usr/bin/env python3

# test air pressure at center ~ average of top and bottom

from math import pow
kappa = 0.2857

p1=2300 # 2300 and 100300
p0=2000 # 2000 and 100000

kap1 = kappa + 1.0

kapr = 1.0 / kappa

Pcenter=pow(((pow(p1, kap1) - pow(p0, kap1))/(kap1*(p1 -p0))), kapr)

print(Pcenter)# 2148.75 and 100149.97

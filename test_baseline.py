from recommender import *
import timeit
import time
from math import sqrt, floor, ceil
import random


    
def testUBbaseline(T):
    print("############################\nNEW TEST RUN")
    print("User-based baseline CF")
    print("n = {}\nm = {}".format( T.n, T.m))
    print("")
    
    T.CF = baseline.UBCF(T.n, T.m, T.R, T.B)
    
    print "BUILD MODEL"
    tmodel=timeit.timeit(T.CF.build_model, number=1)
    
    print "{:4} {:4}  {:8}".format("n","m", "tmodel")
    print "{:<4d} {:<4d} {:8.4f}".format(T.n,T.m, tmodel)
        

    
def testIBbaseline(T):
    print("############################\nNEW TEST RUN")
    print("Item-based baseline CF")
    print("n = {}\nm = {}".format( T.n, T.m))
    print("")
    
    T.CF = baseline.IBCF(T.n, T.m, T.R, T.B)
    
    print "BUILD MODEL"
    tmodel=timeit.timeit(T.CF.build_model, number=1)
    print "{:4} {:4}  {:8}".format("n","m", "tmodel")
    print "{:<4d} {:<4d} {:8.4f}".format(T.n,T.m, tmodel)
    
def testPredictions(T, knn_params, sampsize): 
    if T.CF == None:
        raise RuntimeError("Call another test to build model first!")
    
    print "PREDICTIONS"
    print "{:4} {:4}  {:8} {:8} {:8}".format("k","f", "mae", "rmse", "tpred")
    
    for (k, f) in knn_params:
        
        start_time = time.clock()
        mae = 0
        rmse = 0
        
        sampling = random.sample(T.Rlist,sampsize)
        
        for (u,i,r) in sampling:
                prediction = T.CF.nn_prediction(u,i, k, f)
                error = abs(prediction + T.mean[u] - r)
                mae += error
                rmse += (error)**2
        
        mae = mae / sampsize
        rmse = sqrt(rmse / sampsize)
        end_time = time.clock()
        tpred = end_time-start_time
        print "{:<4d} {:<4d}  {:8.6f} {:8.6f} {:8.4f}".format(k,f, mae, rmse, tpred)

    

"""
Uncomment to Estimate Parameter K
"""
# K_PARAMS = range(1,31)
# F = 14
# NPREDICTIONS = 5000
# knn_params = zip(K_PARAMS, [F]*30)
#     
#     
# T = Test(1).eval_data().mean_centered() # Maximum Size
# testUBbaseline(T)
# testPredictions(T, knn_params, NPREDICTIONS)
#         
# T = Test(2).eval_data().mean_centered() # Maximum Size
# testIBbaseline(T)
# testPredictions(T, knn_params, NPREDICTIONS)
"""
Uncomment to Estimate Parameter f'
"""
# K = 9
# F_PARAMS = range(1,15)
# NPREDICTIONS = 5000
# knn_params = zip([K]*14, F_PARAMS)
#  
# T = Test(10).eval_data().mean_centered() # Maximum Size
# testUBbaseline(T)
# testPredictions(T, knn_params, NPREDICTIONS)
#      
# T = Test(20).eval_data().mean_centered() # Maximum Size
# testIBbaseline(T)
# testPredictions(T, knn_params, NPREDICTIONS)

"""
Uncomment to measure UB performance
"""

# PREDICT = True
# NPREDICTIONS = 5000
# N_PARAMS = [100,200,300,400,500]
# M_PARAMS = [2000,3000,4000,5000,6000]
# K = 9
# F = 4
#  
#   
# for id,n in enumerate(N_PARAMS):
#     T = Test(id*10).eval_data(n=n).mean_centered()
#     testUBbaseline(T)
#     if PREDICT:
#         testPredictions(T, [(K, F)], NPREDICTIONS)
#          
# for id,m in enumerate(M_PARAMS):
#     T = Test(id*10+100).eval_data(m=m).mean_centered()
#     testIBbaseline(T)
#     if PREDICT:
#         testPredictions(T, [(K, F)], NPREDICTIONS)
#    
#   
"""
Debugging 
"""        
# K = 10
# F = 4
# N = 100
# M = 2000
# NPREDICTIONS = 5000
# 
# T = Test(1).small_data().mean_centered() 
# testUBbaseline(T)
# T.CF.print_model()
# testPredictions(T, [(2, 14)], 16)
# 
# T = Test(2).small_data().mean_centered() 
# testIBbaseline(T)
# T.CF.print_model()
# testPredictions(T, [(2, 14)], 16)
# 
# T = Test(3).eval_data(n=N, m=M).mean_centered() 
# testUBbaseline(T)
# testPredictions(T, [(K, F)], NPREDICTIONS)
#      
# T = Test(4).eval_data(n=100, m=2000).mean_centered() 
# testIBbaseline(T)
# testPredictions(T, [(K, F)], NPREDICTIONS)
        
        
        
        
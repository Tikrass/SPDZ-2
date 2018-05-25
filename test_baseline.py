from recommender import *
import timeit
import time
from math import sqrt, floor, ceil
import random

class Test():
    def __init__(self):
        self.n = 0
        self.m = 0
        self.rowcap = None
    
    # DATA
    def small_data(self):
        self.n = 5
        self.m = 5
        self.rowcap = 5
        self.R =[[0.0,1.0,3.0,4.0,0.0],
                 [2.0,1.0,0.0,4.0,0.0],
                 [0.0,2.0,3.0,0.0,3.0],
                 [5.0,0.0,2.0,1.0,0.0],
                 [4.0,3.0,0.0,1.0,4.0]]
        self.B = [[0,1,1,1,0],
                   [1,1,0,1,0],
                   [0,1,1,0,1],
                   [1,0,1,1,0],
                   [1,1,0,1,1]]
        
        self.K = 2

        self.NPREDICTIONS = 5
        
        return self
    
    def eval_data(self, n=None, m=None): 
        folder = "Prep-Data/ml-latest-small"
        
        D = dataset(folder)
        self.R, self.B = D.read(n,m)
        self.n = D.n
        self.m = D.m
        self.rowcap = 2400
        
        self.K = 10

        self.NPREDICTIONS = 500
        
        return self
    

    
    def mean_centered(self):
        self.mean = [0 for _ in range(self.n)]
        for u in range(self.n):
            count = 0
            for i in range(self.m):
                self.mean[u] += self.R[u][i]
                count += self.B[u][i]
            self.mean[u] = self.mean[u]/count
            for i in range(self.m):
                if self.B[u][i] == 1:
                    self.R[u][i] = self.R[u][i] - self.mean[u]
        
        return self
    
    
    def testUBbaseline(self, id, predict):
        n = self.n
        m = self.m
        R = self.R
        B = self.B
        K = self.K
        NPREDICTIONS = self.NPREDICTIONS
        
        print("############################\nNEW TEST RUN")
        print("User-based baseline CF")
        print("n = {}\nm = {}".format( n, m))
        print("")
        
        CF = baseline.UBCF(n, m, R, B)
        
        print "BUILD MODEL"
        tmodel=timeit.timeit(CF.build_model, number=1)
        print "tmodel: {}".format(tmodel)
        

        if (predict):
            print "PREDICTION"
            start_time = time.clock()
            mae = 0
            rmse = 0
            predictions = 0
            pperuser = int(floor(NPREDICTIONS/n))
            additionals = NPREDICTIONS - pperuser * n
            for u in range(n):
                Iu = [i for i in range(m) if B[u][i]==1]
                if u <= additionals:
                    sampsize = pperuser + 1
                else:
                    sampsize = pperuser
                sampling = random.sample(Iu, sampsize)
                for i in sampling:
                    prediction = CF.nn_prediction(u,i, K)
                    error = prediction - R[u][i]
                    #print "u: {}, i: {}, prediction: {}, error: {}".format(u, i, prediction, error)
                    error = abs(error)
                    mae += error
                    rmse += (error)**2
            
            mae = mae / NPREDICTIONS
            rmse = sqrt(rmse / NPREDICTIONS)
            end_time = time.clock()
            print "MAE: ", mae
            print "RMSE: ", rmse
            print "tpred: ", end_time-start_time
        
    
    def testIBbaseline(self, id, predict):
        n = self.n
        m = self.m
        R = self.R
        B = self.B
        K = self.K
        NPREDICTIONS = self.NPREDICTIONS
        
        print("############################\nNEW TEST RUN")
        print("Item-based baseline CF")
        print("n = {}\nm = {}".format( n, m))
        print("")
        
        CF = baseline.IBCF(n, m, R, B)
        
        print "BUILD MODEL"
        tmodel=timeit.timeit(CF.build_model, number=1)
        print "tmodel: {}".format(tmodel)
        
        if (predict):
            print "PREDICTION"
            start_time = time.clock()
            mae = 0
            rmse = 0
            predictions = 0
            pperuser = int(floor(NPREDICTIONS/n))
            additionals = NPREDICTIONS - pperuser * n
            for u in range(n):
                Iu = [i for i in range(m) if B[u][i]==1]
                if u <= additionals:
                    sampsize = pperuser + 1
                else:
                    sampsize = pperuser
                sampling = random.sample(Iu, sampsize)
                for i in sampling:
                    prediction = CF.nn_prediction(u,i, K)
                    error = prediction - R[u][i]
                    #print "u: {}, i: {}, prediction: {}, error: {}".format(u, i, prediction, error)
                    error = abs(error)
                    mae += error
                    rmse += (error)**2
            
            mae = mae / NPREDICTIONS
            rmse = sqrt(rmse / NPREDICTIONS)
            end_time = time.clock()
            print "MAE: ", mae
            print "RMSE: ", rmse
            print "tpred: ", end_time-start_time
        
N_PARAMS = [100, 200, 300, 400, 500]
 
M_PARAMS = [2000, 3000, 4000, 5000, 6000]
 
PREDICT = True
for id,n in enumerate(N_PARAMS):
    T = Test().eval_data(n=n).mean_centered()
    T.testUBbaseline(id*10+0, PREDICT)
       
for id,m in enumerate(M_PARAMS):
    T = Test().eval_data(n=200,m=m).mean_centered()
    T.testIBbaseline(id*10+100, PREDICT)
          
# T = Test().small_data().mean_centered()
# T.testUBbaseline(10, True)
# T = Test().small_data().mean_centered()
# T.testIBbaseline(20, True)        
        
        
        
        
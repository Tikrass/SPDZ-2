from recommender.baseline import BaselineUBCF, BaselineIBCF
from recommender.dataset import Dataset
from recommender.io import InputFp

from Compiler.types import sfix
from Compiler.library import *
from Compiler.collaborative_filter import UBCosineCF, IBCosineCF, SparseUBCosineCF

import timeit
import time
import sys
from math import sqrt, floor, ceil


# Fix constant seed from compiler
import random as random2
random = random2.Random()
random.seed()

# Global parameters
sys.setrecursionlimit(100000)


folder = "Prep-Data/ml-latest-small"
class Test():
    def __init__(self, id):
        self.id = id

    # DATA
    def small_data(self):
        self.n = 5
        self.m = 5
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
        self.Rlist = [(0,1,1.0),(0,2,3.0),(0,3,4.0),
                      (1,0,2.0),(1,1,1.0),(1,3,4.0),
                      (2,1,2.0),(2,1,3.0),(2,4,3.0),
                      (3,0,5.0),(3,2,2.0),(3,3,1.0),
                      (4,0,4.0),(4,1,3.0),(4,3,1.0),(4,4,4.0) ]
        
        return self
    
    def eval_data(self, n=None, m=None): 
        D = Dataset(folder)
        self.R, self.B, self.Rlist, self.n, self.m = D.get(n,m)
        return self
    
    def mean_centered(self):
        self.mean = [0 for _ in range(self.n)]
        for u in range(self.n):
            count = 0
            for i in range(self.m):
                self.mean[u] += self.R[u][i]
                count += self.B[u][i]
            if count == 0:
                print u
            self.mean[u] = self.mean[u]/count
            for i in range(self.m):
                if self.B[u][i] == 1:
                    self.R[u][i] = self.R[u][i] - self.mean[u]
        
        return self
    
    
class SPDZTest(Test):
    def __init__(self, id, IO):
        Test.__init__(self, id)
        self.IO = IO
        

    
    def _prep_private_plain_input(self):
        #########################
        # Preparing Private Input
        #########################
        print("Preparing rating input.")
        for u in range(self.n):
            self.IO.append_fp_array([int(r* (2**sfix.f)) for r in self.R[u]])
        
        print("Preparing rating2 input.")
        for u in range(self.n):
            self.IO.append_fp_array([int((r**2)* (2**sfix.f)) for r in self.R[u]])
            
        print("Preparing bitrating input.")
        for u in range(self.n):
            self.IO.append_fp_array(self.B[u])
    
    def _private_plain_input(self):
        #########################
        # Reading Private Input
        #########################
        
        start_timer(self.id+1)

        print_ln("Loading private input.")
        @for_range(self.n)
        def user_loop1(u):
            self.CF.load_ratings_from(u, 0)
            
        @for_range(self.n)
        def user_loop2(u):
            self.CF.load_ratings2_from(u, 0)

        @for_range(self.n)
        def user_loop3(u):
            self.CF.load_bitratings_from(u, 0)
        stop_timer(self.id+1)
        
        
    def _prep_private_sparse_input(self, IO):
        #########################
        # Preparing Private Input
        #########################
        
        print("Preparing sparse rating input.")
        for u in range(n):
            input=[]
            tailpointer = 0
            for i in range(self.m):
                if bitratings[i] != 0:
                    input += [i,self.R[i]*(2**sfix.f), (self.R[i]**2)*(2**sfix.f)]
                    tailpointer += 1;
            if tailpointer > self.cap:
                raise CompileError("Tailpointer exceeds capacity: {} > {}!".format(tailpointer, capacity))
            for _ in range(tailpointer, capacity):
                input += [0,0,0] # Padding
            input += [tailpointer]
            IO.append_fp_array +=  input
            
    def _private_sparse_input(self):
        #########################
        # Reading Private Input
        #########################
        
        start_timer(self.id+1)

        print_ln("Loading private sparse input.")
        @for_range(self.n)
        def user_loop1(u):
            self.CF.load_ratings_from(u, 0)
        stop_timer(self.id+1)
        
    def buildUBplain(self):
        print_ln("############################\nNEW TEST RUN")
        print_ln("User-based CF")
        print_ln("n = %s\nm = %s", self.n, self.m)
        print_ln("")
        
        self.CF = UBCosineCF(self.n,self.m)
        
        self._prep_private_plain_input()
        self._private_plain_input()
        
        #########################
        # Building Model
        #########################
        start_timer(self.id+2)
        self.CF.build_model()
        stop_timer(self.id+2)

    def buildUBsparse(self, cap):
        print_ln("############################\nNEW TEST RUN")
        print_ln("Sparse User-based CF")
        print_ln("n = %s\nm = %s, cap = %s", self.n, self.m, cap)
        print_ln("")
        
        self.CF = SparseUBCosineCF(s.n,s.m, cap)
        
        self._prep_sparse_input()
        self._private_sparse_input()
        
        #########################
        # Building Model
        #########################
        start_timer(self.id+2)
        self.CF.build_model()
        stop_timer(self.id+2)
    
    def buildIBplain(self):   
        print_ln("############################\nNEW TEST RUN")
        print_ln("Item-based CF")
        print_ln("n = %s\nm = %s", self.n, self.m)
        print_ln("")
        
        self.CF = IBCosineCF(self.n, self.m)
        
        self._prep_private_plain_input()
        self._private_plain_input()
        
        #########################
        # Building Model
        #########################
        start_timer(self.id+2)
        self.CF.build_model()
        stop_timer(self.id+2)

    def testPredictions(self, knn_params, sampsize): 
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        
        print_ln("PREDICTIONS")
        print_ln("k    f     mae      rmse")
        
        timer_count = 1
        for (k, f) in knn_params:
            start_timer(self.id*100+timer_count)
            
            mae = cfix(0)
            rmse = cfix(0)
            
            sampling = random.sample(self.Rlist,sampsize)
            
            for (u,i,r) in sampling:
                print_str("%s to %s    \r", u, i)
                prediction = self.CF.nn_prediction(u,i, k, f)
                if isinstance(prediction, sfix):
                    prediction = prediction.reveal()
                error = prediction + self.mean[u] - r
                error = cint(error>=0) * (error + error) - error
                mae += error
                rmse += (error)**2
            
            mae = mae / sampsize
            rmse = (rmse / sampsize).sqrt()
            
            print_ln("%s   %s   %s %s",k, f, mae, rmse)
            stop_timer(self.id*100+timer_count)
            timer_count += 1
        
    def debugPredictions(self, k, f):
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        print_ln( "PREDICTIONS")
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                prediction = self.CF.nn_prediction(u,i, k, f)
                if isinstance(prediction, sfix):
                    prediction = prediction.reveal()
                prediction += self.mean[u]
                print_str("%s ", prediction)
            print_ln(' ')
            

class BaselineTest(Test):
    def buildUBbaseline(self):
        print("############################\nNEW TEST RUN")
        print("User-based baseline CF")
        print("n = {}\nm = {}".format( self.n, self.m))
        print("")
        
        self.CF = BaselineUBCF(self.n, self.m, self.R, self.B)
        
        print "BUILD MODEL"
        tmodel=timeit.timeit(self.CF.build_model, number=1)
        
        print "{:4} {:4}  {:8}".format("n","m", "tmodel")
        print "{:<4d} {:<4d} {:8.4f}".format(self.n,self.m, tmodel)
        

    
    def buildIBbaseline(self):
        print("############################\nNEW TEST RUN")
        print("Item-based baseline CF")
        print("n = {}\nm = {}".format( self.n, self.m))
        print("")
        
        self.CF = BaselineIBCF(self.n, self.m, self.R, self.B)
        
        print "BUILD MODEL"
        tmodel=timeit.timeit(self.CF.build_model, number=1)
        print "{:4} {:4}  {:8}".format("n","m", "tmodel")
        print "{:<4d} {:<4d} {:8.4f}".format(self.n,self.m, tmodel)
    
    def testPredictions(self, knn_params, sampsize): 
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        
        print "PREDICTIONS"
        print "{:4} {:4}  {:8} {:8} {:8}".format("k","f", "mae", "rmse", "tpred")
        
        for (k, f) in knn_params:
            
            start_time = time.clock()
            mae = 0
            rmse = 0
            
            sampling = random.sample(self.Rlist,sampsize)
            
            for (u,i,r) in sampling:
                    prediction = self.CF.nn_prediction(u,i, k, f)
                    error = abs(prediction + self.mean[u] - r)
                    mae += error
                    rmse += (error)**2
            
            mae = mae / sampsize
            rmse = sqrt(rmse / sampsize)
            end_time = time.clock()
            tpred = end_time-start_time
            print "{:<4d} {:<4d}  {:8.6f} {:8.6f} {:8.4f}".format(k,f, mae, rmse, tpred)

    def debugPredictions(self, k, f):
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        print "PREDICTIONS"
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                prediction = self.CF.nn_prediction(u,i, k, f)
                prediction += self.mean[u]
                print "{: 1.5f}".format(prediction),
            print ' '
            
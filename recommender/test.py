# (C) 2018 Thibaud Kehler. 
# MIT Licence
# see https://opensource.org/licenses/MIT

"""
Test suit to measure the performance and accuracy of the privacy-preserving
collaborative filter. Use the class ``SPDZTest`` to compile a test for SPDZ. 
Call the methods from Python directly to test the baseline. 

The initialization follows a build pattern. Make sure to pass every instance a unique ``ID``.

For a small 5x5 test dataset call "small_data()" after the constructor, e.g.::

    SPDZTest(ID).small_data()

For the MovieLens dataset call "eval_data(n,m)" with the dimensions of the rating matrix, e.g.::

    SPDZTest(ID).eval_data(600,3000)

To apply do mean-centering append ".mean_centered()".::

    SPDZTest(ID).eval_data(600,3000).mean_centered()

Call the test methods on the returned object.
"""

from recommender.baseline import BaselineUBCF, BaselineIBCF
from recommender.dataset import Dataset
from recommender.io import InputFp
from recommender.collaborative_filter import UBCosineCF, IBCosineCF, SparseUBCosineCF

from Compiler.types import sfix
from Compiler.library import *


import timeit
import time
import sys
from math import sqrt, floor, ceil


# Fix constant seed from compiler
import random as random2
random = random2.Random()
random.seed()

# Enlarge python recursion limit for large code.
sys.setrecursionlimit(1000000)

# Folder to the Movie Lens dataset.
folder = "Prep-Data/ml-latest-small"

class Test():
    """
    Abstract test class. Do not use instantiate this class. Instead use SPDZTest or BaselineTest.
    
    :param id: unique test id for timer. 
    """
    def __init__(self, id):
        self.id = id

    # DATA
    def small_data(self):
        """
        Small artificial 5x5 dataset.
        """
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
        """
        Loads the MovieLens Dataset from file in the specified dimension n x m.
        """
        D = Dataset(folder)
        self.R, self.B, self.Rlist, self.n, self.m = D.get(n,m)
        return self
    
    def mean_centered(self):
        """
        Use this method only after you loaded a dataset with one of the other methods!
        
        Transforms the dataset to a mean-centered version.
        """
        self.mean = [0 for _ in range(self.n)]
        for u in range(self.n):
            count = 0
            for i in range(self.m):
                self.mean[u] += self.R[u][i]
                count += self.B[u][i]
            if count == 0:
                print "No ratings for user ",u
                self.mean[u] = 2.5
            else:
                self.mean[u] = self.mean[u]/count
            for i in range(self.m):
                if self.B[u][i] == 1:
                    self.R[u][i] = self.R[u][i] - self.mean[u]
        
        return self
    
    def compute_rowcap(self):
        """
        Decduces an optimal row capacity c for the sparse representation.
        """
        rowcap = 0
        for u in range(self.n):
            count = 0
            for i in range(self.m):
                count += int(self.B[u][i])
            if count >= rowcap:
                rowcap = count
        return rowcap
    
    
class SPDZTest(Test):
    """
    This class builds an SPDZ test when called in an MPC Program. Do not use it in pure Python.
    """
    
    def __init__(self, id, IO):
        """
        Create a new Test instance.
        
        id: unique identifier for the timer objects.
        IO: gen_input_fp connector, which should be used for private input.
        """
        Test.__init__(self, id)
        self.IO = IO

    
    def _prep_private_plain_input(self):
        """
        Prepare the private input of the dataset for a plain representation.
        (Compile time)
        """
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
        """
        Compiles to bytecode that loads a plain rating matrix.
        """
        #########################
        # Reading Private Input
        #########################
        
        start_timer(self.id*10+1)

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
        stop_timer(self.id*10+1)
        
        
    def _prep_private_sparse_input(self, cap):
        """
        Prepare the private input of the dataset for a sparse representation.
        (Compile time)
        """
        
        print("Preparing sparse rating input.")
        for u in range(self.n):
            input=[]
            tailpointer = 0
            for i in range(self.m):
                if self.B[u][i] != 0:
                    r = int((self.R[u][i]*(2**sfix.f)))
                    r2 = int(((self.R[u][i]**2)*(2**sfix.f)))
                    input += [i,r,r2]
                    tailpointer += 1;
                    if tailpointer >= cap:
                        print("Tailpointer exceeds capacity: {} > {}!".format(tailpointer, cap))
                        break;
            
            for _ in range(tailpointer, cap):
                input += [-1,0,0] # Padding
            input += [tailpointer]
            self.IO.append_fp_array(input)
            
    def _private_sparse_input(self):
        """
        Compiles to bytecode that loads a sparse rating matrix.
        """
        
        start_timer(self.id*10+1)

        print_ln("Loading private sparse input.")
        @for_range(self.n)
        def user_loop1(u):
            self.CF.load_ratings_from(u, 0)
        stop_timer(self.id*10+1)
        
    def buildUBplain(self):
        """
        Compiles to bytecode that reads a plain rating matrix and and builds a user-based similarity model.
        """
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
        start_timer(self.id*10+2)
        self.CF.build_model()
        stop_timer(self.id*10+2)

    def buildUBsparse(self, cap):
        """
        Compiles to bytecode that reads a sparse rating matrix and and builds a user-based similarity model.
        """
        print_ln("############################\nNEW TEST RUN")
        print_ln("Sparse User-based CF")
        print_ln("n = %s\nm = %s, cap = %s", self.n, self.m, cap)
        print_ln("")
        
        self.CF = SparseUBCosineCF(self.n,self.m, cap)
        
        self._prep_private_sparse_input(cap)
        self._private_sparse_input()
        
        #########################
        # Building Model
        #########################
        start_timer(self.id*10+2)
        self.CF.build_model()
        stop_timer(self.id*10+2)
    
    def buildIBplain(self):  
        """
        Compiles to bytecode that reads a plain rating matrix and and builds an item-based similarity model.
        """
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
        start_timer(self.id*10+2)
        self.CF.build_model()
        stop_timer(self.id*10+2)

    def testPredictions(self, knn_params, sampsize): 
        """
        Compiles to bytecode to evaluate the accuracy.
        Samples a specified number of ratings.
        For each knn-parameter combination sampsize predictions are made. Then it computes the MAE and RMSE.
        
        sampsize: sampling size, e.g. 5000
        knn_params: array of parameter pairs (k,f') , e.g.
        [(5,14), (6,14)]
        """
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
                prediction = self.CF.nn_prediction(u,i, k, f) + cfix(self.mean[u])
                if isinstance(prediction, sfix):
                    prediction = prediction.reveal()
                error = prediction - cfix(r)
                error = cint(error>=0).if_else(error, -error)
                mae += error
                rmse += (error)**2
            
            mae = mae / sampsize
            rmse = (rmse / sampsize).sqrt()
            
            print_ln("%s   %s   %s %s",k, f, mae, rmse)
            stop_timer(self.id*100+timer_count)
            timer_count += 1
        
    def debugPredictions(self, k, f):
        """
        Prints the first 10x10 predictions out for debugging purposes.
        """
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
    """
    This class tests the baseline implementation. Do not call it from MPC, neither compile it with SPDZ.
    """
    def buildUBbaseline(self):
        """
        Builds a user-based similarity model and measures the time.
        """
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
        """
        Builds an item-based similarity model and measures the time.
        """
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
        """
        Evaluate the accuracy of the baseline
        Samples a specified number of ratings.
        For each knn-parameter combination sampsize predictions are made. Then it computes the MAE and RMSE.
        
        sampsize: sampling size, e.g. 5000
        knn_params: array of parameter pairs (k,f') , e.g.
        [(5,14), (6,14)]
        """
        
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        
        print "PREDICTIONS"
        print "{:4} {:4}  {:8} {:8} {:8} {:8}".format("k","f", "mae", "rmse", "var", "tpred")
        
        for (k, f) in knn_params:
            stats = []
            start_time = time.clock()
            mae = 0
            rmse = 0
            
            sampling = random.sample(self.Rlist,sampsize)
            
            for (u,i,r) in sampling:
                    prediction = self.CF.nn_prediction(u,i, k, f)
                    error = abs(prediction + self.mean[u] - r)
                    mae += error
                    rmse += (error)**2
                    stats.append(error)
            
            mae = mae / sampsize
            rmse = sqrt(rmse / sampsize)
            end_time = time.clock()
            tpred = end_time-start_time
            from numpy import var
            v = var(stats)
            print "{:<4d} {:<4d}  {:8.6f} {:8.6f} {:8.6f} {:8.4f}".format(k,f, mae, rmse, v, tpred)

    def debugPredictions(self, k, f):
        """
        Prints the first 10x10 predictions out for debugging purposes.
        """
        if self.CF == None:
            raise RuntimeError("Call another test to build model first!")
        print "PREDICTIONS"
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                prediction = self.CF.nn_prediction(u,i, k, f)
                prediction += self.mean[u]
                print "{: 1.5f}".format(prediction),
            print ' '
            
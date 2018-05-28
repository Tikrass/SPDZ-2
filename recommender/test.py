from recommender import *
from Compiler.types import sfix
from Compiler.library import *

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
    
    def prep_private_plain_input(self, IO):
        #########################
        # Preparing Private Input
        #########################
        print("Preparing rating input.")
        for u in range(self.n):
            IO.append_fp_array([int(r* (2**sfix.f)) for r in self.R[u]])
        
        print("Preparing rating2 input.")
        for u in range(self.n):
            IO.append_fp_array([int((r**2)* (2**sfix.f)) for r in self.R[u]])
            
        print("Preparing bitrating input.")
        for u in range(self.n):
            IO.append_fp_array(self.B[u])
    
    def private_plain_input(self, CF):
        #########################
        # Reading Private Input
        #########################
        
        start_timer(self.id+1)

        print_ln("Loading private input.")
        @for_range(self.n)
        def user_loop1(u):
            CF.load_ratings_from(u, 0)
            
        @for_range(self.n)
        def user_loop2(u):
            CF.load_ratings2_from(u, 0)

        @for_range(self.n)
        def user_loop3(u):
            CF.load_bitratings_from(u, 0)
        stop_timer(self.id+1)
        
        
    def prep_private_sparse_input(self, IO):
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
            
    def private_plain_input(self, CF):
        #########################
        # Reading Private Input
        #########################
        
        start_timer(self.id+1)

        print_ln("Loading private sparse input.")
        @for_range(self.n)
        def user_loop1(u):
            CF.load_ratings_from(u, 0)
        stop_timer(self.id+1)
            
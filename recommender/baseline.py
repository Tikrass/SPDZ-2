# (C) 2018 Thibaud Kehler.
# MIT Licence
# see https://opensource.org/licenses/MIT

from math import sqrt, isnan

class BaselineUBCF(object):
    """
    User-based collaborative filter with cosine similarity model.     
    
    :param n: number of users :math:`n`
    :type n: int
    :param m: number of items :math:`m`
    :type m: int
    :param ratings: :math:`n` times :math:`m` matrix with the rating values :math:`r_{ui}`
    :type ratings: list of lists
    :param bitratings: :math:`n` times :math:`m`  matrix of boolean values :math:`b_{ui}`.
    :type bitratings: list of lists
    """
    def __init__(self, n, m, ratings, bitratings):
        """
        Constructor
        """
        self.S = [[0 for _ in range(n)] for _ in range(n)] # Similarity model
        self.n = n # Number of users
        self.m = m # Number of items
        self.R = ratings # Rating matrix
        self.B = bitratings # Boolean ratings
    
    def build_model(self):
        """
        Builds the user-similarity model.
        
        Call this method before any prediction method.
        """
        for u in range(self.n):
            for v in range(u,self.n):
                s_uv = self.cosine(u,v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
                print "{:5d} to {:5d}\r".format(u,v),
            
    def print_model(self):
        """
        Prints the first 10 times 10 similarity values :math:`s_{uv}` to console.
        """
        print "S"
        for u in range(min(self.n,10)):
            for v in range(min(self.n,10)):
                print "{: 1.5f}".format(self.S[u][v]),
            print ""
        
                
    def print_ratings(self):
        """
        Prints the first 10 times 10 rating values :math:`r_{ui}`, :math:`r^2_{ui}` and :math:`b_{ui}` to console.
        """
        print "R"
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.R[u][i]),
            print ""
        
        print "R2"    
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.R[u][i]**2),
            print ""
        
        print "B"    
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.B[u][i]),
            print ""
                
    def cosine(self, u,v):
        """        
        :param u: one user :math:`u`
        :param v: another user :math:`v`
        
        Returns the cosine similarity  :math:`s_{uv}`.
        """
        d = 0
        su = 0
        sv = 0
        for i in range(self.m):
            d += self.R[u][i] * self.R[v][i]
            su += self.R[u][i]**2 * self.B[v][i]
            sv += self.R[v][i]**2 * self.B[u][i]
        if d == 0:
            return 0
        else :
            return  d / (sqrt(su) * sqrt(sv))
        
    def nn_prediction_sort(self,u,i,k):
        """
        Predicts the rating :math:`\hat{r}_{ui}` with k-nearest neighbour approach. 
        
        Algorithm uses sorting to obtain k-NN.
        
        :param u: target user :math:`u`
        :param i: target item :math:`i`
        :param k: parameter for :math:`k`-nearest neighbour algorithm

        Returns the prediction :math:`\hat{r}_{ui}`.
        """
        # Find K best peers
        
        # Remove all users who have not rated the target item
        candidates = []
        for v in range(self.n):
            if v == u: # skip target user
                continue
            if self.B[v][i] == 1:
                candidates.append(v)
        
        peers = []
        def find_minpeer(peers):
            min_peer = peers[0]
            for v in peers:
                if self.S[u][v] < self.S[u][min_peer]:
                    min_peer = v
            return min_peer
        
        for v in candidates:
            if len(peers) < k:
                peers.append(v)
                min_peer = find_minpeer(peers)
            
            if self.S[u][v] < self.S[u][min_peer]:
                peers.remove(min_peer)
                peers.append(v)
                min_peer = find_minpeer(peers)
        #print peers
        rating = 0
        norm = 0
        for v in peers:
            if self.S[u][v] >= 0:
                rating += self.R[v][i] * self.S[u][v]
                norm += self.S[u][v]
            #print "r: {}, n: {}".format(rating, norm)
        if norm == 0:
            return 0
        return rating / norm
    
    def nn_prediction_bs(self,u,i,k,f):
        """
        Predicts the rating :math:`\hat{r}_{ui}` with k-nearest neighbour approach. 
        
        Algorithm uses binary search of precision :math:`f\,'` to obtain k-NN.
        
        :param u: target user :math:`u`
        :param i: target item :math:`i`
        :param k: parameter for :math:`k`-nearest neighbour algorithm
        :param f: precision of the binary search :math:`f\,'`

        Returns the prediction :math:`\hat{r}_{ui}`.  
        """
        epsilon = 2**(-1)
       
        for e in range(2, f):
            c = 0
            for v in range(self.n):
                if u != v and self.S[u][v] >= epsilon:
                    c += self.B[v][i]
            delta = 2**(-e)
            if c > k:
                epsilon += delta
            if c < k:
                epsilon -= delta
        
        r = 0
        n = 0 
        for v in range(self.n):
            if u != v and self.S[u][v] >= epsilon and self.B[v][i] == 1:
                r += self.S[u][v] * self.R[v][i]
                n += self.S[u][v]
                
        if n == 0:
            return 0
        else :
            return r / n
        
        
    # Use approx knn per default 
    nn_prediction=nn_prediction_bs            
        
            


class BaselineIBCF(object):
    """
    Item-based collaborative filter with cosine similarity model.     
    
    :param n: number of users :math:`n`
    :type n: int
    :param m: number of items :math:`m`
    :type m: int
    :param ratings: :math:`n` times :math:`m` matrix with the rating values :math:`r_{ui}`
    :type ratings: list of lists
    :param bitratings: :math:`n` times :math:`m`  matrix of boolean values :math:`b_{ui}`.
    :type bitratings: list of lists
    """
    def __init__(self, n, m, ratings, bitratings):
        self.S = [[0 for _ in range(m)] for _ in range(m)] # Similarity model
        self.n = n # Number of users
        self.m = m # Number of items
        self.R = ratings # Rating matrix
        self.B = bitratings # Boolean ratings
    
    def build_model(self):
        """
        Builds the user-similarity model.
        
        Call this method before any prediction method.
        """
        for i in range(self.m):
            for j in range(i,self.m):
                s_ij = self.cosine(i,j)
                self.S[i][j] = s_ij
                self.S[j][i] = s_ij
                print "{:5d} to {:5d}\r".format(i,j),
            
    def print_model(self):
        """
        Prints the first 10 times 10 similarity values :math:`s_{uv}` to console.
        """
        print "S"
        for i in range(min(self.m,10)):
            for j in range(min(self.m,10)):
                print "{: 1.5f}".format(self.S[i][j]),
            print ""
                
    def print_ratings(self):
        """
        Prints the first 10 times 10 rating values :math:`r_{ui}`, :math:`r^2_{ui}` and :math:`b_{ui}` to console.
        """
        print "R"
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.R[u][i]),
            print ""
        
        print "R2"    
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.R[u][i]**2),
            print ""
        
        print "B"    
        for u in range(min(self.n,10)):
            for i in range(min(self.m,10)):
                print "{: 1.5f}".format(self.B[u][i]),
            print ""
                
    def cosine(self, i,j):
        """        
        :param u: one user :math:`u`
        :param v: another user :math:`v`
        
        Returns the cosine similarity  :math:`s_{uv}`.
        """
        d = 0
        si = 0
        sj = 0
        for u in range(self.n):
            d += self.R[u][i] * self.R[u][j]
            si += self.R[u][i]**2 * self.B[u][j]
            sj += self.R[u][j]**2 * self.B[u][i]
        if d == 0:
            return 0
        else :
            return  d / (sqrt(si) * sqrt(sj))
    
    def nn_prediction_sort(self,u,i,k):
        """
        Predicts the rating :math:`\hat{r}_{ui}` with k-nearest neighbour approach. 
        
        Algorithm uses sorting to obtain k-NN.
        
        :param u: target user :math:`u`
        :param i: target item :math:`i`
        :param k: parameter for :math:`k`-nearest neighbour algorithm

        Returns the prediction :math:`\hat{r}_{ui}`.
        """
        # Find K best peers
        
        # Remove all users who have not rated the target item
        candidates = []
        for j in range(self.m):
            if j == i: # skip target user
                continue
            if self.B[u][j] == 1:
                candidates.append(j)
        
        peers = []
        def find_minpeer(peers):
            min_peer = peers[0]
            for j in peers:
                if self.S[i][j] < self.S[i][min_peer]:
                    min_peer = j
            return min_peer
        
        for j in candidates:
            if len(peers) < k:
                peers.append(j)
                min_peer = find_minpeer(peers)
            
            if self.S[i][j] < self.S[i][min_peer]:
                peers.remove(min_peer)
                peers.append(j)
                min_peer = find_minpeer(peers)
        #print peers
        rating = 0
        norm = 0
        for j in peers:
            if self.S[i][j] >= 0:
                rating += self.R[u][j] * self.S[i][j]
                norm += self.S[i][j]
            #print "r: {}, n: {}".format(rating, norm)
        if norm == 0:
            return 0
        return rating / norm
    
    def nn_prediction_bs(self,u,i,k,f):
        """
        Predicts the rating :math:`\hat{r}_{ui}` with k-nearest neighbour approach. 
        
        Algorithm uses binary search of precision :math:`f\,'` to obtain k-NN.
        
        :param u: target user :math:`u`
        :param i: target item :math:`i`
        :param k: parameter for :math:`k`-nearest neighbour algorithm
        :param f: precision of the binary search :math:`f\,'`

        Returns the prediction :math:`\hat{r}_{ui}`.  
        """
        epsilon = 2**(-1)
       
        for e in range(2, f):
            c = 0
            for j in range(self.m):
                if i != j and self.S[i][j] >= epsilon:
                    c += self.B[u][j]
            delta = 2**(-e)
            if c > k:
                epsilon += delta
            if c < k:
                epsilon -= delta
        
        r = 0
        n = 0 
        for j in range(self.m):
            if i != j and self.S[i][j] >= epsilon and self.B[u][j] == 1:
                r += self.S[i][j] * self.R[u][j]
                n += self.S[i][j]
                
        if n == 0:
            return 0
        else :
            return r / n
        
        
    # Use approx knn per default 
    nn_prediction=nn_prediction_bs  
    
    
    

from math import sqrt, isnan

class UBCF(object):
    def __init__(self, n, m, ratings, bitratings):
        self.S = [[0 for _ in range(n)] for _ in range(n)] # Similarity model
        self.n = n # Number of users
        self.m = n # Number of items
        self.R = ratings # Rating matrix
        self.B = bitratings # Boolean ratings
    
    def build_model(self):
        for u in range(self.n):
            for v in range(u,self.n):
                s_uv = self.cosine(u,v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
            
    def print_model(self):
            for u in range(self.n):
                for v in range(self.n):
                    print self.S[u][v],
                print ""
                
    def cosine(self, u,v):
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
            


class IBCF(object):
    def __init__(self, n, m, ratings, bitratings):
        self.S = [[0 for _ in range(m)] for _ in range(m)] # Similarity model
        self.n = n # Number of users
        self.m = n # Number of items
        self.R = ratings # Rating matrix
        self.B = bitratings # Boolean ratings
    
    def build_model(self):
        for i in range(self.m):
            for j in range(i,self.m):
                s_ij = self.cosine(i,j)
                self.S[i][j] = s_ij
                self.S[j][i] = s_ij
            
    def print_model(self):
            for i in range(self.m):
                for j in range(self.m):
                    print self.S[i][j],
                print ""
                
    def cosine(self, i,j):
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
    
    
    
    

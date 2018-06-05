from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *
from config_mine import *
        
class UBCosineCF():
    
    def __init__(self, n, m):
        self.S = sfixMatrix(n,n) # Similarity model
        self.n = n # Number of users
        self.m = m # Number of items
        self.R = sfixMatrix(n,m) # Rating matrix
        self.R2 = sfixMatrix(n,m) # Squared rating matrix
        self.B = Matrix(n,m,sint) # Boolean ratings                
            
    def load_ratings_from(self, user, player):
        ratings = self.R[user]
        @for_range(self.m)
        def items_loop1(i):
            r = sint.get_raw_input_from(player)
            ratings[i] = sfix(*r)
            
    def load_ratings2_from(self, user, player):
        ratings2 = self.R2[user]
        @for_range(self.m)
        def items_loop(i):
            r2 = sint.get_raw_input_from(player)
            ratings2[i] = sfix(*r2)
        
    def load_bitratings_from(self, user, player):
        bitratings = self.B[user]
        @for_range(self.m)
        def items_loop2(i):
            bitratings[i] = sint.get_raw_input_from(player)
            
    def print_ratings(self):
        """
        Only for debugging
        """
        print_ln("R")
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.R[u][i].reveal())
            print_ln(' ')
        
        print_ln("R2")    
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.R2[u][i].reveal())
            print_ln(' ')
        
        print_ln("B")    
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.B[u][i].reveal())
            print_ln(' ')
    
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.n)
        def users_loop1(u):
            self.S[u][u] = sfix(1)
            @for_range(u+1,self.n)
            def users_loop2(v):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("%s to %s     \r", u,v)
                s_uv = self.cosine(u, v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
            
    @method_block
    def cosine(self, u,v):
        d = MemValue(sint(0))
        su = MemValue(sint(0))
        sv = MemValue(sint(0))
        @for_range(self.m)
        def item_loop(i):
            d.write(d.read() + self.R[u][i].conv() * self.R[v][i].conv())
            su.write(su.read() + self.R2[u][i].conv() * self.B[v][i])
            sv.write(sv.read() + self.R2[v][i].conv() * self.B[u][i])
        
        # Truncate only once
        d = sfix(TruncPr(d.read(), 2 * sfix.k, sfix.f, sfix.kappa))
        norm = sfix(su.read()).sqrt() * sfix(sv.read()).sqrt()
        
        not_zero = sint(norm != 0)
        cos = not_zero.if_else(d/norm, sfix(0))             
        return cos
    
    def print_model(self):
        """
        Only for debugging
        """
        print_ln("S")
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.n,10))
            def user_loop(v):
                print_str('%s ', self.S[u][v].reveal())
            print_ln(' ')
            
    @method_block
    def threshold_prediction(self, u, i, epsilon):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", u, i)
        
        r = MemValue(sint(0))
        n = MemValue(sint(0))
        
        @for_range(self.n)
        def user_loop(v):
            if_then(u != v)
            c = sint(self.S[u][v] >= epsilon) * self.B[v][i]
            r.write(r.read() + c * self.S[u][v].conv() * self.R[v][i].conv() )
            n.write(n.read() + c * self.S[u][v].conv())
            end_if()
        
        r = sfix(TruncPr(r.read(), 2 * sfix.k, sfix.f, sfix.kappa))
        n = sfix(n.read())

        prediction = sint(n != 0).if_else(r / n, sfix(0))  
        return prediction 
    
    @method_block
    def nn_prediction(self, u, i, k, f):
        epsilon = sfix.MemValue(sfix(sint(2**(sfix.f-1)))) # 0.5
        
        @for_range(2,f)
        def search_loop(round):
            c = sint.MemValue(sint(0))
            @for_range(self.n)
            def user_loop(v):
                if_then(u != v)
                c.write(c + (self.S[u][v] >= epsilon.read()) * self.B[v][i])
                end_if()
            delta = cfix(cint(2**(sfix.f-(round))))
            epsilon.write( epsilon.read() + (c > k) * delta)
            epsilon.write( epsilon.read() - (c < k) * delta)
            
        return self.threshold_prediction(u, i, epsilon.read())
            
    def delete(self):
        self.S.delete()
        self.R.delete()
        self.R2.delete()
        self.B.delete()

class SparseUBCosineCF():
    def __init__(self, n, m, capacity):
        self.S = sfixMatrix(n,n) # Similarity model
        self.n = n # Number of users
        self.m = m # Number of items
        self.capacity = capacity
        self.R = sfixSparseRowMatrix(n,m,capacity) # Rating matrix  
        
    def load_ratings_from(self, user, player):
        sfixSparseArray.get_raw_input_from(player, self.n, self.capacity, address=self.R[user].address)
    
    def print_ratings(self):
        """
        Only for debugging
        """
        print_ln("R")
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.R[u].get_rating(i).reveal())
            print_ln(' ')
        
        print_ln("R2")    
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                _, r2 = self.R[u].get_pair(i)
                print_str('%s ', r2.reveal())
            print_ln(' ')
    
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.n)
        def users_loop1(u):
            self.S[u][u] = sfix(1.0)
            @for_range(u+1,self.n)
            def users_loop2(v):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("%s to %s     \r", u,v)
                s_uv = self.cosine(u, v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
    
    
    @method_block
    def cosine(self, u,v):
        d = MemValue(sint(0))
        su = MemValue(sint(0))
        sv = MemValue(sint(0))
        @for_range(self.capacity)
        def item_loop(k):
            @for_range(self.capacity)
            def item_loop(l):
                c = self.R[u]._getkey(k) == self.R[v]._getkey(l)
                d.write(d.read() + c * self.R[u]._getr(k).conv() * self.R[v]._getr(l).conv())
                su.write(su.read() + c * self.R[u]._getr2(k).conv())
                sv.write(sv.read() + c * self.R[v]._getr2(l).conv())
        
        # Truncate only once
        d = sfix(TruncPr(d.read(), 2 * sfix.k, sfix.f, sfix.kappa))
        norm = sfix(su.read()).sqrt() * sfix(sv.read()).sqrt()
        
        not_zero = sint(norm != 0)
        cos = not_zero.if_else(d/norm, sfix(0))             
        return cos    
    
    
    def print_model(self):
        """
        Only for debugging
        """
        print_ln("S")
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.n,10))
            def user_loop(v):
                print_str('%s ', self.S[u][v].reveal())
            print_ln(' ')
            
    def delete(self):
        self.S.delete()
        self.R.delete()

class IBCosineCF(object):
    def __init__(self, n, m):
        self.S = cfixMatrix(m,m) # Similarity model
        self.R = sfixMatrix(n,m)
        self.R2 = sfixMatrix(n,m)
        self.B = Matrix(n,m,sint)
        self.n = n # Number of users
        self.m = m # Number of items

        
    def load_ratings_from(self, user, player):
        ratings = self.R[user]
        @for_range(self.m)
        def items_loop(i):
            r = sint.get_raw_input_from(player)
            ratings[i] = sfix(*r)
            
    def load_ratings2_from(self, user, player):
        ratings2 = self.R2[user]
        @for_range(self.m)
        def items_loop(i):
            r2 = sint.get_raw_input_from(player)
            ratings2[i] = sfix(*r2)
        
    def load_bitratings_from(self, user, player):
        bitratings = self.B[user]
        @for_range(self.m)
        def items_loop2(i):
            bitratings[i] = sint.get_raw_input_from(player)
            
    def print_ratings(self):
        """
        Only for debugging
        """
        print_ln("R")
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.R[u][i].reveal())
            print_ln(' ')
        
        print_ln("R2")    
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.R2[u][i].reveal())
            print_ln(' ')
        
        print_ln("B")    
        @for_range(min(self.n,10))
        def user_loop(u):
            @for_range(min(self.m,10))
            def user_loop(i):
                print_str('%s ', self.B[u][i].reveal())
            print_ln(' ')
        
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.m)
        def item_loop1(i):
            self.S[i][i] = cfix(1.0)
            @for_range(i+1,self.m)
            def item_loop2(j):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("%s to %s     \r", i,j)
                s_ij = self.cosine(i,j)
                self.S[i][j] = s_ij
                self.S[j][i] = s_ij
            
    @method_block
    def cosine(self, i,j):
        d = MemValue(sint(0))
        si = MemValue(sint(0))
        sj = MemValue(sint(0))
        @for_range(self.n)
        def item_loop(u):
            d.write(d.read() + self.R[u][i].conv() * self.R[u][j].conv())
            si.write(si.read() + self.R2[u][i].conv() * self.B[u][j])
            sj.write(sj.read() + self.R2[u][j].conv() * self.B[u][i])
        
        # Truncate only once
        d = sfix(TruncPr(d.read(), 2 * sfix.k, sfix.f, sfix.kappa))
        norm = sfix(si.read()).sqrt() * sfix(sj.read()).sqrt()
        
        not_zero = sint(norm != 0)
        cos = not_zero.if_else(d/norm, sfix(0))             
        return cos.reveal()
            
    def print_model(self):
        """
        Only for debugging
        """
        print_ln("S")
        @for_range(min(self.m, 10))
        def item_loop(i):
            @for_range(min(self.m,10))
            def item_loop(j):
                print_str('%s ', self.S[i][j])
            print_ln(' ')
            
    
    
    
    @method_block
    def threshold_prediction(self, u, i, epsilon):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", u, j)
        
        rating = cfix.MemValue(cfix(0))
        norm = cfix.MemValue(cfix(0))
        
        @for_range(self.m)
        def item_loop(j):
            if_then(i != j)
            c = (self.S[i][j] >= epsilon) * self.B[u][j].reveal()
            if_then(c)
            rating.write(rating.read() + self.S[i][j] * self.R[u][j].reveal() )
            norm.write(norm.read() + self.S[i][j])
            end_if()
            end_if()
        if_then(norm.read() != 0)
        prediction = rating.read() / norm.read()  
        else_then()
        prediction = cfix(0)
        end_if()
        return prediction
    
    @method_block
    def nn_prediction(self, u, i, k, f):
        epsilon = cfix.MemValue(cfix(cint(2**(cfix.f-1)))) # 0.5
        
        @for_range(2,f)
        def search_loop(round):
            c = cint.MemValue(cint(0))
            @for_range(self.m)
            def user_loop(j):
                if_then(i != j)
                c.write(c + cint(self.S[i][j] >= epsilon.read()) * self.B[u][j].reveal())
                end_if()
            delta = cfix(cint(2**(cfix.f-(round))))
            epsilon.write( epsilon.read() + cint(c > k) * delta)
            epsilon.write( epsilon.read() - cint(c < k) * delta)
        return self.threshold_prediction(u, i, epsilon.read())
        
    
    def delete(self):
        self.S.delete()
        self.R.delete()
        self.R2.delete()
        self.B.delete()
        
    

    
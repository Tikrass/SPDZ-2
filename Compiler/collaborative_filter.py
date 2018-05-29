from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *
from config_mine import *
        
class UserBasedModel(object):
    def __init__(self, n, m, ratings, bitratings):
        self.S = sfixMatrix(n,n) # Similarity model
        self.n = n # Number of users
        self.m = m # Number of items
        self.R = ratings # Rating matrix
        self.B = bitratings # Boolean ratings
    
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.n)
        def users_loop1(u):
            @for_range(u,self.n)
            def users_loop2(v):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("%s to %s     \r", u,v)
                s_uv = self.cosine(u, v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
            
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
    
    @method_block
    def threshold_prediction(self, u, i, epsilon):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", u, i)
        
        r = sfix.MemValue(0)
        n = sfix.MemValue(0)
        
        @for_range(self.n)
        def user_loop(v):
            if_then(u != v)
            c = (self.S[u][v] >= epsilon) * self.B[v][i]
            r.write(r + c * self.S[u][v] * self.R[v][i] )
            n.write(n + c * self.S[u][v])
            end_if()
        
        return r.read() / n.read()   
    
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
            #print_ln("e: %s, d: %s, c:%s", epsilon.read(), delta.read(), c)
        return self.threshold_prediction(u, i, epsilon.read())
        
    
    def delete(self):
        self.S.delete()
        self.R.delete()
        self.B.delete()

class UBCosineCF(UserBasedModel):
    
    def __init__(self, n, m):
        self.R2 = sfixMatrix(n,m)
        UserBasedModel.__init__(self, n, m, sfixMatrix(n,m), Matrix(n,m,sint))
            
            
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
            
    
    @method_block
    def cosine(self, u,v):
        d = sfix.MemValue(0)
        su = sfix.MemValue(0)
        sv = sfix.MemValue(0)
        @for_range(self.m)
        def item_loop(i):
            d.write(d.read() + self.R[u][i] * self.R[v][i])
            su.write(su.read() + self.R2[u][i] * self.B[v][i])
            sv.write(sv.read() + self.R2[v][i] * self.B[u][i])
        
        cos = d.read()/(su.read() * sv.read()).sqrt() 
        
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", d.reveal())
            print_ln("sumu: %s, sumv: %s", su.reveal(), sv.reveal())
            print_ln("cos: %s", d.reveal())
            print_ln(" ")
            
        return cos
            
    def delete(self):
        self.R2.delete()
        UserBasedModel.delete(self)

class SparseUBCosineCF(UBCosineCF):
    def __init__(self, n, m, capacity):
        self.capacity = capacity
        UserBasedModel.__init__(self, n, m, sfixSparseRowMatrix(n, m), None)
        
    def load_ratings_from(self, user, player):
        sfixSparseArray.get_raw_input_from(player, self.n, self.capacity, address=self.R[u].address)
        
    @method_block
    def cosine_sim(self,a_ptr, norma, b_ptr, normb):
        a = sfixSparseArray(self.nitems,self.capacity,a_ptr)
        b = sfixSparseArray(self.nitems,self.capacity,b_ptr)
        return self._cosine_sim(a,norma,b,normb)
    
    @classmethod
    def _dot_product(self, a, b):
        dot = sfix.MemValue(0)
        pa = MemValue(cint(0))
        pb = MemValue(cint(0))
        if DEBUG >= INTERMEDIATE_FULL:
            print_ln("selfcap: %s, othercap: %s", a.capacity, b.capacity)
        @do_while
        def product_loop():
            ka = a._getkey(pa.read())
            kb = b._getkey(pb.read())
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("pself: %s, pother: %s", pa.read(), pb.read())
            cond = (ka == kb).reveal()
            if_then(cond)
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("case 1: kself %s == kother %s", ka.reveal(), kb.reveal())
                print_ln("%s + %s * %s = %s",
                         dot.reveal(),
                         self._getval(pa.read()).reveal(),
                         other._getval(pb.read()).reveal(),
                         (dot.read() + a._getval(pa.read()) * b._getval(pb.read())).reveal()  
                         )
            dot.write(dot.read() + a._getval(pa.read()) * b._getval(pb.read()))
            pa.write(pa+1)
            pb.write(pb+1)
            end_if()
           
            cond = (ka<kb).reveal()
            if_then(cond)
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("case 2: ka %s < kb %s", ka.reveal(), kb.reveal())
            pa.write(pa+1)
            end_if()
            
            cond = (ka > kb).reveal()
            if_then(cond)
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("case 3: ka %s > kb %s", ka.reveal(), kb.reveal())
            pb.write(pb+1)
            end_if()
            
            #abort = (ka == sint(0) and kb == sint(0)).reveal()
            cond = (pa.read() < a.capacity) * (pb.read() < b.capacity)
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("dot: %s", dot.reveal())
                print_ln("Loop-Condition: %s < %s and %s < %s -> %s", pa.read(), a.capacity, pb.read(), b.capacity,  cond)
                print_ln(" ")
            return cond
        
        #res = dot.read()
        #dot.delete()
        #pa.delete()
        #pb.delete()
        return dot.read()

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
        
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.m)
        def item_loop1(i):
            @for_range(i,self.m)
            def item_loop2(j):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("\r%s to %s     ", i,j)
                s_ij = self.cosine(i,j)
                self.S[i][j] = s_ij
                self.S[j][i] = s_ij
        if DEBUG >= VERBOSE_PROGRESS:
            print_str("\r")
            
            
    @method_block
    def cosine(self,i,j):
        dot = sfix.MemValue(0)
        sumi = sfix.MemValue(0)
        sumj = sfix.MemValue(0)
        @for_range(self.n)
        def item_loop(u):
            dot.write(dot.read() + self.R[u][i] * self.R[u][j])
            sumi.write(sumi.read() + self.R2[u][i] * self.B[u][j])
            sumj.write(sumj.read() + self.R2[u][j] * self.B[u][i])
        if_then(dot.reveal() == 0)
        cos = cfix(0)
        else_then()
        cos = dot.reveal()/(sumi.read() * sumj.read()).sqrt().reveal()
        end_if()
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", dot.reveal())
            print_ln("sumi: %s, sumj: %s", sumi.reveal(), sumj.reveal())
            print_ln("cos: %s", cos)
            print_ln(" ")
            
        return cos
            
    def print_model(self):
        """
        Only for debugging
        """
        @for_range(min(self.m, 10))
        def item_loop(i):
            @for_range(min(self.m,10))
            def item_loop(j):
                print_str('%s ', self.S[i][j])
            print_ln(' ')
            
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
            norm.write(norm + self.S[i][j])
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
            end_if()
        
        return rating.read() / norm.read()   
    
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
            #print_ln("e: %s, d: %s, c:%s", epsilon.read(), delta.read(), c)
        return self.threshold_prediction(u, i, epsilon.read())
        
    
    def delete(self):
        self.S.delete()
        self.R.delete()
        self.R2.delete()
        self.B.delete()
        
        
def OptimalCollaborativeFilter(nusers, nitems, capacity=None):
    raise CompilerError('Not implemented yet!')
    

    
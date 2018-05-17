from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *
        
class UserBasedModel(object):
    def __init__(self, n, m, ratings, bitratings):
        self.S = sfixMatrix(n,m) # Similarity model
        self.n = n # Number of users
        self.m = n # Number of items
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
                    print_str("\r%s to %s     ", u,v)
                s_uv = self._build_model(u, v)
                self.S[u][v] = s_uv
                self.S[v][u] = s_uv
        
        if DEBUG >= VERBOSE_PROGRESS:
            print_str("\r")
            
    def print_model(self):
            @for_range(self.n)
            def user_loop(u):
                @for_range(self.n)
                def user_loop(v):
                    print_str('%s ', self.S[u][v].reveal())
                print_ln(' ')
    
    @method_block
    def range_prediction(self, v, i, epsilon):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", v, i)
        
        r = sfix.MemValue(0)
        n = sfix.MemValue(0)
        
        @for_range(self.n)
        def user_loop(u):
            if_then(u != v)
            c = (self.S[u][v] >= epsilon) * self.B[u][v]
            r.write(r + c * self.S[u][v] * self.R[u][i] )
            n.write(n + c * self.S[u][v])
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
        
        return r.read() / n.read()   
    
    def count_range(self, v, i, epsilon):
        c = sint.MemValue(sint(0))
        @for_range(self.n)
        def user_loop(u):
            if_then(u != v)
            c.write(c + self.S[u][v] > epsilon * self.B[u][v])
            end_if()
        return c.read()
    
    @method_block
    def peer_prediction(self, v, i, k):
        epsilon = cfix.MemValue(cfix(0.5))
        delta = cfix.MemValue(cfix(0.25))
        @do_while
        def search_loop():
            c = self.count_range(v, i, epsilon.read()).reveal()
            if_then(c < k)
            epsilon.write(epsilon.read() - delta.read())
            end_if()
            if_then(c > k)
            epsilon.write(epsilon.read() + delta.read())
            end_if()
            delta.write(delta / 2)
            #print_ln("e: %s, d: %s, c:%s", epsilon.read(), delta.read(), c)
            return (c != k and delta != 0)
        return self.range_prediction(v, i, epsilon.read())
        

    predict_rating = lambda self, v,i : self.peer_prediction(v, i, 2)
        
    
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
    def cosine_sim(self, u,v):
        
        dot = sfix.MemValue(0)
        sumu = sfix.MemValue(0)
        sumv = sfix.MemValue(0)
        @for_range(self.m)
        def item_loop(i):
            dot.write(dot.read() + self.R[u][i] * self.R[v][i])
            sumu.write(sumu.read() + self.R2[u][i] * self.B[v][i])
            sumv.write(sumv.read() + self.R2[v][i] * self.B[u][i])
        
        cos = dot/(sumu.read() * sumv.read()).sqrt() 
        
        res = dot.read()
        #dot.delete()
        return res
    
    @classmethod
    def _cosine_sim(cls, a, norma, b, normb):
        dot = cls._dot_product(a,b)
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", dot.reveal())
            print_ln("sumu: %s, sumv: %s", sumu.reveal(), sumv.reveal())
            print_ln("cos: %s", cos.reveal())
            print_ln(" ")
            
        return cos
    
    _build_model = lambda self, u, v :  self.cosine_sim(u,v)
            
    def delete(self):
        self.R2.delete()
        UserBasedModel.delete(self)

class SparseUBCosineCF(UBCosineCF):
    def __init__(self, n, m, capacity):
        UserBasedModel.__init__(self, n, m, sfixSparseRowMatrix(n, m))
        
    def _load_ratings_from(self, player, ratings):
        sfixSparseArray.get_raw_input_from(player, self.nitems, self.capacity, address=ratings.address)
        
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
        self.S = cfixMatrix(n,m) # Similarity model
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
                s_ij = self._build_model(i,j)
                self.S[i][j] = s_ij
                self.S[j][i] = s_ij
        if DEBUG >= VERBOSE_PROGRESS:
            print_str("\r")
            
            
    @method_block
    def cosine_sim(self,i,j):
        dot = sfix.MemValue(0)
        sumi = sfix.MemValue(0)
        sumj = sfix.MemValue(0)
        @for_range(self.n)
        def item_loop(u):
            dot.write(dot.read() + self.R[u][i] * self.R[u][j])
            sumi.write(sumi.read() + self.R2[u][i] * self.B[u][j])
            sumj.write(sumj.read() + self.R2[u][j] * self.B[u][i])
        
        cos = dot.reveal()/(sumi.read() * sumj.read()).reveal().sqrt()
        
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", dot.reveal())
            print_ln("sumi: %s, sumj: %s", sumi.reveal(), sumj.reveal())
            print_ln("cos: %s", cos)
            print_ln(" ")
            
        return cos
    
    _build_model = lambda self, i, j :  self.cosine_sim(i,j)
            
    def print_model(self):
        @for_range(self.m)
        def item_loop(i):
            @for_range(self.m)
            def item_loop(j):
                print_str('%s ', self.S[i][j])
            print_ln(' ')
    
    
    @method_block
    def range_prediction(self, u, j, epsilon):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", u, j)
        
        rating = cfix.MemValue(cfix(0))
        norm = cfix.MemValue(cfix(0))
        
        @for_range(self.m)
        def item_loop(i):
            if_then(i != j)
            c = (self.S[i][j] >= epsilon) * self.B[u][i].reveal()
            if_then(c)
            rating.write(rating.read() + self.S[i][j] * self.R[u][i].reveal() )
            norm.write(norm + self.S[i][j])
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
            end_if()
        
        return rating.read() / norm.read()   
    
    @method_block
    def peer_prediction(self, user, item, k):
        pass

    predict_rating = lambda self, v,i : self.range_prediction(v, i, cfix(0.0))
        
    
    def delete(self):
        self.S.delete()
        self.R.delete()
        self.R2.delete()
        self.B.delete()
        
        
def OptimalCollaborativeFilter(nusers, nitems, capacity=None):
    raise CompilerError('Not implemented yet!')
    

    
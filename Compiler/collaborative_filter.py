from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *
# 0 no verbosity (secure)
# 1 compare final results
# 2 print dot-product and ratings
# 3 verbose dot-product calculation
DEBUG = 0

class AbstractCollaborativeFilter(object):
    
    def build_model(self):
        raise CompilerError('Not implemented yet!')
    
    def predict_rating(self, user, item):
        raise CompilerError('Not implemented yet!')
    
class ItemBasedCollaborativeFilter():
    def __init__(self):
        raise CompilerError('Not implemented yet!')
    
class UserBasedCollaborativeFilter():
    def __init__(self):
        raise CompilerError('Not implemented yet!')
    



class SparseIBCosineCollaborativeFilter(AbstractCollaborativeFilter):
    
    @classmethod
    def dot_product(cls, a, b):
        if a.capacity != b.capacity or a.length != b.length :
            raise CompileError("Size or Capacity does not match.")
        dot = sfix.MemValue(0)
        pa = MemValue(cint(0))
        pb = MemValue(cint(0))
        if DEBUG >= 3: 
            print_ln("selfcap: %s, othercap: %s", a.capacity, b.capacity)
        def product_loop():
            ka = a._getkey(pa.read())
            kb = b._getkey(pb.read())
            if DEBUG >= 3: 
                print_ln("pself: %s, pother: %s", pa.read(), pb.read())
            cond = (ka == kb).reveal()
            if_then(cond)
            if DEBUG >= 3: 
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
           
            
            #condition = ka < kb
            #pa.write(if_else(condition, val, res.read()))
            cond = (ka<kb).reveal()
            if_then(cond)
            if DEBUG >= 3: 
                print_ln("case 2: ka %s < kb %s", ka.reveal(), kb.reveal())
            pa.write(pa+1)
            end_if()
            
            cond = (ka > kb).reveal()
            if_then(cond)
            if DEBUG >= 3: 
                print_ln("case 3: ka %s > kb %s", ka.reveal(), kb.reveal())
            pb.write(pb+1)
            end_if()
            
            #abort = (ka == sint(0) and kb == sint(0)).reveal()
            cond = (pa.read() < a.capacity) * (pb.read() < b.capacity)
            if DEBUG >= 3: 
                print_ln("dot: %s", dot.reveal())
                print_ln("Loop-Condition: %s < %s and %s < %s -> %s", pa.read(), a.capacity, pb.read(), b.capacity,  cond)
                print_ln(" ")
            return cond
        do_while(product_loop)
        return dot.read()

    @classmethod
    def cosine_sim(cls, a, norma, b, normb):
        dot = cls.dot_product(a,b)
        if DEBUG >= 2:
            print_ln("dot: %s", dot.reveal())
        cos2 = (dot/norma)*(dot/normb) #square of cosine similarity: Take square root after revelation.
        if DEBUG >= 2:
            print_ln("cos2: %s", cos2.reveal())
            print_ln(" ")
        return cos2
    
    
    def __init__(self, nusers, nitems, capacity):
        self.nusers = nusers # Number of users
        self.nitems = nitems # Number of items
        self.capacity = capacity
        self.ratings = sfixSparseRowMatrix(nusers, nitems, capacity) # Rating matrix in sparse representation
        self.model = sfixMatrix(nusers,nusers) # Similarity model
        self.similarity = self.cosine_sim # Similarity measure
        self.norms = sfixArray(nusers)  # Normalization factors for the similarity measure.
    
    def load_raitings_from(self, user, player):
        ratings, tp = sfixSparseArray.get_raw_input_from(0, self.nitems, self.capacity, address=self.ratings[user].address)
        
    def load_normalization_from(self, user, player):
        norm = sint.get_raw_input_from(player)
        self.norms[user] = sfix(*norm)
    
    def set_normalization_factor(self, user, value):
        self.norms[user] = value
        
    def calc_normalization_factor(self, user):
        norm = sfix.MemValue(0)
        @for_range(self.nitems)
        def items_loop(i):
            norm += self.ratings[user][i]**2
        self.set_normalization_factor(user, norm)
    
    def calc_normalization_factors(self):
        @for_range(self.nusers)
        def users_loop(i):
            self.calc_normalization_factor(i)
    
    def build_model(self):
        library.print_ln("Computing shared Similarity Model.")
        @for_range(self.nusers)
        def users_loop1(i):
            @for_range(self.nusers)
            def users_loop2(j):
                ratings_j = self.ratings[j]
                self.model[i][j] = self.similarity(self.ratings[i], self.norms[i], self.ratings[j], self.norms[j])
    
    def predict_rating(self, user, item):
        raise CompilerError('Not implemented yet!')

    
def OptimalCollaborativeFilter(nusers, nitems, capacity=None):
    raise CompilerError('Not implemented yet!')
    

    
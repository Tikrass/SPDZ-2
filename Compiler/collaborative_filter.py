from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *

# 0 no verbosity (secure)
# 1 verbose progress (secure)
# 2 print intermediate results 
# 3 print more intermediate results
DEBUG = 1

class AbstractCollaborativeFilter(object):
    def __init__(self, nusers, nitems, ratings):
        self.nusers = nusers # Number of users
        self.nitems = nitems # Number of items
        self.ratings = ratings # Rating matrix
        
    def load_raitings_from(self, user, player):
        ratings = self.ratings[user]
        self._load_ratings_from(player, ratings)
            
    def delete(self):
        self.ratings.delete()
        
class UserBasedModel(object):
    def __init__(self, nusers, nitems):
        self.model = sfixMatrix(nusers,nusers) # Similarity model
    
    def build_model(self):
        if DEBUG >= 1:
            print_ln("Building secure shared similarity model")
        @for_range(self.nusers)
        def users_loop1(i):
            @for_range(i,self.nusers)
            def users_loop2(j):
                if DEBUG >= 1:
                    print_str("\r%s to %s     ", i,j)
                ratings_j = self.ratings[j]
                sim = self._build_model(i, j)
                self.model[i][j] = sim
                self.model[j][i] = sim
        
        if DEBUG >= 1:
            print_str("\r")
    
    @method_block
    def predict_rating_all(self, user, item):
        if DEBUG >= 1.5:
            print_ln("Predicting rating for user %s and item %s.", user, item)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nusers)
        def user_loop(i):
            similarity = self.model[user][i]
            rating_other = self.ratings[i][item]
            if_then(i != user)
            rating_sum.write(rating_sum + rating_other * similarity)
            normalization.write(normalization + similarity)
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
        prediction = rating_sum.read() / normalization.read()
        
        #rating_sum.delete()
        #normalization.delete()
        
        return prediction     
    
    @method_block
    def predict_rating_thresholded(self, user, item, t):
        if DEBUG >= 1.5:
            print_ln("Predicting rating for user %s and item %s.", user, item)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nusers)
        def user_loop(i):
            similarity = self.model[user][i]
            rating_other = self.ratings[i][item]
            if_then(i != user)
            condition = similarity >= t
            rating_sum.write(condition.if_else(
                    rating_sum + rating_other * similarity,
                    rating_sum.read()
                            ))
            normalization.write(condition.if_else(
                    normalization + similarity,
                    normalization.read()
                            ))
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
        prediction = rating_sum.read() / normalization.read()
        
        #rating_sum.delete()
        #normalization.delete()
        
        return prediction     
    
    @method_block
    def predict_rating_knn(self, user, item, k):
        pass
    
    predict_rating = predict_rating_all
        
    
    def delete(self):
        self.model.delete()
        
class ItemBasedModel(object):
    def __init__(self, nusers, nitems):
        self.model = cfixMatrix(nitems,nitems) # Similarity model
        
    def build_model(self):
        if DEBUG >= 1:
            print_ln("Building secure shared similarity model")
        @for_range(self.nitems)
        def item_loop1(i):
            @for_range(i,self.nitems)
            def item_loop2(j):
                if DEBUG >= 1:
                    print_str("\r%s to %s     ", i,j)
                ratings_j = self.ratings[j]
                sim = self._build_model(i, j)
                self.model[i][j] = sim
                self.model[j][i] = sim
        
        if DEBUG >= 1:
            print_str("\r")
    
    def predict_rating_all(self, user, item):
        pass

    def predict_rating_thresholded(self, user, item, t):
        pass
    
    def predict_rating_knn(self, user, item, k):
        pass
    
    predict_rating = predict_rating_all
        
    
    def delete(self):
        self.model.delete()

class UBCosineCF(UserBasedModel, AbstractCollaborativeFilter):
    
    def __init__(self, nusers, nitems):
        self.norms = sfixArray(nusers)  # Normalization factors for the similarity measure.
        UserBasedModel.__init__(self, nusers, nitems)
        AbstractCollaborativeFilter.__init__(self, nusers, nitems,sfixMatrix(nusers,nitems))
            
    def _load_ratings_from(self, player, ratings):
        @for_range(self.nitems)
        def items_loop(i):
            r = sint.get_raw_input_from(player)
            ratings[i] = sfix(*r)
            
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
    
    @classmethod
    def _dot_product(cls,a,b):
        dot = sfix.MemValue(0)
        @for_range(a.length)
        def product_loop(i):
            dot.write(dot.read() + a[i] * b[i])
        
        res = dot.read()
        #dot.delete()
        return res
    
    @classmethod
    def _cosine_sim(cls, a, norma, b, normb):
        dot = cls._dot_product(a,b)
        if DEBUG >= 2:
            print_ln("dot: %s", dot.reveal())
        cos2 = (dot/norma)*(dot/normb) #square of cosine similarity: Take square root after revelation.
        if DEBUG >= 2:
            print_ln("cos2: %s", cos2.reveal())
            print_ln(" ")
        return cos2
    
    @method_block
    def cosine_sim(self,a_ptr, norma, b_ptr, normb):
        a = sfixArray(self.nitems,a_ptr)
        b = sfixArray(self.nitems,b_ptr)
        return self._cosine_sim(a,norma,b,normb)
    
    _build_model = lambda self, i, j :  self.cosine_sim(self.ratings[i].address, self.norms[i], self.ratings[j].address, self.norms[j])
            
    def delete(self):
        self.norms.delete()
        AbstractCollaborativeFilter.delete(self)
        UserBasedModel.delete(self)

class SparseUBCosineCF(UBCosineCF, AbstractCollaborativeFilter):
    def __init__(self, nusers, nitems, capacity):
        self.norms = sfixArray(nusers)  # Normalization factors for the similarity measure.
        UserBasedModel.__init__(self, nusers, nitems)
        self.capacity = capacity
        AbstractCollaborativeFilter.__init__(self, nusers, nitems, sfixSparseRowMatrix(nusers, nitems, capacity))
        
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
        if DEBUG >= 3: 
            print_ln("selfcap: %s, othercap: %s", a.capacity, b.capacity)
        @do_while
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
        
        #res = dot.read()
        #dot.delete()
        #pa.delete()
        #pb.delete()
        return dot.read()
        

def OptimalCollaborativeFilter(nusers, nitems, capacity=None):
    raise CompilerError('Not implemented yet!')
    

    
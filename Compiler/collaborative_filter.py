from Compiler.types import *
from Compiler.library import *
from Compiler.sparse_types import *
from config_mine import *
        
class UserBasedModel(object):
    def __init__(self, nusers, nitems, ratings, bitratings):
        self.model = sfixMatrix(nusers,nusers) # Similarity model
        self.nusers = nusers # Number of users
        self.nitems = nitems # Number of items
        self.ratings = ratings # Rating matrix
        self.bitratings = bitratings
        
    def load_ratings_from(self, user, player):
        ratings = self.ratings[user]
        self._load_ratings_from(player, ratings)
        
    def load_bitratings_from(self, user, player):
        bitratings = self.bitratings[user]
        self._load_bitratings_from(player, bitratings)
        
    
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.nusers)
        def users_loop1(i):
            @for_range(i,self.nusers)
            def users_loop2(j):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("\r%s to %s     ", i,j)
                ratings_j = self.ratings[j]
                sim = self._build_model(i, j)
                self.model[i][j] = sim
                self.model[j][i] = sim
        
        if DEBUG >= VERBOSE_PROGRESS:
            print_str("\r")
            
    def print_model(self):
            @for_range(self.nusers)
            def user_loop(i):
                @for_range(self.nusers)
                def user_loop(j):
                    print_str('%s ', self.model[i][j].reveal())
                print_ln(' ')
    
    @method_block
    def predict_rating_all(self, user, item):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", user, item)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nusers)
        def user_loop(i):
            similarity = self.model[user][i]
            rating_other = self.ratings[i][item]
            bitrating_other = self.bitratings[i][item]
            if_then(i != user)
            rating_sum.write(rating_sum + rating_other * similarity)
            normalization.write(normalization + bitrating_other * similarity)
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
        prediction = rating_sum.read() / normalization.read()
        
        #rating_sum.delete()
        #normalization.delete()
        
        return prediction     
    
    @method_block
    def predict_rating_thresholded(self, user, item, t):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s, threshold %s", user, item, t)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nusers)
        def user_loop(i):
            similarity = self.model[user][i]
            rating_other = self.ratings[i][item]
            bitrating_other = self.bitratings[i][item]
            if_then(i != user)
            condition = (similarity >= t)
            rating_sum.write(condition.if_else(
                    rating_sum + rating_other * similarity,
                    rating_sum.read()
                            ))
            normalization.write(condition.if_else(
                    normalization + bitrating_other * similarity,
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
        self.ratings.delete()

class UBCosineCF(UserBasedModel):
    
    def __init__(self, nusers, nitems):
        self.norms = sfixArray(nusers)  # Normalization factors for the similarity measure.
        UserBasedModel.__init__(self, nusers, nitems, sfixMatrix(nusers,nitems), Matrix(nusers,nitems,sint))
            
    def _load_ratings_from(self, player, ratings):
        @for_range(self.nitems)
        def items_loop1(i):
            r = sint.get_raw_input_from(player)
            ratings[i] = sfix(*r)
            
    def _load_bitratings_from(self, player, bitratings):
        @for_range(self.nitems)
        def items_loop2(i):
            bitratings[i] = sint.get_raw_input_from(player)
            
    def load_normalization_from(self, user, player):
        norm = sint.get_raw_input_from(player)
        self.norms[user] = sfix(*norm)
    
    def set_normalization_factor(self, user, value):
        self.norms[user] = value
        
    def calc_normalization_factor(self, user):
        norm2 = sfix.MemValue(0)
        @for_range(self.nitems)
        def items_loop(i):
            norm2 += self.ratings[user][i]**2
        norm = norm2.reveal().sqrt()
        self.set_normalization_factor(user, norm)
    
    def calc_normalization_factors(self):
        @for_range(self.nusers)
        def users_loop(i):
            self.calc_normalization_factor(i)
    
    @method_block
    def cosine_sim(self, i,j):
        a = self.ratings[i]
        b = self.ratings[j]
        norma = self.norms[i]
        normb = self.norms[j]
        
        dot = sfix.MemValue(0)
        @for_range(a.length)
        def product_loop(i):
            dot.write(dot.read() + a[i] * b[i])
        
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", dot.reveal())
            print_ln("norma: %s, normb: %s", norma.reveal(), normb.reveal())
        cos = (dot/(norma * normb))
        if DEBUG >= INTERMEDIATE:
            print_ln("cos: %s", cos.reveal())
            print_ln(" ")
        return cos
    
    _build_model = lambda self, i, j :  self.cosine_sim(i,j)
            
    def delete(self):
        self.norms.delete()
        UserBasedModel.delete(self)

class SparseUBCosineCF(UBCosineCF):
    def __init__(self, nusers, nitems, capacity):
        self.norms = sfixArray(nusers)  # Normalization factors for the similarity measure.
        UserBasedModel.__init__(self, nusers, nitems, sfixSparseRowMatrix(nusers, nitems, capacity))
        self.capacity = capacity
        
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

class ItemBasedModel(object):
    def __init__(self, nusers, nitems, ratings, bitratings):
        self.model = cfixMatrix(nitems,nitems) # Similarity model
        self.ratings = ratings
        self.bitratings = bitratings
        self.nusers = nusers # Number of users
        self.nitems = nitems # Number of items
        
    def load_ratings_from(self, user, player):
        ratings = self.ratings[user]
        self._load_ratings_from(player, ratings)
        
    def load_bitratings_from(self, user, player):
        bitratings = self.bitratings[user]
        self._load_bitratings_from(player, bitratings)
        
    def build_model(self):
        if DEBUG >= VERBOSE:
            print_ln("Building secure shared similarity model")
        @for_range(self.nitems)
        def item_loop1(i):
            @for_range(i,self.nitems)
            def item_loop2(j):
                if DEBUG >= VERBOSE_PROGRESS:
                    print_str("\r%s to %s     ", i,j)
                ratings_j = self.ratings[j]
                sim = self._build_model(i,j)
                self.model[i][j] = sim
                self.model[j][i] = sim
        
        if DEBUG >= VERBOSE_PROGRESS:
            print_str("\r")
            
    def print_model(self):
        @for_range(self.nitems)
        def item_loop(i):
            @for_range(self.nitems)
            def item_loop(j):
                print_str('%s ', self.model[i][j])
            print_ln(' ')
    
    
    @method_block
    def predict_rating_all(self, user, item):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s", user, item)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nitems)
        def item_loop(i):
            similarity = self.model[item][i]
            rating_other = self.ratings[user][i]
            bitrating_other = self.bitratings[user][i]
            if_then(i != item)
            rating_sum.write(rating_sum + rating_other * similarity)
            normalization.write(normalization + bitrating_other * similarity)
            #print_ln("R: %s, N: %s", rating_sum.reveal(), normalization.reveal())
            end_if()
        prediction = rating_sum.read() / normalization.read()
        
        #rating_sum.delete()
        #normalization.delete()
        
        return prediction     
    
    @method_block
    def predict_rating_thresholded(self, user, item, t):
        if DEBUG >= INTERMEDIATE:
            print_ln("Predicting rating:\n user %s, item %s, threshold %s", user, item, t)
        
        rating_sum = sfix.MemValue(0)
        normalization = sfix.MemValue(0)
        
        @for_range(self.nitems)
        def item_loop(i):
            similarity = self.model[item][i]
            rating_other = self.ratings[user][i]
            bitrating_other = self.bitratings[user][i]
            if_then(i != item and similarity >= t)
            rating_sum.write(rating_sum + rating_other * similarity)
            normalization.write(normalization + bitrating_other * similarity)
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
        self.ratings.delete()
        self.ratings2.delete()


class IBCosineCF(ItemBasedModel):
    def __init__(self, nusers, nitems):
        self.norms = sfixArray(nitems)
        self.ratings2 = sfixMatrix(nusers,nitems)
        ItemBasedModel.__init__(self, nusers, nitems, sfixMatrix(nusers,nitems), Matrix(nusers,nitems,sint))
            
    def _load_ratings_from(self, player, ratings):
        @for_range(self.nitems)
        def items_loop(i):
            r = sint.get_raw_input_from(player)
            ratings[i] = sfix(*r)
    
    def _load_bitratings_from(self, player, bitratings):
        @for_range(self.nitems)
        def items_loop2(i):
            bitratings[i] = sint.get_raw_input_from(player)
    
    def load_ratings2_from(self, user, player):
        ratings2 = self.ratings2[user]
        @for_range(self.nitems)
        def items_loop(i):
            r2 = sint.get_raw_input_from(player)
            ratings2[i] = sfix(*r2)
            
    def set_normalization_factor(self, item, value):
        self.norms[item] = value
    
    def calc_normalization_factor(self, item):
        norm = sfix.MemValue(0)
        @for_range(self.nusers)
        def users_loop(i):
            norm.write(norm+ self.ratings2[i][item])
        self.set_normalization_factor(item, norm)
    
    def calc_normalization_factors(self):
        @for_range(self.nitems)
        def users_loop(i):
            self.calc_normalization_factor(i)
    
   
    
    @method_block
    def cosine_sim(self,i,j):
        dot = sfix.MemValue(0)
        normi2 = sfix.MemValue(0)
        normj2 = sfix.MemValue(0)
        @for_range(self.nusers)
        def user_loop(u):
            dot.write(dot+self.ratings[u][i] * self.ratings[u][j])
            normi2.write(normi2+self.bitratings[u][j] * self.ratings2[u][i])
            normj2.write(normj2+self.bitratings[u][i] * self.ratings2[u][j])
            if DEBUG >= INTERMEDIATE_FULL:
                print_ln("dot: %s", dot.reveal())
                print_ln("normi2: %s, normj2: %s", normi2.reveal(), normj2.reveal())
        
        normi = normi2.reveal().sqrt()
        normj = normj2.reveal().sqrt()
        if DEBUG >= INTERMEDIATE:
            print_ln("dot: %s", dot.reveal())
            print_ln("normi: %s, normj: %s", normi, normj)
        cos = dot.reveal()/(normi*normj)
        if DEBUG >= INTERMEDIATE:
            print_ln("cos: %s", cos)
        return cos
    
    _build_model = lambda self, i, j :  self.cosine_sim(i,j)
            
    def delete(self):
        self.norms.delete()
        ItemBasedModel.delete(self)
        
        
def OptimalCollaborativeFilter(nusers, nitems, capacity=None):
    raise CompilerError('Not implemented yet!')
    

    
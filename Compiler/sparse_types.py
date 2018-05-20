from Compiler.library import *
from Compiler.types import *

class sintSparseRatingArray(Array):
    def __init__(self, length, capacity,value_type, address=None):
        self.length = length
        self.capacity = capacity
        self.value_type = value_type
        self.array = Array(capacity*3, value_type, address)
        self.address = self.array.address
        self.tailpointer = cint(0)
        self.readonly = False
        if address != None:
            self.readonly = True
            self.tailpointer = capacity
    
    def delete(self):
        self.array.delete()
    
    def _getkey(self, index):
        return self.array[3*index]
    
    def _setkey(self, index, key):
        self.array[2*index] = key
    
    def _getr(self, index):
        return self.array[3*index+1]
    
    def _setr(self, index, r):
        self.array[2*index+1] = r
    
    def _setr2(self, index, r2):
        self.array[2*index+2] = r2
        
    def _getr2(self, index):
        return self.array[3*index+2]
                          
    def get_pair(self, key):        
        accu1 = MemValue(sint(0))
        accu2 = MemValue(sint(0))
        @library.for_range(self.tailpointer)
        def f(i):
            k = self._getkey(i)
            comp = k == key
            r1 = self._getr(i)
            accu1.write(match.if_else(r1, accu1.read()))
            r2 = self._getr2(i)
            accu2.write(match.if_else(r2, accu2.read()))
        return accu1.read(), accu2.read() 
    
    def get_rating(self, key):
        accu1 = MemValue(sint(0))
        @library.for_range(self.tailpointer)
        def f(i):
            k = self._getkey(i)
            comp = k == key
            r1 = self._getr(i)
            accu1.write(match.if_else(r1, accu1.read()))
        return accu1.read()
    
    def set_pair(self, key, rating, rating2):   
        if self.readonly:
            raise CompileError("Sparse Array is in readonly mode.")
        self._setkey(self.tailpointer, key)
        self._setr(self.tailpointer, rating)
        self._setr2(self.tailpointer, rating2)
        self.tailpointer += 1
    
    def writable(self, tailpointer=0):
        self.readonly = False
        self.tailpointer = tailpointer
        
    
    @classmethod
    def get_raw_input_from(cls, player, length, capacity,value_type, address=None):
        res = cls(length, capacity, value_type, address)
        @library.for_range(capacity)
        def get_entry(i):
            k = res.value_type.get_raw_input_from(player)
            r = res.value_type.get_raw_input_from(player)
            r2 = res.value_type.get_raw_input_from(player)
            res._setkey(i, k)
            res._setr(i, r)
            res._setr2(i,r2)
        tailpointer = sint.get_raw_input_from(player).reveal()
        res.writable(tailpointer)
        return res, tailpointer
        
    
class SparseRowMatrix(Matrix):
    def __init__(self, rows, columns, rowcap, value_type, addess=None):
        self.rows = rows
        self.columns = columns
        self.rowcap = rowcap
        self.matrix = Matrix(rows, columns*3, value_type)
    
    def delete(self):
        self.matrix.delete() 

    def __getitem__(self, index):
        return SparseArray(self.columns,self.rowcap, self.value_type, self.matrix[index].address)
    
class sfixSparseRatingArray(Array):
    def __init__(self, length, capacity, address=None):
        self.length = length
        self.capacity = capacity
        self.array = sintSparseRatingArray(length, capacity, sint, address)
        self.value_type = sfix
        self.address = self.array.address
        
        
    def delete(self):
        self.array.delete()
    
    _getkey = lambda self, index: self.array._getkey(index)
    _setkey = lambda self, index, key: self.array._setkey(index,key)
    _getr = lambda self, index: sfix(*self.array._getr(index))
    _setr = lambda self, index, val: self.array._setr(index,val.v)
    _getr2 = lambda self, index: sfix(*self.array._getr2(index))
    _setr2 = lambda self, index, val: self.array._setr2(index,val.v)
    writable =  lambda self, *args : self.array.writable(*args)
    
    def get_pair(self, key):    
        r1, r2 = self.array.get_pair(key)    
        return sfix(r1), sfix(r2)
    
    def get_rating(self, key):
        return self.array.get_rating(key)
    
    def set_pair(self, key, rating, rating2):   
        self.array.set_pair(key, rating.v, rating2.v)
    
    @classmethod
    def get_raw_input_from(cls, player, length, capacity, address=None):
        _, tp = SparseArray.get_raw_input_from(player, length, capacity, sint, address)
        res = cls(length, capacity, address)
        res.writable(tp)
        return res, tp
    

class sfixSparseRowMatrix(Matrix):
    def __init__(self, rows, columns, rowcap, addess=None):
        self.rows = rows
        self.columns = columns
        self.rowcap = rowcap
        self.value_type = sfix
        self.matrix = Matrix(rows, columns*3, sint)
        self.address = self.matrix.address
    
    def delete(self):
        self.matrix.delete()

    def __getitem__(self, index):
        return sfixSparseArray(self.columns,self.rowcap, self.matrix[index].address)
    


from Compiler.library import *
from Compiler.types import *

class SparseArray(Array):
    def __init__(self, length, capacity, value_type, address=None):
        self.length = length
        self.capacity = capacity
        self.value_type = value_type
        self.array = Array(capacity*2, value_type, address)
        self.address = self.array.address
        self.tailpointer = cint(0)
        self.readonly = False
        if address != None:
            self.readonly = True
            self.tailpointer = capacity
    
    def delete(self):
        self.array.delete()
    
    def _getkey(self, index):
        return self.array[2*index]-1
    
    def _setkey(self, index, key):
        self.array[2*index] = key+1
    
    def _getval(self, index):
        return self.array[2*index+1]
    
    def _setval(self, index, val):
        self.array[2*index+1] = val
    
    @method_block                      
    def __getitem__(self, key):
        if isinstance(key, slice):
            return Array.__getitem__(self, key)
        
        res = MemValue(sint(0))
        @library.for_range(self.tailpointer)
        def f(i):
            k = self._getkey(i)
            match = k == key
            val = self._getval(i)
            res.write(match.if_else(val, res.read()))
            #print_ln("match %s, res %s", match.reveal(), res.reveal())
        #val = res.read()
        #res.delete()
        return res.read()  
    
    def __setitem__(self, key, value):   
        if isinstance(key, slice):
            return Array.__setitem__(self, key, value)
        if self.readonly:
            raise CompileError("Sparse Array is in readonly mode.")
        self._setkey(self.tailpointer, key)
        self._setval(self.tailpointer, value)
        self.tailpointer += 1
    
    def writable(self, tailpointer=0):
        self.readonly = False
        self.tailpointer = tailpointer
        
    
    @classmethod
    def get_raw_input_from(cls, player, length, capacity, value_type, address=None):
        res = cls(length, capacity, value_type, address)
        @library.for_range(capacity)
        def get_entry(i):
            k = res.value_type.get_raw_input_from(player)
            v = res.value_type.get_raw_input_from(player)
            res._setkey(i, k)
            res._setval(i, v)
        tailpointer = sint.get_raw_input_from(player)
        res.writable(tailpointer)
        return res, tailpointer
        
    
class SparseRowMatrix(Matrix):
    def __init__(self, rows, columns, rowcap, value_type, addess=None):
        self.rows = rows
        self.columns = columns
        self.rowcap = rowcap
        self.matrix = Matrix(rows, columns*2, value_type)
    
    def delete(self):
        self.matrix.delete() 

    def __getitem__(self, index):
        return SparseArray(self.columns,self.rowcap, self.matrix.value_type, self.matrix[index].address)
    
class sfixSparseArray(Array):
    def __init__(self, length, capacity, address=None):
        self.length = length
        self.capacity = capacity
        self.array = SparseArray(length, capacity, sint, address)
        self.value_type = sfix
        self.address = self.array.address
        
        
    def delete(self):
        self.array.delete()
    
    _getkey = lambda self, index: self.array._getkey(index)
    _setkey = lambda self, index, key: self.array._setkey(index,key)
    _getval = lambda self, index: sfix(*self.array._getval(index))
    _setval = lambda self, index, val: self.array._setval(index,val.v)
    writable =  lambda self, *args : self.array.writable(*args)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return Array.__getitem__(self, index)
        return sfix(*self.array[index])

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            return Array.__setitem__(self, index, value)
        self.array[index] = value.v
    
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
        self.matrix = Matrix(rows, columns*2, sint)
        self.address = self.matrix.address
    
    def delete(self):
        self.matrix.delete()

    def __getitem__(self, index):
        return sfixSparseArray(self.columns,self.rowcap, self.matrix[index].address)
    


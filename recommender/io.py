import subprocess

class InputFp:
    def __init__(self,player):
        self.input_fp = []
        self.player = player
        
    def clear(self):
        self.input_fp = []
    
        
    def gen_input_fp(self):
        args = ("./gen_input_fp.x", "-i", "-", "-o", "Player-Data/Private-Input-{}".format(self.player))
        proc = subprocess.Popen(args, stdin=subprocess.PIPE)
        proc.stdin.write("{}\n".format(len(self.input_fp)))
        for value in self.input_fp:
            print(value)
            proc.stdin.write("{}\n".format(value))
        proc.wait()
        #print("Integers written to input %s: %s" % ( player, len(values)) )
    
    def append_fp(self, *values): 
        self.input_fp += values
        
    def append_fp_sparse_array(self, length, capacity, values):
        input=[]
        tailpointer = 0
        for k in range(length):
            if values[k] != 0:
                input += [k,values[k]]
                tailpointer += 1;
        if tailpointer > capacity:
            raise CompileError("Tailpointer exceeds capacity: {} > {}!".format(tailpointer, capacity))
        for _ in range(tailpointer, capacity):
            input += [0,0]
        input += [tailpointer]
        self.input_fp +=  input
    
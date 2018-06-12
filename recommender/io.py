import subprocess


class InputFp:
    """
    Connector for gen_input_fp.x.
    
    Generates the private input for the specified player.
    """
    def __init__(self,player):
        self.input_fp = []
        self.player = player
        
    def clear(self):
        """
        Reset the input.
        """
        self.input_fp = []
    
        
    def gen_input_fp(self):
        """
        Write the input from the buffer to the corresponding file. 
        
        Call it only once and at the end, because it overwrites previous files.
        """
        args = ("./gen_input_fp.x", "-i", "-", "-o", "Player-Data/Private-Input-{}".format(self.player))
        proc = subprocess.Popen(args, stdin=subprocess.PIPE)
        proc.stdin.write("{}\n".format(len(self.input_fp)))
        for value in self.input_fp:
            proc.stdin.write("{}\n".format(value))
        proc.wait()
        #print("Integers written to input %s: %s" % ( player, len(values)) )
    
    def append_fp(self, *values): 
        """
        Append an integer in F_p to the buffer.
        """
        self.input_fp += values
        
    def append_fp_array(self, values):
        """
        Append an array of integers in F_p to the buffer.
        """
        self.append_fp(*values)

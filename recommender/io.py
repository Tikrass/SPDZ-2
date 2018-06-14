# (C) 2018 Thibaud Kehler. 
# MIT Licence
# see https://opensource.org/licenses/MIT

import subprocess


class InputFp:
    """
    Connector for ``gen_input_fp.x``.
    
    Buffers and generates the private input for the specified ``player``.
    
    :param player: the player
    """
    def __init__(self,player):
        self.input_fp = []
        self.player = player
        
    def clear(self):
        """
        Reset the input buffer.
        """
        self.input_fp = []
    
        
    def gen_input_fp(self):
        """
        Write the input from the buffer to the corresponding private input file. 
        
        .. note::
        
            Call it exactly once and at the end, because it overwrites previous files.
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
        Append an integer to the buffer.
        
        :param values: one or more integers
        """
        self.input_fp += values
        
    def append_fp_array(self, values):
        """
        Append an array of integers to the buffer.
        
        :param values: a list of values.
        """
        self.append_fp(*values)

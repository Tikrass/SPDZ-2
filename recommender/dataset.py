# (C) 2018 Thibaud Kehler. 
# MIT Licence
# see https://opensource.org/licenses/MIT

import csv
from scipy.sparse import lil_matrix

class Dataset:
    """
    Connector for MovieLens datasets. 
    
    :param folder: a string containing the path to the movie lens files.
    :param separator: collumn separator (default: ``,``)
    :param quotechar: deliminator for longer strings. (default: ``"``)
    :param ratings_file_name: filename of the ratings file (default: ``ratings.csv``)
    :param movies_file_name: filename of the movie file (default: ``movies.csv``)
    """
    def __init__(self, folder, separator=',', quotechar='"', ratings_file_name="ratings.csv", movies_file_name="movies.csv"):
        self.ratings_file_name=ratings_file_name
        self.movies_file_name=movies_file_name
        
        self.delimiter=separator
        self.quotechar=quotechar
        
        self.ratings_file_path=folder+"/"+ratings_file_name
        self.movies_file_path=folder+"/"+movies_file_name
        
        # mid -> i    i -> mid
        self.i_to_mid,self.mid_to_i = self.__canonicalize_movieids()
        
        self.rating_list = self.__list_ratings()
        
        self.n_max = self.__count_userids()
        
        self.m_max = len(self.mid_to_i)
    
    def __canonicalize_movieids(self):
        """
        Enumerates the movie IDs (mid) canonically to item IDs (i) and builds a dictionary in both directions
        mid -> i, i -> mid
        """
        counter = 0
        i_to_mid = []
        mid_to_i = {}
        with open(self.movies_file_path, 'r') as movies_file:
            reader = csv.reader(movies_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)
            assert(header[0] == 'movieId')
            for row in reader:
                mid = int(row[0])
                i_to_mid.append(mid)
                mid_to_i[mid] = counter
                counter+=1
        return i_to_mid, mid_to_i   
    
    def __list_ratings(self):
        """
        Produces a list of all ratings::
        
            [(u1,i1,r1), (u2,i2,r2), ...]
        """
        ratings = []
        with open(self.ratings_file_path, 'r') as ratings_file:
            reader = csv.reader(ratings_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)    
            assert(header[0] == 'userId')
            assert(header[1] == 'movieId')
            assert(header[2] == 'rating')
            for rating in reader:
                u = int(rating[0])-1
                mid = int(rating[1])
                i = self.mid_to_i[mid]
                r = float(rating[2])
                ratings.append((u,i,r))
        return ratings
    
    def __count_userids(self):
        """
        Counts the number of users ``n``.
        """
        highest_id=0;
        for (u,i,r) in self.rating_list:
            if u > highest_id:
                highest_id = u
        return highest_id+1
            
    
    
    
    def get(self, n=None, m=None):
        """
        Get the specified rating matrix out of the file. 
        
        :param n: a number of users (default: ``None`` - load maximum possible)
        :param m: a number of items (default: ``None`` - load maximum possible)
        
        Returns 
        
            1. a rating matrix ``R``, where all undefined ratings are 0.
            2. a matrix of boolean values (1,0) ``B`` which indicate whether a rating exists.
            3. the ratings in list representation.
            4. the dimension of the rating matrix ``n`` and ``m``, which can be smaller than specified in the arguments.
            
        """
        if n == None or n >= self.n_max:
            n = self.n_max
        
        if m == None or m >= self.m_max:
            m = self.m_max
        
        R = lil_matrix((n, m))
        Rb = lil_matrix((n, m), dtype=int)
        Rlist = []                        
        for (u,i,r) in self.rating_list: 
            if u < n and i < m:
                Rlist.append((u,i,r))
                R[u,i] = r
                Rb[u,i] = 1
        return R.toarray(), Rb.toarray(), Rlist, n, m
    

    
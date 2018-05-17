import csv
from scipy.sparse import lil_matrix

class dataset:
    def __init__(self, folder, separator=',', quotechar='"', ratings_file_name="ratings.csv", movies_file_name="movies.csv"):
        self.ratings_file_name=ratings_file_name
        self.movies_file_name=movies_file_name
        
        self.delimiter=separator
        self.quotechar=quotechar
        
        self.ratings_file_path=folder+"/"+ratings_file_name
        self.movies_file_path=folder+"/"+movies_file_name
        
        self.n_max = self.__count_userids()
        self.mid_dict,self.mid_invdict = self.__canonicalize_movieids()
        self.m_max = len(self.mid_dict)
        
            
    def __count_userids(self):
        with open(self.ratings_file_path, 'r') as ratings_file:
            highest_id=0;
            reader = csv.reader(ratings_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)
            assert(header[0] == 'userId')
            for row in reader:
                if int(row[0]) > highest_id :
                    highest_id = int(row[0])
        return highest_id            
            
    
    def __canonicalize_movieids(self):
        counter = 0
        dict = []
        inv_dict = {}
        with open(self.movies_file_path, 'r') as movies_file:
            reader = csv.reader(movies_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)
            assert(header[0] == 'movieId')
            for row in reader:
                movieid = int(row[0])
                dict.append(movieid)
                inv_dict[movieid] = counter
                counter+=1
        return dict, inv_dict   
    
    def read(self, n=None, m=None):
        if n != None and n <= self.n_max:
            self.n = n
        else:
            self.n = self.n_max
        
        if m != None and m <= self.m_max:
            self.m = m
        else:
            self.m = self.m_max
        
        R = lil_matrix((self.n, self.m))
        Rb = lil_matrix((self.n, self.m), dtype=int)
                                       
        with open(self.ratings_file_path, 'r') as ratings_file:
            reader = csv.reader(ratings_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)    
            for rating in reader:
                u = int(rating[0])-1
                mid = int(rating[1])
                i = self.mid_invdict[mid]
                r = float(rating[2])
                    
                if u < self.n and mid < self.m:
                    R[u,i] = r
                    Rb[u,i] = 1
        return R.toarray(), Rb.toarray()
    

    
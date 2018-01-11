import csv
from scipy.sparse import lil_matrix

class dataset:
    def __init__(self, folder, separator=',', quotechar='"', ratings_file_name="ratings.csv", movies_file_name="movies.csv", discretize=None ):
        self.ratings_file_name=ratings_file_name
        self.movies_file_name=movies_file_name
        
        self.delimiter=separator
        self.quotechar=quotechar
        
        self.ratings_file_path=folder+"/"+ratings_file_name
        self.movies_file_path=folder+"/"+movies_file_name
        
        self.n = self.__count_userids()
        self.m = self.__count_movieids()
        
        self.discretize = discretize
            
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
            
    
    def __count_movieids(self):
        with open(self.movies_file_path, 'r') as movies_file:
            highest_id=0;
            reader = csv.reader(movies_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)
            assert(header[0] == 'movieId')
            for row in reader:
                if int(row[0]) > highest_id :
                    highest_id = int(row[0])
        return highest_id    
    
    def read(self, n=None, m=None):
        if isinstance(self.discretize, int):
            M = lil_matrix((self.n, self.m), dtype=int)
        else :
            M = lil_matrix((self.n, self.m))
                                       
        with open(self.ratings_file_path, 'r') as ratings_file:
            reader = csv.reader(ratings_file, delimiter=self.delimiter, quotechar=self.quotechar)
            header = next(reader)    
            for rating in reader:
                uid = int(rating[0])-1
                mid = int(rating[1])-1
                r = float(rating[2])
                if isinstance(self.discretize, int):
                    r = r * (10**self.discretize)
                    r = round(r)
                M[uid,mid] = r
        return M
    

    
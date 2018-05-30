from recommender.test import BaselineTest

def estimate_k():
    """
    Tests to estimate parameter k
    """
    K_PARAMS = range(1,31)
    F = 14
    NPREDICTIONS = 5000
    knn_params = zip(K_PARAMS, [F]*30)
         
         
    T = BaselineTest(1).eval_data().mean_centered() # Maximum Size
    T.buildUBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)
             
    T = BaselineTest(2).eval_data().mean_centered() # Maximum Size
    T.buildIBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)

def estimate_f():
    """
    Tests to estimate parameter f
    """
    K = 9
    F_PARAMS = range(1,15)
    NPREDICTIONS = 5000
    knn_params = zip([K]*14, F_PARAMS)
      
    T = BaselineTest(10).eval_data().mean_centered() # Maximum Size
    T.buildUBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)
          
    T = BaselineTest(20).eval_data().mean_centered() # Maximum Size
    T.buildIBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)

def performance_ub():
    """
    measure UB CF performance
    """
    PREDICT = True
    NPREDICTIONS = 5000
    N_PARAMS = [100,200,300,400,500]
    M = 3000
    K = 9
    F = 4
      
       
    for id,n in enumerate(N_PARAMS):
        T = BaselineTest(id*10).eval_data(n=n, m=M).mean_centered()
        T.buildUBbaseline()
        if PREDICT:
            T.testPredictions([(K, F)], NPREDICTIONS)


def performance_ib():
    """
    measure IB CF performance
    """
    PREDICT = True
    NPREDICTIONS = 5000
    N = 200
    M_PARAMS = [2000,3000,4000,5000,6000]
    K = 9
    F = 4  
    for id,m in enumerate(M_PARAMS):
        T = BaselineTest(id*10+100).eval_data(n=N, m=m).mean_centered()
        T.buildIBbaseline()
        if PREDICT:
            T.testPredictions([(K, F)], NPREDICTIONS)
        
def debug():
    """
    Debugging Tests
    """        
    K = 9
    F = 4
    N = 50
    M = 500
    NPREDICTIONS = 500
    
    T = BaselineTest(1).small_data().mean_centered() 
    T.buildUBbaseline()
    T.CF.print_ratings()
    T.CF.print_model()
    T.testPredictions([(2, 14)], 16)
    T.debugPredictions(2,14)
    
    T = BaselineTest(2).small_data().mean_centered() 
    T.buildIBbaseline()
    T.CF.print_ratings()
    T.CF.print_model()
    T.testPredictions([(2, 14)], 16)
    T.debugPredictions(2,14)
     
    T = BaselineTest(3).eval_data(n=N, m=M).mean_centered() 
    T.buildUBbaseline()
    T.CF.print_ratings()
    T.CF.print_model()
    T.testPredictions([(K, F)], NPREDICTIONS)
    T.debugPredictions(K, F)
          
    T = BaselineTest(4).eval_data(n=N, m=M).mean_centered() 
    T.buildIBbaseline()
    T.CF.print_ratings()
    T.CF.print_model()
    T.testPredictions([(K, F)], NPREDICTIONS)
    T.debugPredictions(K, F)
    
if __name__ == "__main__":
    import sys
    for mode in sys.argv:
        if mode == "DEBUG":
            debug()
        if mode == "ESTK":
            estimate_k()
        if mode == "ESTF":
            estimate_f()
        if mode == "UB":
            performance_ub()
        if mode == "IB":
            performance_ib()
            
        

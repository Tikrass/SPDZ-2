from recommender.test import BaselineTest

def estimate_ubk():
    """
    Tests to estimate parameter k in user-based filtering
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
    
def estimate_ibk():
    """
    Tests to estimate parameter k in item-based filtering
    """
    K_PARAMS = range(1,31)
    F = 14
    NPREDICTIONS = 5000
    knn_params = zip(K_PARAMS, [F]*30)
         
             
    T = BaselineTest(2).eval_data().mean_centered() # Maximum Size
    T.buildIBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)

def estimate_ubf():
    """
    Tests to estimate parameter f in user-based filtering
    """
    K = 9
    F_PARAMS = range(1,15)
    NPREDICTIONS = 5000
    knn_params = zip([K]*14, F_PARAMS)
      
    T = BaselineTest(10).eval_data().mean_centered() # Maximum Size
    T.buildUBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)
    
def estimate_ibf():
    """
    Tests to estimate parameter f in item-based filtering
    """
    K = 11
    F_PARAMS = range(1,15)
    NPREDICTIONS = 5000
    knn_params = zip([K]*14, F_PARAMS)
      
    T = BaselineTest(10).eval_data().mean_centered() # Maximum Size
    T.buildUBbaseline()
    T.testPredictions(knn_params, NPREDICTIONS)
          

def eval_ub():
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


def eval_ib():
    """
    measure IB CF performance
    """
    PREDICT = True
    NPREDICTIONS = 5000
    N = 200
    M_PARAMS = [1000,1500,2000,2500,3000]
    K = 11
    F = 14  
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
    
    K = 11
    F = 14
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
        if mode == "ESTUBK":
            estimate_ubk()
        if mode == "ESTUBF":
            estimate_ubf()
        if mode == "ESTIBK":
            estimate_ibk()
        if mode == "ESTIBF":
            estimate_ubf()
        if mode == "EVALUB":
            eval_ub()
        if mode == "EVALIB":
            eval_ib()
            
        

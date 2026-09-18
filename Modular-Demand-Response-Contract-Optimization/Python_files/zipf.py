import numpy as np
import scipy.stats as stats

class zipf:
    def __init__(self,min,max):
        self.a = 1.1
        self.x = np.arange(min,max+1)
        self.weights = self.x ** (-self.a)
        self.weights /= self.weights.sum()
        self.bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(self.x, self.weights))
    def sample(self,size=1):
        return self.bounded_zipf.rvs(size=size)[0]
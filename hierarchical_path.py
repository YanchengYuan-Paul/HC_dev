import numpy as np
import scipy as sc
from projections import *
from utils import *
from convex_hc_ADMM_nn_sparse import *
from convex_hc_denoising import *
from convex_hc_simplex import *
import time
import pickle


MAXIT_ADMM = 500
MAXIT_FISTA = 20
TOL= 5*1e-3
MAXITER_UX = 100
LAMBDA_MAX = 1e-3
N_LAMBDA = 20
LAMBDA0 = 1e-2

def compute_reg_path(kernel, alpha, pi_warm_start, mode="ADMM",
                     direction='up', tol= TOL,
                     lambdas = [0.00001, 0.001, 0.005, 0.01, 0.05, 0.1 ,0.5, 1.0],
                     verbose= False, savefile =None, logger=None, **kwargs):
    ''' Computes the regularization path for K

        INPUT:
        -----------------------------------------------------------
        kernel            :      similarity matrix
        alpha             :      weight l1 norm vs l21
        pi_warm_start     :      starting point of the algorith,
        direction         :      increasing r decreasing lambda sequence
                                 (if lambdas is not provided)
        
        OUTPUT:
        pi                :      sequence of results (dict)
        time              :      total time
        evol_rank         :      efficient rank of the solution (dict)
        -----------------------------------------------------------
        
    '''
    n_nodes = kernel.shape[0]
    evol_efficient_rank={}
    pi = {}
    x_init = pi_warm_start
    for lambd in lambdas:
        tic = time.time()
        if logger is not None: 
            logger.info('Starting lambda = %f'%lambd)
        else:
            print('Starting lambda = %f'%lambd)
        if mode == 'ADMM':
              x_k, _, _, _ = hcc_ADMM(kernel, x_init, lambd,
                                            alpha=alpha, rho=rho,
                                            maxit_ADMM=MAXIT_ADMM,
                                            tol=TOL,verbose=verbose,
                                            maxiter_ux=MAXITER_UX,
                                            logger=logger)
        elif mode == 'simplex':
              x_k, _, _, _ = hcc_FISTA_tot_simplex(kernel, x_init, lambd,
                                                    alpha=alpha, 
                                                    maxiterFISTA=MAXIT_FISTA,
                                                    tol = TOL,
                                                    verbose=verbose,
                                                    logger=logger)
        else:
              x_k, _, _, _ = hcc_FISTA(kernel, x_init, lambd,
                                        alpha=alpha, 
                                        maxiterFISTA=MAXIT_FISTA,
                                        tol = TOL,verbose=verbose,
                                        logger=logger)
        
        pi[lambd] = x_k
        x_init = x_k
        evol_efficient_rank[lambd]  = efficient_rank(x_k)
        print('--------------------------')
        print('--------------------------')
        print('--------------------------')
        toc = time.time()
        pi[lambd]={'pi':x_k, 'time':toc-tic}
        # Check divergence compare to previous

        if verbose:
             print('finished lambda = %f'%lambd)
        if logger is not None: 
            logger.info('finished lambda = %f'%lambd)
            logger.info('--------------------------------')
        if savefile is not None:
            pickle.dump(pi,open(savefile,'wb'))


    return pi, toc - tic, evol_efficient_rank




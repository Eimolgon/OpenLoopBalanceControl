# -*- coding: utf-8 -*-
"""
GSA (Morris) analysis for a bicycle model.
The model output no longer depends on speed `v`: each simulation returns a
single scalar, so the analysis is done once on the whole output vector.
"""

import numpy as np
import matplotlib.pyplot as plt
from SALib.sample import morris as morris_smpl
from SALib.analyze import morris as morris_anlz

import json
from timeit import default_timer as timer
from tqdm import tqdm
import uuid

from utils import generate_txt
from synthetic_data_study import fun_SA


def fun(bike):
    
    generate_txt('n', bike)
    res = fun_SA()
    
    return res


def get_fixed_parameters(problem, base_design):
    """Return fixed parameters and their values as a dict."""
    fixed = {}
    for kk in base_design:
        if kk not in problem['names']:
            fixed[kk] = base_design[kk]
    return fixed


def run_GSA_DOE(fun, problem, base_design, N, typ='morris',
                fname=None, randname=False):
    """Run Morris DOE. Number of simulations = (N_param + 1) * N.

    :param func fun: function to analyse (takes a bike dict, returns a scalar)
    :param dict problem: SALib problem definition
    :param dict base_design: base bike design, used for fixed parameters
    :param int N: number of trajectories for Morris
    :param str typ: 'morris'
    :param str fname: base name of file to save DOE and results
    :param bool randname: add random string to file name (overwrite protection)
    """
    fixedparam = get_fixed_parameters(problem, base_design)

    # SAMPLE
    if typ == 'morris':
        param_values = morris_smpl.sample(problem, N, 4)

    # RUN SIMULATIONS
    Y = []
    print('\nGoing to run %i simulations' % len(param_values))
    startt = timer()
    for ii, params in tqdm(enumerate(param_values)):
        pdict = dict(zip(problem['names'], params))
        pdict.update(fixedparam)
        Y.append(fun(pdict))

    endt = timer()
    printval = (endt - startt, len(param_values), (endt - startt) / len(param_values))
    print("\nTook %g s to run %i simulations: %g s/simu" % printval)
    Y = np.array(Y)   # 1D array, one scalar per simulation

    # SAVE INPUTS, OUTPUTS, and PARAMETERS OF DOE
    if fname is None:
        fname = '%s_n%i' % (typ, N)
    if randname:
        fname += '_' + uuid.uuid4().hex

    problem['fixed'] = fixedparam
    problem['GSA'] = {'typ': typ, 'N': N}
    with open(fname + '.json', 'w') as f:
        json.dump(problem, f)

    np.savez(fname, X=param_values, Y=Y)


class MorrisResults:
    """Handle Morris analysis results for a single scalar output."""

    def __init__(self, filename, output_index):
        """Load data from filename (.json and .npz)."""
        data = np.load(filename + '.npz', allow_pickle=False)
        self.X = data['X']
        self.Y = data['Y'][:, output_index]
        
        print(self.X, self.Y)

        with open(filename + '.json', 'r') as f:
            self.problem = json.load(f)

        self.names = self.problem['names']
        self._run_analysis()

    def _run_analysis(self):
        """Run Morris analysis once on the whole output vector."""
        print('Start Morris analysis')
        morris_indices = morris_anlz.analyze(self.problem, self.X, self.Y)

        # 1D arrays, one value per parameter
        self.SA = {
            'mu': np.array(morris_indices['mu']),
            'mu_star': np.array(morris_indices['mu_star']),
            'mu_star_conf': np.array(morris_indices['mu_star_conf']),
            'sigma': np.array(morris_indices['sigma']),
        }
        print('End of analysis')

    def plot_ranking(self, ranking='mu_star', figname=None, title=None):
        """Horizontal bar chart ranking the parameters by `ranking`."""
        order = np.argsort(self.SA[ranking])
        names = [self.names[i] for i in order]
        vals = self.SA[ranking][order]

        fig, ax = plt.subplots(num=figname, figsize=(6, len(names) / 2.5))
        ax.barh(range(len(names)), vals)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        if title:
            plt.title(title)
        plt.xlabel('%s' % ranking)
        plt.tight_layout()

    def plot_mu_sigma(self, figname=None, yscale='linear'):
        """Two bar charts: mu* and sigma per parameter."""
        fig, (ax1, ax2) = plt.subplots(2, 1, num=figname, figsize=(max(6, len(self.names) * 0.4), 8))
        x = range(len(self.names))

        ax1.bar(x, self.SA['mu_star'], yerr=self.SA['mu_star_conf'], capsize=3)
        ax1.set_ylabel('$\\mu^*$')
        ax1.set_yscale(yscale)

        ax2.bar(x, self.SA['sigma'])
        ax2.set_ylabel('$\\sigma$')
        ax2.set_yscale(yscale)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels(self.names, rotation=90)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(self.names, rotation=90)
        plt.tight_layout()

    def plot_mu_vs_sigma(self, figname=None, scale='linear'):
        """Scatter of mu* vs sigma, one point per parameter."""
        plt.figure(figname)
        plt.plot(self.SA['mu_star'], self.SA['sigma'], 'o')
        for mu, sig, name in zip(self.SA['mu_star'], self.SA['sigma'], self.names):
            plt.text(mu, sig, name, fontsize='x-small')

        plt.axline((0, 0), slope=1, color='0.8', zorder=0)
        plt.xlabel('$\\mu^*$')
        plt.ylabel('$\\sigma$')
        plt.gca().set_xscale(scale)
        plt.gca().set_yscale(scale)
        plt.tight_layout()


if __name__ == "__main__":
    plt.close('all')

    #%% Define base design
    names = ['lambda', 'c', 'm_H', 'x_H', 'z_H', 'I_Hxx', 'I_Hzz', 'I_Hxz',
             'm_R', 'r_R', 'I_Rxx', 'I_Ryy', 'm_F', 'r_F', 'I_Fxx', 'I_Fyy',
             'm_B', 'x_B', 'z_B', 'I_Bxx', 'I_Bzz', 'I_Bxz', 'w']
    param = [0.399680398707, 0.0685808540382, 3.22, 0.866949640247, -0.748236400835,
         0.25335539588, 0.0955686343473, -0.0720217263293, 3.11, 0.340958858855,
         0.0904114316323, 0.152391250767, 2.02, 0.34352982332, 0.0883826870796,
         0.149221207336, 9.86, 0.275951285677, -0.537842424305, 0.52962890621,
         0.756786895402, -0.116285607878, 1.121]
    
    names = ['lambda', 'c', 'm_H', 'x_H', 'z_H', 
             'm_R', 'r_R', 'I_Rxx', 'I_Ryy', 'm_F', 'r_F', 'I_Fxx', 'I_Fyy',
             'm_B' 'w']

    param = [0.399680398707, 0.0685808540382, 3.22, 0.866949640247, -0.748236400835,
         3.11, 0.340958858855, 0.0904114316323, 0.152391250767, 2.02, 0.34352982332, 0.0883826870796,0.149221207336, 
         9.86, 1.121]


    bike = dict(zip(names, param))

    #%% Define GSA problem with all parameters (10% variation)
    p_var = 0.10
    bounds = [(bike[kk] - abs(bike[kk] * p_var), bike[kk] + abs(bike[kk] * p_var))
              for kk in names]
    problem = {'num_vars': len(names), 'names': names, 'bounds': bounds}
    scenario = 'scenario_I'

    #%% RUN Morris
    if False:
        N = 10
        print('Running Morris')
        run_GSA_DOE(fun, problem, bike, N=N, typ='morris',
                    fname=f'results/SA/morris_{scenario}_n{N}_10p')

    #%% LOAD MORRIS
    if True:
        plt.close('all')
        N = 10
        MP = MorrisResults(f'results/SA/morris_{scenario}_n{N}', -1)
        MP.plot_mu_vs_sigma()
        MP.plot_mu_vs_sigma(scale='log', figname='mu_vs_sigma_log')
        MP.plot_mu_sigma()
        MP.plot_mu_sigma(yscale='log', figname='mu_sigma_log')
        MP.plot_ranking()
        MP.plot_ranking(ranking='sigma', figname='ranking_sigma')
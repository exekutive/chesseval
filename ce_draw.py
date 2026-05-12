''' ################################################################    
    This file contains functions to plot the results of the
    chess game analysis.
    
    
    GLOBALS:
            cfg.rcstyle         : arguments for the matplotlib rcsytle parameter.
                            
            cfg.chessplot_style : additional graph formatting
                
    ################################################################
    
    # add logging
    # add function descriptions
'''

import logging
import math
import ce_config as cfg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import (AutoMinorLocator, MaxNLocator)
from matplotlib.lines import lineStyles


# Subclass MaxNLocator to enforce a minimum tick interval
class ChessturnMajLocator(ticker.Locator):
    def __init__(self, min_interval=1.0):
        self.min_interval = min_interval

    def __call__(self):
        vmin, vmax = self.axis.get_view_interval()
        ticks = ticker.MaxNLocator(integer=True).tick_values(vmin, vmax)
        if len(ticks) > 1:
            interval = ticks[1] - ticks[0]
            if interval < self.min_interval:
                ticks = ticker.MultipleLocator(1.0).tick_values(vmin, vmax)
        return ticks

class ChessturnMinLocator(ticker.Locator):
    def __init__(self, threshold=10):
        self.threshold = threshold

    def __call__(self):
        vmin, vmax = self.axis.get_view_interval()
        ticks = ticker.MultipleLocator(1.0).tick_values(vmin, vmax)
        if vmax-vmin < self.threshold:
            ticks = ticker.MultipleLocator(0.5).tick_values(vmin, vmax)
        return ticks

def abs_max(adv_list:list):
    return max([abs(i) for i in adv_list])

def norm_score(eval_ns):
    # Normalize the scores.

    # Pass 1
    # # isolate scores of moves which aren't evaluated as mate
    nonmate_scores = [j for i,j in enumerate(eval_ns['score']['Advantage']) if eval_ns['wdl']['Draw'][i] != 0]

    score_max = abs_max(nonmate_scores)
    logging.info(f" Maximum centipawn advantage:\t{score_max}")
    
    # Pass 2
    # flatten the mate moves
    for l,m in enumerate(eval_ns['score']['Advantage']):
        if eval_ns['wdl']['Draw'][l] == 0:
            eval_ns['score']['Advantage'][l] = ( m/abs(m) * score_max ) + 10

    logging.info(" Analysis results normalized")
    
    return

def pawns(x, pos): #        Formatter to convert centipawn score to pawns
    return f'{x*1e-2:+g}'

def draw_eval(game_eval):
    
    global rcstyle
    global chessplot_style   

    logging.info( " Building graph ...")

    # Build X series data:
    eval_moves = range(1,len(game_eval['wdl']['White']) + 1) # a list of half-move numbers
    eval_turns = [(m/2) + 0.5 for m in eval_moves]
        
    norm_score(game_eval)

    with plt.rc_context(cfg.rcstyle):
        
        fig1, ax_prob = plt.subplots()
        
        ax_prob.stackplot(
            eval_turns, game_eval['wdl'].values(),
            labels = game_eval['wdl'].keys(),
            colors = [  cfg.chessplot_style['stack_top'],
                        cfg.chessplot_style['stack_mid'],
                        cfg.chessplot_style['stack_bottom']],
            alpha = 0.8)
        
        ax_prob.plot(
            eval_turns, game_eval['score']['Expectation'],
            label = 'Expected outcome',
            color = cfg.chessplot_style['exp_col'])


        ax_prob.set(
            title       = 'Stockfish Evaluation',
            xlabel      = 'Turn',
            ylabel      = 'Probability',
            xlim        = (1,eval_turns[-1]),
            ylim        = (-0.005,1.005) )


        #* add vertical lines every 10 turns for long games
        # ax_prob.axvline()


        ax_prob.xaxis.set_major_locator(ChessturnMajLocator(min_interval=1.0))
        ax_prob.xaxis.set_minor_locator(ChessturnMinLocator(threshold=10))


        ax_prob.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax_prob.yaxis.set_major_locator(ticker.MultipleLocator(0.25))
        ax_prob.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
                
        ax_prob.legend( title            = 'Win Probability',
                        bbox_to_anchor   = (1.15, 1),
                        loc              = 'upper left'
                        ).get_title().set_fontweight('bold')

        ax_prob.plot()

        ax_adv = ax_prob.twinx()

        # configure base line
        ax_adv.axhline(
            color       = cfg.chessplot_style['base_col'],
            linestyle   = cfg.chessplot_style['base_style'],
            linewidth   = cfg.chessplot_style['base_width']
            )

        ax_adv.plot(
                eval_turns, game_eval['score']['Advantage'],
                color = cfg.chessplot_style['adv_col'],
                label = 'Advantage (Pawns)')


        # configure pawn advantage y-axis
        pawn_max    = abs_max( game_eval['score']['Advantage'] ) * 1e-2
        y_max       = -(-pawn_max // 1) * 1e2 # rounds up to next integer and converts back to centipawn
        
        ax_adv.set(
            ylabel  = 'Pawns',
            ylim    = (-(y_max * 1.01), (y_max * 1.01) ))
        
        ax_adv.legend(bbox_to_anchor = (1.15, 0), loc='lower left').get_title().set_fontweight('bold')

        ax_adv.yaxis.set_major_formatter(pawns)
        ax_adv.yaxis.set_major_locator(ticker.MultipleLocator(100))
        ax_adv.yaxis.set_minor_locator(AutoMinorLocator())

    plt.tight_layout()
    
    print( "Rendering graph ...")

    plt.show()
    
    return
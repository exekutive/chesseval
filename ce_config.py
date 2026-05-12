''' ############################# INFO ##################################

    In this module:
    
    Code to initialize global variables and generally setup
    the environment.
    Configure things chess engine options, file paths and display
    styles here.
    
    Note:     Logging requires Python 3.8 or newer

    ################################################################

'''

import argparse
import logging
import chess.pgn

def set_clargs():
# - - - - - - - 
# FN set_clargs
# description   : Define command line parameters and help page
# parameters    : none
# returns       : parser object

    parser = argparse.ArgumentParser (
        prog          = 'chesseval.py',
        description   = 'Chess game evaluator. Accepts a chess game in Portable Game Notation (PGN). Evaluates the strength of each move, and plots the results on a chart. github.com/exekutive',
        epilog        = '"One bad move nullifies forty good ones."'
    )

    
    parser.add_argument('--game', '-g', type=str, help="Chess game/moves in Portable Game Notation.") 
    parser.add_argument('-v', '--verbose',  action="count", default=0, help="increase output verbosity")
    
    logging.info(" Command line parameters defined.")
    
    return parser
    
def fetch_clargs():
# - - - - - - - 
# FN fetch_clargs
# description   : Retrieve arguments entered at the command line
# parameters    : None
# Requires      : parser object with defined args (pgn and verbosity)
# returns       : dictionary object containing the parsed args (pgn string and verbosity level integer)
#                 eg.
#                 ce_test.py -vv -g '1. e4 e5 2. Nf3 Nf6 3. Bc4 Nxe4'
#                 returns
#                 {'game': '1. e4 e5 2. Nf3 Nf6 3. Bc4 Nxe4', 'verbose': 2}


    fc_args = vars(set_clargs().parse_args())
    logging.info ( f" Command line args captured: {fc_args}")
    
    return fc_args

def set_verbosity():
# - - - - - - - 
# FN set_verbosity
# description   : Sets the program verbosity level. 0=none, 1=info, 2+=debug
# parameters    : None
# Requires      : global cl_args with integer verbosity level. Can be 0, 1, 2, 3, ....
# returns       : None

    global cl_args

    if cl_args['verbose'] >= 2:
        logging.basicConfig( level=logging.DEBUG, force=True )
        logging.debug(" Verbosity level set to DEBUG")

    elif cl_args['verbose'] == 1:
        logging.basicConfig( level = logging.INFO, force=True )
        logging.info(" Verbosity level set to INFO")

    else:
        logging.info(" Verbosity requested is zero, negative or not specified.\nLeaving it unchanged.")

sf_options = dict(   # Stockfish UCI options
    path            = "/opt/homebrew/bin/stockfish",
    threads         = 8,
    hash			= 24_000, #		    (MiB)
    depth		    = 12,
    time            = 200, #			ms
    log			    = "./debugsf.txt",
    # syz_path      = "/somepath/syzygy"
)

pgn_outputfile	= "./analyzedgame.pgn"
mate_eval       = 100_000 # initial cp score for mate. gets normalized later

# matplotlib style arguments for graphs 
rcstyle = {
    'text.color'        : '#08160E',
    'figure.facecolor'  : "#C8EDD5",
    # 'axes.facecolor'    : '#C0BCA9',
    'axes.facecolor'    : 'none',
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'axes.titlepad'     : '20.0',
    'axes.titlesize'    : '18',
    'axes.grid'         : False,
    'axes.grid.axis'    : 'x',
    'grid.color'        : '#746C3C',
    'grid.linestyle'    : (0, (1, 5)),
    'grid.linewidth'    : '1.2',
    'grid.alpha'        : '1',
    'legend.facecolor'  : '#746C3C',
    'legend.framealpha' : '0.3',
    'legend.loc'        : 'upper right',
    'lines.linewidth'   : '1.3',
    'ytick.left'        : True,
    'xtick.direction'   : 'out',
    'ytick.direction'   : 'out',
    'ytick.major.size'  : 10,
    'ytick.major.width' : 1.2,
    'ytick.minor.size'  : 5,
    'ytick.minor.width' : 0.6  
}

# additional graphical elements
chessplot_style = {
    'stack_top'     : '0.2',      # stackplot colors. greyscale values
    'stack_mid'     : '0.7',
    'stack_bottom'  : 'white',
    'exp_col'       : '#868400',    # lineplot colors
    'adv_col'       : '#003A0A',
    'base_col'      : '#08160E',    # base line
    'base_style'    : (0, (1, 1)),
    'base_width'    : 1.0
}


cl_args = fetch_clargs()
set_verbosity()

#* use chess.pgn.GameBuilder here?
game_input = chess.pgn.Game()

logging.info (" Game object initialized. Configuration complete.")
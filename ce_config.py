''' ############################# INFO ##################################

    In this module:
    
    Code to initialize global variables and generally setup
    the environment.
    Configure chess engine options, file paths and display
    styles etc here.
    
    Note:     Logging requires Python 3.8 or newer

    #####################################################################
'''

import argparse
import logging
import chess.pgn

cl_args = {}

def set_clargs():
    ''' descr   : Define command line parameters and help page
        params  : None
        returns : parser object '''
    parser = argparse.ArgumentParser (
        prog          = 'chesseval.py',
        description   = 'Chess game evaluator. Accepts a chess game in Portable Game Notation (PGN). Evaluates the strength of each move, and plots the results on a chart. github.com/exekutive/chesseval',
        epilog        = '"One bad move nullifies forty good ones."'
    )
    
    parser.add_argument('--verbose', '-v', action="count", default=0, help="increase output verbosity")
    parser.add_argument('--noplot', help="Skip displaying the analysis", action="store_true", default=False)
    parser.add_argument('--nowdl', help="Do not show win/draw/lose stackplot", action="store_true", default=False)
    parser.add_argument('--noexp', help="Do not show expected outcome lineplot", action="store_true", default=False)
    parser.add_argument('--noadv', help="Do not show Pawn advantage lineplot", action="store_true", default=False)
    parser.add_argument('--depth', '-d', type=int, help="Use custom Stockfish analysis depth limit (plies)")
    parser.add_argument('--time', '-t', type=int, help="Use custom Stockfish analysis time limit (ms)")
    parser.add_argument('--game', '-g', type=str, help="Specify a move list in Portable Game Notation") 
    parser.add_argument('--import', '-i', type=str, help="Enable PGN file import", metavar='file_path') 
    parser.add_argument('--export_pgn', '-ep',
        help    = "Enable PGN file export. Default path: ./ce_export.pgn",
        metavar = 'file_path',
        type    = str,
        nargs   = '?', 
        const   = './ce_export.pgn',
        default = None )
    parser.add_argument('--export_csv', '-ec',
        help    = "Enable CSV file export. Default path: ./ce_export.csv",
        metavar = 'file_path',
        type    = str,
        nargs   = '?', 
        const   = './ce_export.csv',
        default = None )
    parser.add_argument('--export_fig', '-ef',
        help    = "Enable plot figure export. Default path: ./ce_export.png",
        metavar = 'file_path',
        type    = str,
        nargs   = '?', 
        const   = './ce_export.png',
        default = None )
    logging.info(" Command line parameters defined.")
    
    return parser
    
def fetch_clargs():
    ''' descr   : Retrieve arguments entered at the command line
        params  : None
        Requires: parser object with defined args (see set_clargs)
                  global dictionary object cl_args
        returns : none
        eg.
        ce_test.py -vv -g '1. e4 e5 2. Nf3 Nf6 3. Bc4 Nxe4'
        returns
        {'game': '1. e4 e5 2. Nf3 Nf6 3. Bc4 Nxe4', 'verbose': 2}
        '''

    global cl_args

    cl_args = vars(set_clargs().parse_args())

    set_verbosity()

    logging.info ( f" Command line args captured: {cl_args}")
    
    return

def set_verbosity():
    ''' descr   : Sets the program verbosity level. 0=none, 1=info, 2+=debug
        params  : none. Uses global cfg.cl_args. Value can be 0, 1, 2, 3, ....
        returns : none. '''

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
    hash			= 24_000, #     (MiB)
    depth		    = 18, #         (plies)
    time            = 200, #        (ms)
    log			    = "./debug_sf.txt",
    # syz_path      = "/somepath/syzygy"
)

pgn_outputfile	= "./analyzedgame.pgn"

# matplotlib style arguments for graphs 
rcstyle = {
    'text.color'        : '#08160E',
    'figure.facecolor'  : "#C8EDD5",
    # 'axes.facecolor'    : '#C0BCA9',
    'axes.facecolor'    : 'none',
    'axes.spines.top'   : False,
    'axes.spines.right' : True,
    'axes.spines.left'  : True,
    'axes.spines.bottom': False,
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
    'lines.linewidth'   : '1.5',
    'xtick.direction'   : 'out',
    'xtick.major.size'  : 6,
    'xtick.major.width' : 1.0,
    'xtick.minor.size'  : 3,
    'xtick.minor.width' : 0.5,
    'ytick.left'        : True,
    'ytick.direction'   : 'out',
    'ytick.major.size'  : 6,
    'ytick.major.width' : 1.0,
    'ytick.minor.size'  : 4,
    'ytick.minor.width' : 0.5,
    'font.family'       : 'sans-serif'
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


fetch_clargs()

# override config values if command line args provided
if cl_args['depth'] and cl_args['depth'] > 0:
    sf_options['depth'] = cl_args['depth']

if cl_args['time'] and cl_args['time'] > 0:
    sf_options['time'] = cl_args['time']


#* use chess.pgn.GameBuilder here?
game_input = chess.pgn.Game()

logging.info (" Configuration complete. Game object initialized.")
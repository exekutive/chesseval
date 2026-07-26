''' ############################# INFO ##################################
    This file contains functions to obtain input needed for the program:
        - Get game data from the user
        - Format and parse it
        - Build a chess game object from the input
    And also for output
        - writing PGN etc.
        
    It relies on ce_config being run first.

    GLOBALS:
                game_input: The game object returned and
                            used by the rest of the program           
                cl_args:    arguments user entered at
                            the command line.

    FLOW:
        build_game              
        │                      
        │(calls)               
        │                      
        ├─► <REDO>     
        │   │                  
        │   ├─────►xxxx
        │   └─────►yyy
    #####################################################################
'''

import logging
import sys
from io import StringIO
import chess
import chess.pgn
import ce_config as cfg
import time


def fetch_cl_movelist():
    ''' descr   : fetch the move list entered with '--game' CL argument.
                  clean it up a bit and check basic validity
        params  : None. Requires the cl_args global from ce_config.py
        returns : move list as StringIO object'''

    global cl_args
    movelist_io = None

    logging.info(" Checking CL args for input ...")

    if cfg.cl_args['game']:
        logging.info(" '--game' argument detected.")
        move_list = cfg.cl_args['game'].strip()

        if len(move_list) > 1:
            logging.info(" Possible valid moves found in CL args.")
            movelist_io = StringIO(move_list)

    return movelist_io

def fetch_file():
    ''' descr   : fetch contents of file entered with '--import' CL argument.
                  clean it up a bit and check basic validity
        params  : None. Requires the cl_args global from ce_config.py
        returns : file contents as StringIO object if valid
                  Otherwise, "None" '''

    global cl_args
    file_stream = None

    logging.info(" Checking for file input ...")

    if cfg.cl_args['import']:
        logging.info(" '--import' argument detected.")
        logging.info (f" Attempting to load file : {cfg.cl_args['import']} ...")
        
        with open(cfg.cl_args['import'], "rt") as pgnfile:
            file_read = pgnfile.read().strip()
            # logging.info (f" File contents :\n{file_read}")            
            if len(file_read) > 1:
                file_stream = StringIO(file_read)
                logging.info(" Found some data in the file.")
            else:
                logging.info(" Couldn't find data in the file.")

    return file_stream

def fetch_stdin():
    ''' descr   : gets stdin data if present, and do basic checks
        params  : None
        returns : StringIO object containing piped data if present, otherwise None '''

    logging.info(" Checking for stdin input ...")

    stdin_IO = None

    if sys.stdin.isatty():
        logging.info ( " No pipe detected. stdin connected to interactive terminal")
    else:
        logging.info ( " Pipe detected. Reading in the data ...")
        stdin_input = sys.stdin.read().strip()        
        if len(stdin_input) > 1:
            logging.info ( " stdin data is non-empty.")
            stdin_IO = StringIO(stdin_input)
        else:
            print ("\nNo valid data in stdin.")

    return stdin_IO

def prompt_input():
    ''' descr   : Prompt user to enter PGN data, and return the entered text
        params  : None
        returns : StringIO object containing text entered by user if present
                  Otherwise, None '''
    
    logging.info (" Prompting user for PGN data at terminal ...")

    usr_input = None

    print()
    while usr_input is None or len(usr_input) < 2:
        try:
            usr_input = input("Enter the game move list in PGN format: ").strip()
        except (EOFError):
            print ("You must enter at least one valid chess move.")
            usr_input = None

    logging.info (f" Input received: {usr_input}")

    return StringIO(usr_input)

def parse_pgn(pgn_stream):
    ''' descr   : Use chess module to read in a PGN formatted move list from file or stream and build a game object
        params  : stringio stream object containing the PGN move list for one game
        returns : populated Chess game object for valid input. Exits if not. '''
    
    logging.info (" Parsing input PGN stream ...")

    # turn down volume on parser. It's too noisy
    logging.getLogger("chess.pgn").setLevel(logging.CRITICAL)
    
    pgn_parsed = chess.pgn.read_game(pgn_stream)

    if pgn_parsed is None:
        print ("End of data reached. Exiting")
        sys.exit(1)
    elif pgn_parsed.errors:
        print ("\nThe game could not be imported because:")
        print (pgn_parsed.errors)
        print ("\nPlease fix PGN and try again. Exiting")
        sys.exit(1)
    elif pgn_parsed.end().ply() == 0:
        print ("Bad PGN data or no valid moves found.")
        print ("Please check the PGN data and try again. Exiting")
        sys.exit(1)

    logging.info (" Game created successfully.")
    logging.info (f" {pgn_parsed.end().ply()} moves read.")

    return pgn_parsed

def build_game():
    ''' descr   : Fetches pgn data provided by user & uses it to build chess game object for analysis
        params  : none
        returns : game_input chess object is populated if pgn is valid. Exits if not '''

    global game_input
    global cl_args
    
    # do prelim checks and proceed based on results
    piped_input = fetch_stdin()
    clarg_input = fetch_cl_movelist()
    file_input = fetch_file()

    # Looks for user input via stdin, CL args, and file, and decides if prompt is needed

    # CASE 1: too many inputs
    if (piped_input and clarg_input or
        piped_input and file_input or
        clarg_input and file_input):

        print ("Warning: chesseval received too many inputs. Please provide only one.")
        print ("Exiting.")
        raise SystemExit(1)

    # CASE 2: pgn entered via stdin
    elif piped_input:
        logging.info(" Data from stdin selected for parsing.")
        pgnIO = piped_input

    # CASE 3: move list entered via cli '-g' option
    elif clarg_input:
        logging.info(" Move list CL argument selected for parsing.")
        pgnIO = clarg_input

    # CASE 4: User provided a file path argument
    elif file_input:
        print("Using PGN file for input.")
        pgnIO = file_input

    # CASE 5: nothing provided at launch
    else:
        logging.info(" Undefined or invalid input at launch.")
        pgnIO = prompt_input()

    logging.info(f" Chosen input:\n{pgnIO.getvalue()}")
    
    cfg.game_input = parse_pgn(pgnIO)

    return

def write_pgn():
    ''' descr   : writes move list to a PGN file including evaluation as annotations
        params  : none. Uses globals cfg.game_input and cfg.cl_args['export_pgn']
        returns : none. '''
    
    global game_input
    global cl_args

    logging.info (" Attempting PGN file export ...")

    cfg.game_input.headers["Result"] = cfg.game_input.end().board().result()
    cfg.game_input.headers["Event"] = "chesseval.py analysis"
    cfg.game_input.headers["Site"] = "github.com/exekutive/chesseval"
    cfg.game_input.headers["Date"] = time.ctime()


    with open(cfg.cl_args['export_pgn'], "wt") as export_file:
        print(cfg.game_input, file = export_file, end="\n\n")
        logging.info (f" Game PGN saved to file {cfg.cl_args['export_pgn']}")

    return

def write_csv(sf_eval):
    ''' descr   : write analysis stats to a CSV file
        params  : Stockfish evaluation from ce_analysze.eval_game()
                  Uses globals cfg.game_input and cfg.cl_args['export_csv']
        returns : none. '''
    
    import csv
    global game_input
    global cl_args

    

    logging.info (" Attempting CSV file export ...")

    with open(cfg.cl_args['export_csv'], "wt", newline="", encoding="utf-8") as csv_file:
        csv_out = csv.writer(csv_file)

        move_list = list( chess.pgn.ChildNode.san(node) for node in cfg.game_input.mainline() )

        csv_out.writerow( ['half_move'] + list(range(1,len(move_list)+1)) )
        csv_out.writerow( ['move_san'] + move_list )

        csv_out.writerow( ['wdl_black'] + sf_eval['wdl']['Black'] )
        csv_out.writerow( ['wdl_draw'] + sf_eval['wdl']['Draw'] )
        csv_out.writerow( ['wdl_white'] + sf_eval['wdl']['White'] )

        csv_out.writerow( ['score_exp'] + sf_eval['score']['Expectation'] )
        csv_out.writerow( ['score_adv'] + sf_eval['score']['Advantage'] )

        csv_out.writerow( ['analysis_depth'] + sf_eval['analysis']['Depth'] )
        csv_out.writerow( ['analysis_time'] + sf_eval['analysis']['Time'] )        

        logging.info (f" Analysis saved to CSV file {cfg.cl_args['export_csv']}")

    return


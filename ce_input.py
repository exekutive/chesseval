''' ############################# INFO ##################################
    
    This file contains functions to obtain input needed for the program:
    
        - Get game data from the user
        - Format and parse it
        - Build a chess game object from the input
        
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
        ├─►get_pgn             
        │   │                  
        │   ├─────►fetch_stdin 
        │   └─────►prompt_input
        │                      
        ├─►make_stream         
        └─►parse_pgn           

    #####################################################################
'''

import logging
import sys
import io
import chess
import chess.pgn

import ce_config as cfg



def prompt_input():

# - - - - - - - 
# FN prompt_input
# description   : Prompt user to enter PGN data, and return the entered text
# parameters    : none
# returns       : string containing text entered by user
    
    usr_input = None
    print()

    while usr_input is None or len(usr_input.strip()) < 2:
        
        try:
            usr_input = input("Enter PGN data: ")
        except (EOFError):
            print ("Input ended before data could be found")
            usr_input = None


    logging.info (f" Input received: '{usr_input}'")

    
    return usr_input.strip()


def fetch_stdin():
# - - - - - - - 
# FN fetch_stdin
# description   : gets piped data if present
# parameters    : None
# returns       : string containing piped data or None

    if sys.stdin.isatty():
        logging.info ( " No pipe detected. stdin connected to interactive terminal")
        stdin_input = None
    else:
        logging.info ( " Pipe detected.")
        stdin_input = sys.stdin.read().strip()
        logging.info ( " stdin data captured and trimmed." )
        
        if len(stdin_input) < 2:
            print ("\nPiped stdin is invalid.")
            sys.exit(1)

    return stdin_input


def get_pgn():

# - - - - - - - 
# FN get_pgn
# description   : Looks for user input via stdin, CL args, and decides if prompt is needed
# parameters    : none
# requires      : global cl_args from ce_config
# returns       : string containing input game PGN, or exits if there's conflict

    global cl_args
    
    piped_input = fetch_stdin()
    clarg_input = None

    if cfg.cl_args['game']:
        clarg_input = cfg.cl_args['game'].strip()
        if len(clarg_input) < 2:
            clarg_input = None

    if piped_input and clarg_input:
        print ("Warning: Program recived stdin data and --pgn argument. Please use one or the other.")
        print ("Exiting.")
        raise SystemExit(1)
    elif piped_input:
        logging.info(" Data from stdin selected for parsing.")
        input_pgn = piped_input   
    elif clarg_input:
        logging.info(" Selecting game argument provided at command line.")
        input_pgn = clarg_input
    else:
        logging.info(" Invalid or undefined PGN from CL arguments and stdin.")
        logging.info(" Prompting for PGN input at terminal device.")
        input_pgn = prompt_input()

    return input_pgn


def make_stream(input_string:str):
# - - - - - - - 
# FN make_stream
# description   : create a text i/o stream object containing input string
# parameters    : a string
# returns       : io stream object containing text from input string


#  *** take out while loop but check for empty string. or ditch the function altogether

    output_stream = io.StringIO()

    while not output_stream.getvalue():    
        try:
            output_stream = io.StringIO(input_string)
        except (OSError, MemoryError):
            print("A system error occurred creating text io stream. Exiting.")
            raise SystemExit(1)
        except (UnicodeEncodeError, UnicodeDecodeError, TypeError):
            print ("Input text error creating io stream. Exiting.")
            raise SystemExit(1)
        finally:
            logging.info (" Input stream created successfully.")

    return output_stream


def parse_pgn(pgn_stream:io.StringIO):
# - - - - - - - 
# FN parse_pgn
# description   : Use chess module to build a game object from pgn data
#                   https://python-chess.readthedocs.io/en/latest/pgn.html#chess.pgn.read_game
# parameters    : stringIO stream containing pgn formatted text. One game per call.
# returns       : populated game object
    
    #check for empty game
    
    logging.info (" parsing input PGN stream.")

    logging.getLogger("chess.pgn").setLevel(logging.CRITICAL) # silence the parser
    
    pgn_parsed = chess.pgn.read_game(pgn_stream)

    if pgn_parsed.errors:
        print ("\nThe moves could not be imported because:")
        print (pgn_parsed.errors)
        print ("\nPlease fix PGN and try again. Exiting")
        sys.exit(1)
    elif pgn_parsed is None:
        print ("End of data reached. Exiting")
        sys.exit(1)
    elif pgn_parsed.end().ply() == 0:
        print ("Bad PGN data or no valid moves found.")
        print ("Please check the PGN data and try again. Exiting")
        sys.exit(1)

    logging.info (" Game created successfully.")
    


    # try:
    #     if hasattr(pgn_parsed, 'errors'):
    #         print ("Error: Invalid game data.")
    #         print (pgn_parsed.errors)
    #         print ("Please fix PGN and try again.")
    #         raise ValueError
        
    #     if pgn_parsed is None:
    #         print ("End of data reached.")
    #         raise ValueError

    # except ValueError:
        
    #     print ("Exiting.")
    #     raise SystemExit(1)

    return pgn_parsed


def build_game():
    # - - - - - - - 
    # FN build_game
    # description   : Fetches pgn data provided by user & uses it to build chess game object for analysis
    # parameters    : string containing game PGN
    # returns       : chess game object if pgn is valid. Exits if not

    global game_input

    with make_stream(get_pgn()) as pgn_strio:
        cfg.game_input=parse_pgn(pgn_strio)



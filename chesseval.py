''' ############################# INFO ##################################

    chesseval
    2026-MAY-11

    https://github.com/exekutive/chesseval
    
    Description:
        A Python program that uses the Stockfish engine to analyze the strengths of all the moves in a chess game,
        then plots the analysis on a graph. Chesseval does not generate moves.
        Developed with Python 3.13 and Visual Studio Code on MacOS.

    Dependencies:
        Python v3.6 required for f strings (https://www.python.org/)
        Python v3.8 for debug logging
        Matplotlib Python package (https://matplotlib.org/)
        Chess Python package (https://github.com/niklasf/python-chess)
        Stockfish chess analysis engine (https://stockfishchess.org/)

    Installation:
        1.  Install Python (https://wiki.python.org/moin/BeginnersGuide/Download)
        2.  Create a virtual environment and install the packages
            (https://packaging.python.org/en/latest/tutorials/installing-packages/)
        3.  Install Stockfish command line program
        4.  Type your Stockfish binary path into ce_config.py 
        5.  Adjust the threads value to your system. Your system's number of physical CPU cores is a good number
        6.  Adjust hash value to your system. Value is specified in MiB.
            According to Stockfish documentation:
            "For deep analysis set it to as much as you can afford given the available memory in your system,
            leaving some memory for the operating system and other applications."
            https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html#analysis

    Usage:
        type 'python chesseval.py --help' to get usage help.

    Sample PGN Data:
        1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
'''

import time
time_start = time.time()


import ce_config as cfg
import ce_input as cei
import ce_analyze as cea
import ce_draw as ced
# import ce_fileout

import logging
# manually set verbosity here. Valid until (if) elevated by user args later
# logging.basicConfig (level = logging.INFO)


print ()
logging.info (" Started: %s\n" % time.ctime())


cei.build_game()    

ge = cea.eval_game()

time_analyzed = time.time()
logging.info (f" Analysis time:\t{round(time.time() - time_start,3)} seconds")

print ("\nDisplaying evaluation graph...\n")
ced.draw_eval(ge)


# ce_fileout.save_game(game_pgn, pgn_outputfile)


# Exit
logging.info (f" Total execution time:\t{round(time.time() - time_start,3)} seconds")
print ("\nExiting on %s" % time.ctime())


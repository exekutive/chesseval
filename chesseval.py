''' ############################# INFO ##################################

    chesseval
    2026-JUN-16

    https://github.com/exekutive/chesseval
    
    Description:
        A Python program that uses the Stockfish engine to analyze the strengths of all the moves in a chess game,
        then plots the analysis on a graph. Chesseval does not generate moves.

    Usage:
        Type 'python chesseval.py --help' to get usage help.

        You can input your games four ways:
            1. Run the program and type or paste it in when prompted.
            2. Enter PGN move list using the '--game' command-line argument.
            3. Using a pipe (|) to send it via stdin in your terminal
            4. Import a PGN file using the  '--import <filepath>' command-line argument.

        Examples:
            python chesseval.py -v -g "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#"
            echo "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#" | python chesseval.py
            python chesseval.py -i "/mydocs/last nights game.pgn"

    Troubleshooting:
        Only main lines are analyzed. Variations are ignored.
        Multi-game PGN is not supported. Only the first game will be analyzed.

    Dependencies:
        Python v3.6 required for f strings (https://www.python.org/)
        Python v3.8 for debug logging
        Python v3.10 required for 'match' structure statement
        Matplotlib Python package (https://matplotlib.org/)
        Chess Python package (https://github.com/niklasf/python-chess)
        Stockfish chess analysis engine (https://stockfishchess.org/)

    Installation:
        1.  Install Python (https://docs.python.org/3/using/index.html)
        2.  Create a virtual environment and install the packages
            (https://packaging.python.org/en/latest/tutorials/installing-packages/)
        3.  Install Stockfish command line program
        4.  Type your Stockfish binary path into ce_config.py

    Configure Stockfish parameters in ce_config.py:
        -   Adjust the threads value: Your system's number of physical CPU cores is a good number
        -   Adjust the hash value: 70% - 80% of your system's RAM is a good starting point. (Value is specified in MiB.)
            According to Stockfish documentation: (https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html#analysis)
            "For deep analysis set it to as much as you can afford given the available memory in your system,
            leaving some memory for the operating system and other applications."
        -   depth: Limit the depth of analysis. (half-moves/plies). Can be specified per-game with command-line argument.
        -   time: Limit how long Stockfish spends analyzing a move (ms).  Can be specified per-game with command-line argument.

    PGN:
        What is it? https://en.wikipedia.org/wiki/Portable_Game_Notation
'''

import logging
import time
time_start = time.time()

import ce_config as cfg
import ce_input as cei
import ce_analyze as cea
import ce_draw as ced

# manually set verbosity here. Valid until (if) elevated by user args later
# logging.basicConfig (level = logging.INFO)

logging.info (" Started: %s\n" % time.ctime())

print ("\nStarting chesseval.py chess game evaluator.")
print ("http://github.com/exekutive/chesseval")
print ("Press Ctrl + C at any time to exit.\n")

cei.build_game()    
ge = cea.eval_game()
time_analyzed = time.time()
logging.info (f" Analysis time: {round(time.time() - time_start,3)} seconds")
ced.draw_eval(ge)

# ce_fileout.save_game(game_pgn, pgn_outputfile)

# Exit
logging.info (f" Total execution time:\t{round(time.time() - time_start,3)} seconds")
print ("\nExiting on %s" % time.ctime())


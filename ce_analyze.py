''' ############################# INFO ##################################
    
    ce_analyze.py
    
    Functions to manage the stockifish chess engine and use it to analyze
    the moves in an input game and return a formatted result.

    GLOBALS:
                cfg.game_input: The game object containing moves to be
                                analyzed
                            
                cfg.sf_options: Stockfish engine options like memory,
                                depth, etc.

                mate_eval
                
    FLOW:
    
        eval_game              
        │                      
        │(calls)               
        │                      
        └─►inst_engine   
        
    #####################################################################
'''

import logging
import chess
import chess.engine as ce

import ce_config as cfg

def inst_engine():
    # - - - - - - - 
    # FN inst_engine
    # description   : Spawns a stockfish chess engine instance
    # parameters    : None. Uses sf_options global from ce_config
    # returns       : chess.engine.SimpleEngine object

    global sf_options

    eng_inst = ce.SimpleEngine.popen_uci(cfg.sf_options['path'])
    logging.info (" Stockfish engine spawned.")

    eng_inst.configure({    "Threads":          cfg.sf_options['threads'],
                            "Hash":             cfg.sf_options['hash'],
                            "Debug Log File":   cfg.sf_options['log'],
                            "UCI_ShowWDL":      True})

    # eng_inst.configure({"SyzygyPath": syz_path})

    logging.info (" Stockfish engine configured.")

    return eng_inst

def eval_game():
    
    # - - - - - - - 
    # FN eval_game
    # description   : starts the engine, steps through game moves evaluating each one
    # parameters    : none. uses config globals game_input, sf_options, mate_eval
    # returns       : a dictionary with lists of move evaluations

    global sf_options
    global game_input
    global mate_eval
    
    eval_adv = []       # White player advantage in centipawns
    eval_exp  = []      # SF game outcome probability prediction
    eval_wdl_win = []   # White win probability
    eval_wdl_draw = []  # Draw probability
    eval_wdl_lose = []  # Black win probability
    
    sf_inst = inst_engine()
    
    print ("\nBeginning game evaluation ...")
    
    for number, mainline_node in enumerate(cfg.game_input.mainline()):

        logging.info(f" Evaluating node:\t{number}")

        move_eval = sf_inst.analyse(    mainline_node.board(),
                                        ce.Limit( depth = cfg.sf_options['depth'],
                                        time = cfg.sf_options['time'] / 1000 ))
        
        eval_adv.append(move_eval['score'].pov(chess.WHITE).score(mate_score = cfg.mate_eval))
        
        if mainline_node.board().is_game_over():
            logging.info(f" Final move:\t\t{mainline_node.move}")
            logging.info (" End of game.\n")

            # Stockfish does not provide WDL eval for game end moves, so revert to CP advantage based WDL calculation
            eval_exp.append(        move_eval['score'].wdl().white().expectation())
            eval_wdl_win.append(    move_eval['score'].wdl().white().winning_chance())
            eval_wdl_draw.append(   move_eval['score'].wdl().white().drawing_chance())
            eval_wdl_lose.append(   move_eval['score'].wdl().white().losing_chance())

        else: # normal move
            logging.info(f"\tmove:\t\t{mainline_node.move}\n")
            eval_exp.append(        move_eval['wdl'].white().expectation())
            eval_wdl_win.append(    move_eval['wdl'].white().winning_chance())
            eval_wdl_draw.append(   move_eval['wdl'].white().drawing_chance())
            eval_wdl_lose.append(   move_eval['wdl'].white().losing_chance())

    # wrap up analysis
    
    sf_inst.quit()
    logging.info (" Stockfish engine despawned.")
    print ("Analysis complete.")

    # compile and return results
    return  {
            "wdl"       : { 'Black'         : eval_wdl_lose,
                            'Draw'          : eval_wdl_draw,
                            'White'         : eval_wdl_win},
            "score"     : { 'Expectation'   : eval_exp,
                            'Advantage'     : eval_adv}
            }

    
# #   record analysis to PGN comment field:

# mainline_node.set_eval(move_analysis['score'], move_analysis['depth'])
# mainline_node.comment = (
# f"{mainline_node.comment} "
# f"WDL: {i_wdl_w:.2f}/{i_wdl_d:.2f}/{i_wdl_l:.2f} | " 
# f"Exp: {i_wdl_e:.2f}"
# )

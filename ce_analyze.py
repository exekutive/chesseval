''' ############################# INFO ##################################
    ce_analyze.py
    
    Functions to manage the stockifish chess engine and use it to analyze
    the moves in an input game and return a formatted result.

    GLOBALS:
                cfg.game_input: The game object containing moves to be
                                analyzed
                cfg.sf_options: Stockfish engine options like memory,
                                depth, etc.

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
    ''' descr   : Spawn a stockfish chess engine instance
        params  : None. Uses sf_options global from ce_config.py
        returns : chess.engine.SimpleEngine object '''
    
    global sf_options

    eng_inst = ce.SimpleEngine.popen_uci(cfg.sf_options['path'])
    logging.info (" Stockfish engine started.")

    eng_inst.configure({    "Threads":          cfg.sf_options['threads'],
                            "Hash":             cfg.sf_options['hash'],
                            "Debug Log File":   cfg.sf_options['log'],
                            "UCI_ShowWDL":      True})

    # eng_inst.configure({"SyzygyPath": syz_path})

    logging.info (  ' Stockfish configured:\n'
                    f'\t\tthreads\t: {cfg.sf_options['threads']}\n'
                    f'\t\tHash\t: {cfg.sf_options['hash']} MB\n'
                    f'\tLog file path\t: {cfg.sf_options['log']}\n' )

    return eng_inst

def flatten_adv( report:dict, cp_max:int ):
    ''' descr   : flatten scores of mate moves
        params  : report - game evaluation data,
                : cp_max - maximum centipawn advantage reached
        returns : none '''

    for l,m in enumerate(report['score']['Advantage']):
        if report['wdl']['Draw'][l] == 0:
            report['score']['Advantage'][l] = (m/abs(m)) * (cp_max + 10)

    logging.info(" Forced mate scores flattened")
    
    return

def eval_game():
    ''' descr   : starts the engine, steps through game moves evaluating each one
        params  : none. uses config globals game_input, sf_options
        returns : a dictionary with lists of move evaluations '''

    global sf_options
    global game_input
    
    eval_adv = []       # White player advantage in centipawns
    eval_exp  = []      # SF game outcome probability prediction
    eval_wdl_win = []   # White win probability
    eval_wdl_draw = []  # Draw probability
    eval_wdl_lose = []  # Black win probability
    eval_depth = []     # How deep the engine went for this move
    eval_time = []      # How long the engine spent evaluating the move
    
    adv_max = 0         # keeps track of maximum advantage reached

    sf_inst = inst_engine()

    print ("Beginning game analysis ...\n")


    logging.info (  ' Analysis parameters:\n'
                    f'\tGame length\t\t: {cfg.game_input.end().ply()} half-moves\n'
                    f'\tAnalysis depth limit\t: {cfg.sf_options['depth']} half-moves\n'
                    f'\tAnalysis time limit\t: {cfg.sf_options['time']} ms\n' )


    for number, mainline_node in enumerate(cfg.game_input.mainline()):

        logging.info(f" Evaluating node\t: {number}")
        logging.info(f" UCI Move\t\t: {mainline_node.move}")
        logging.info(f" Result\t\t: {mainline_node.board().result()}")

        move_eval = sf_inst.analyse(    mainline_node.board(),
                                        ce.Limit(
                                            depth = cfg.sf_options['depth'],
                                            time = cfg.sf_options['time'] / 1000 ),
                                            info = chess.engine.INFO_SCORE)
        
        # raw analysis report for debugging
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            with open("./debug_analysis.txt", "at") as debug_file:
                print(f"{number}\t{mainline_node.move}", file = debug_file)
                print(move_eval, file = debug_file)

        eval_adv.append(move_eval['score'].pov(chess.WHITE).score( mate_score = 100_000 ))


        if mainline_node.board().is_game_over():
            logging.info (" Ending move.\n")

            # Stockfish does not report all stats (time, wdl, depth=0) for end-game moves,
            # so use CP advantage to populate wdl values and make graph complete 
            eval_exp.append(        move_eval['score'].wdl().white().expectation())
            eval_wdl_win.append(    move_eval['score'].wdl().white().winning_chance())
            eval_wdl_draw.append(   move_eval['score'].wdl().white().drawing_chance())
            eval_wdl_lose.append(   move_eval['score'].wdl().white().losing_chance())

        else: # normal move
            eval_exp.append(        move_eval['wdl'].white().expectation())
            eval_wdl_win.append(    move_eval['wdl'].white().winning_chance())
            eval_wdl_draw.append(   move_eval['wdl'].white().drawing_chance())
            eval_wdl_lose.append(   move_eval['wdl'].white().losing_chance())
            eval_depth.append(      move_eval['depth'])
            eval_time.append(       move_eval['time'])

            if move_eval['score'].is_mate():
                logging.info(" Forced mate.\n")
            else:
                # rolling score maximum for normalizing later
                adv_max = max( adv_max, abs( move_eval['score'].pov(chess.WHITE).score()))
                logging.info(f" Maximum advantage\t: {adv_max} cP\n")

            
            # Annotations/comments for export
            mainline_node.set_eval( move_eval['score'], move_eval['depth'] )
            mainline_node.comment = (   f"{mainline_node.comment} "
                                        f"W{eval_wdl_win[-1]:.2f}/D{eval_wdl_draw[-1]:.2f}/L{eval_wdl_lose[-1]:.2f}"
                                        f"/X{eval_exp[-1]:.2f} "
                                        f"{move_eval['time']}s" )
                

    sf_inst.quit()
    logging.info (" Stockfish engine despawned.")

    print ("Evaluation complete.")

    eval_report =  {
        "wdl"       : { 'Black'         : eval_wdl_lose,
                        'Draw'          : eval_wdl_draw,
                        'White'         : eval_wdl_win},
        "score"     : { 'Expectation'   : eval_exp,
                        'Advantage'     : eval_adv},
        "analysis"  : { 'Depth'         : eval_depth,
                        'Time'          : eval_time}
            }

    flatten_adv( eval_report, adv_max )

    return eval_report
    
# chesseval
A free, open-source, Python program that analyzes chess games for improving skill. You input your game (PGN text) and the Stockfish chess engine analyzes the strengths of all the moves in the game. Chesseval then plots the analysis on a graph for a visual representation of how the board black/white advantage evolved. Chesseval does not generate moves.

### Instructions
Installation and usage instructions can be found in the [chesseval.py](chesseval.py) header.
You can also type 'python chesseval.py -h' to get usage help.

You will need:
* Familiarity with the command line environment
* Python 3 and a couple of modules
* Stockfish

### Features
* Three ways to input your games: direct entry at the prompt, command line argument, and `stdin`
* State-of-the-art game analysis provided by the worlds strongest artificial neural network chess engine: [Stockfish](https://stockfishchess.org/)
* Graphical output using Matplotlib, which can be saved to image files.
* Most common variables are exposed in [ce_config.py](ce_config.py) for easy user customization
* Easily define file paths, engine parameters like analysis depth and time, and even graph styles
<img src="https://stockfishchess.org/images/logo/icon_128x128@2x.webp" width="64">

### Interpreting results
The Stockfish Evaluation graphic combines several metrics into one chart. _Fig. 1_ shows an example of a game evaluation.

<img width="1116" height="620" alt="glucksberg-najdorf1930" src="https://github.com/user-attachments/assets/569a9baf-9452-4fbc-bd60-4691efd8ef5b" />

###### _(fig 1.) Glucksberg vs. Najdorf, 1930. “The Polish Immortal”_

###### `1.d4 f5 2.c4 Nf6 3.Nc3 e6 4.Nf3 d5 5.e3 c6 6.Bd3 Bd6 7.O-O O-O 8.Ne2 Nbd7 9.Ng5 Bxh2+ 10.Kh1 Ng4 11.f4 Qe8 12.g3 Qh5 13.Kg2 Bg1 14.Nxg1 Qh2+ 15.Kf3 e5 16.dxe5 Ndxe5+ 17.fxe5 Nxe5+ 18.Kf4 Ng6+ 19.Kf3 f4 20.exf4 Bg4+ 21.Kxg4 Ne5+ 22.fxe5 h5#`

#### White/Draw/Black Probabilities (area plot)
The stacked “mountains” in the background of the evaluation represent game outcome probabilities. To better understand , we can elarge a portion of the evaluation chart to focus on one moment in a game. (_fig. 2_). Use the probability scale on the vertical axis, which has divisions every 10%, to gauge the evaluation at this board position. The amount of vertical space occupied is the probability, not the absolute height. 

In this example, the white and black areas both occupy around 7% of the vertical scale, so those are the odds of them winning. The grey area is around 8.6 ticks high, so the odds of a draw are 86%. The probabilities always add up to 100% (7 + 86 + 7).

<img width="811" height="974" alt="stack" src="https://github.com/user-attachments/assets/4f0163e2-55fd-4a37-baff-431387e33d00" />

###### _(fig 2.) Zoomed on the probabilities stack plot of a game. Line plots are turned off for clarity._

#### Expected outcome  (line plot)
The “Expected Outcome” line plot simply represents who the winner is expected to be at each board position. 50% means a draw is expected. The closer the value is to 0%, the more strongly Black is favored, and values closer to 100% favor white.

#### Advantage (line plot)
Advantage (or Pawn score) is the traditional way of evaluating chess board positions. A zero pawn score means no player has an advantage. Positive values indicate White advantage, and negative values indicate Black has the advantage. In experienced play, a Pawn score of at least +/- 2.0 (equivalent to 200 centipawns) is typically considered a winning advantage.

### Contract
I made this program to help me play chess better. I am sharing it on the internet so you can download it too, but after that you are on your own.
If you find bugs, then I am grateful if you report them, and if they’re bad enough I might fix them. I will entertain feature suggestions, but I make no guarantees.

Enjoy.

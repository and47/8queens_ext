# program taking input from command line

import main
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


parser = ArgumentParser(description='Solve a chessboard puzzle',
                        formatter_class=ArgumentDefaultsHelpFormatter,
                        epilog='Example: \n python script.py 8 8 --queen 8')
parser.add_argument("w", type=int, help="Board dimensions: horizontal axis")
parser.add_argument("h", type=int, help="Board dimensions: vertical axis")

# 0 or 1 positional for each chess piece, with default 0
parser.add_argument("king", nargs='?', default=0, type=int, help="Number of kings (optional, positional)")
parser.add_argument("queen", nargs='?', default=0, type=int, help="Number of queens (optional, positional)")
parser.add_argument("bishop", nargs='?', default=0, type=int, help="Number of bishops (optional, positional)")
parser.add_argument("rook", nargs='?', default=0, type=int, help="Number of rooks (optional, positional)")
parser.add_argument("knight", nargs='?', default=0, type=int, help="Number of knights (optional, positional)")

# Optional named arguments for chess pieces, mapping to the same destination, also with 0 as default  more for clarity
# and documentation, as the positional arguments already ensure a default of 0
parser.add_argument("--king", dest="king", type=int, default=0, help="Number of kings (optional, named)")
parser.add_argument("--queen", dest="queen", type=int, default=0, help="Number of queens (optional, named)")
parser.add_argument("--bishop", dest="bishop", type=int, default=0, help="Number of bishops (optional, named)")
parser.add_argument("--rook", dest="rook", type=int, default=0, help="Number of rooks (optional, named)")
parser.add_argument("--knight", dest="knight", type=int, default=0, help="Number of knights (optional, named)")

# can capture more arguments for solving settings...

# Parse the command-line arguments
args_dict = vars(parser.parse_args())

task = main.Puzzle(**args_dict)
task.run_solver()  # in actual use can pass here "technical" arguments for custom options, etc.
print(task.count_layouts())

import os
import sys


"""
function to get user input and validate the input arguments
"""


def get_user_input():

    # initialize error messages list to store any validation errors
    error_msgs = []

    # check if the user provided exactly 3 parameters
    if len(sys.argv) != 4:
        print(
            "Usage: python3 2020310083_HW3.py input_file.txt [RM R | DM R | EDF U | EDF D]"
        )
        sys.exit(1)

    # get the arguments
    input_file = sys.argv[1]
    scheduling_algorithm = sys.argv[2]
    analysis = sys.argv[3]

    # check if the input file exists
    if not os.path.exists(input_file):
        error_msgs.append("Error: Input file does not exist.")

    # validate the scheduling algorithm, analysis type pair
    pair = scheduling_algorithm + " " + analysis
    if pair not in {"RM R", "DM R", "EDF U", "EDF D"}:
        error_msgs.append(
            "Error: Invalid [scheduling_algorithm analysis] pair. Choose from [RM R|DM R|EDF U|EDF D]."
        )

    # print all error messages and exit if any errors exist
    if error_msgs:
        for message in error_msgs:
            print(message)
        sys.exit(1)

    return input_file, scheduling_algorithm, analysis

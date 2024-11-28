import os
import sys


class Task:
    def __init__(self, period, wcet, deadline):
        self.period = period
        self.wcet = wcet
        self.relative_deadline = deadline
        self.absolute_deadline = deadline  # 1st absolute deadline


"""
Get user input and validate the input arguments
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


"""
Load the task sets from the input file
"""


def load_tasks(input_file):

    tasks = []
    with open(input_file, "r") as file:

        for i, line in enumerate(file):
            # skip empty lines
            line = line.strip()
            if not line:
                continue

            # read metadata from the first line
            if i == 0:
                metadata = line.split()[:3]
                num_tasks = int(metadata[0])
                is_constrained_deadline = int(metadata[2])

            # read task set from the subsequent lines
            data = list(map(int, line.split()[3:]))

            # create a task set from the data
            task_set = [
                Task(data[j * 3], data[j * 3 + 1], data[j * 3 + 2])
                for j in range(num_tasks)
            ]

            # append the task set to the tasks list
            tasks.append(task_set)

    return tasks, is_constrained_deadline

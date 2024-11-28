import os
import sys
import math


class Task:
    def __init__(self, index, period, wcet, deadline):
        self.index = index
        self.period = period
        self.wcet = wcet
        self.relative_deadline = deadline


class TasksetAnalyzer:
    """
    Initialize the taskset analyzer
    """

    def __init__(self, task_set, scheduling_algorithm, analysis):

        # sort the task based on the scheduling algorithm (no need to sort for EDF)
        if scheduling_algorithm == "RM":
            self.task_set = sorted(task_set, key=lambda task: (task.period, task.index))
        elif scheduling_algorithm == "DM":
            self.task_set = sorted(
                task_set, key=lambda task: (task.relative_deadline, task.index)
            )
        else:
            self.task_set = task_set

        # other attributes
        self.scheduling_algorithm = scheduling_algorithm
        self.analysis = analysis

    """
    Utilization bound analysis (only for EDF scheduling algorithm)
    """

    def utilization_bound_analysis(self):

        # calculate the sum of the utilization of all tasks
        sum_of_utilizations = sum(task.wcet / task.period for task in self.task_set)

        return "P" if sum_of_utilizations <= 1 else "F"

    """
    Response time analysis (for RM or DM scheduling algorithms)
    """

    def response_time_analysis(self):

        for i, task in enumerate(self.task_set):

            # initialize the response time to the task's WCET (R_i^0 = C_i)
            R_previous = task.wcet

            while True:

                # Calculate interference from higher priority tasks
                interference = sum(
                    math.ceil(R_previous / HP_task.period) * HP_task.wcet
                    for HP_task in self.task_set[:i]
                )

                # calculate the current step of response time
                R_current = task.wcet + interference

                # check the convergence and condition that R <= D (can be early stopped before converge)
                if R_current > task.relative_deadline:
                    return "F"
                elif R_current == R_previous:
                    break

                # update R_i^k to R_i^(k+1) for next while iteration
                R_previous = R_current

        return "P"

    """
    Processor Demand Criterion (only for EDF scheduling algorithm)
    """

    def processor_demand_criterion(self):

        # Find the hyperperiod of the task set (upperbound of the interval L)
        # TODO: What if the hyperperiod is too large? (> 100000)
        hyperperiod = math.lcm(*[task.period for task in self.task_set])

        # All possible interval candidates for interval L for efficiency
        interval_candidates = sorted(
            {
                task.relative_deadline + k * task.period
                for task in self.task_set
                for k in range(hyperperiod // task.period + 1)
                if task.relative_deadline + k * task.period <= hyperperiod
            }
        )

        # Iterate over all possible interval candidates and check if g(0, interval) <= interval
        for interval in interval_candidates:

            # Calculate the total demand g(0, interval)
            total_demand = sum(
                math.floor(
                    (interval - task.relative_deadline + task.period) / task.period
                )
                * task.wcet
                for task in self.task_set
            )

            # check if g(0, interval) <= interval, if not, the task set is not schedulable
            if total_demand > interval:
                return "F"

        return "P"

    """
    Analyze the task set and return the result
    """

    def analyze(self):
        if self.scheduling_algorithm == "EDF":
            if self.analysis == "U":
                return self.utilization_bound_analysis()
            else:  # D
                return self.processor_demand_criterion()
        else:  # RM or DM --> R
            return self.response_time_analysis()


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

    task_sets = []
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
                Task(index, data[index * 3], data[index * 3 + 1], data[index * 3 + 2])
                for index in range(num_tasks)
            ]

            # append the task set to the tasks list
            task_sets.append(task_set)

    return task_sets, is_constrained_deadline


"""
Generate the output file
"""


def generate_output_file(result):
    os.makedirs("./output", exist_ok=True)
    output_file = os.path.join("./output", "2020310083_HW3.txt")
    with open(output_file, "w") as file:
        for line in result:
            file.write(line + "\n")


def main():

    # validate the user input
    input_file, scheduling_algorithm, analysis = get_user_input()

    # load the task sets from the input file
    task_sets, is_constrained_deadline = load_tasks(input_file)

    # check if the deadline type is matched with scheduling algorithm, analysis pair
    deadline_type_mapping = {
        "EDF U": 1,
        "EDF D": 0,
        "RM R": 0,
        "DM R": 1,
    }

    if (
        deadline_type_mapping[scheduling_algorithm + " " + analysis]
        == is_constrained_deadline
    ):

        result = []
        for task_set in task_sets:
            taskset_analyzer = TasksetAnalyzer(task_set, scheduling_algorithm, analysis)
            result.append(taskset_analyzer.analyze())

        generate_output_file(result)

    else:
        print(
            f"Error: [scheduling_algorithm analysis] pair does not match with the deadline type."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import sys
import math
from multiprocessing import Pool
from functools import partial, reduce
from dataclasses import dataclass


@dataclass
class Task:
    """
    Represents a real-time task with timing constraints.

    Attributes:
        index (int): Unique identifier for the task
        period (int): Task's Period
        wcet (int): Task's Worst-Case Execution Time
        relative_deadline (int): Task's Relative Deadline
        utilization (float): Task's Utilization
    """

    index: int
    period: int
    wcet: int
    relative_deadline: int

    @property
    def utilization(self):
        return self.wcet / self.period


class TasksetAnalyzer:
    """
    Analyzes real-time task sets schedulability using different tests
    based on the scheduling algorithm and analysis method.

    Supports:
    - Implicit RM Response Time Analysis
    - Constrained DM Response Time Analysis
    - Implicit EDF Utilization Bound Analysis
    - Constrained EDF Processor Demand Criterion
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

    def utilization_bound_analysis(self):
        """
        Performs Implicit EDF utilization bound analysis.

        Returns:
            str: 'P' if schedulable (utilization ≤ 1), 'F' otherwise
        """

        return "P" if sum(task.utilization for task in self.task_set) <= 1 else "F"

    def response_time_analysis(self):
        """
        Performs Implicit RM or Constrained DM response time analysis.

        Iteratively calculates the worst-case response time for each task,
        considering interference from higher priority tasks.

        If task's converged response time is greater than its relative deadline,
        the task set is not schedulable.

        Returns:
            str: 'P' if schedulable, 'F' otherwise
        """

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

    def processor_demand_criterion(self):
        """
        Performs Explicit EDF processor demand criterion analysis.
        Uses min(hyperperiod, L*) as the upper bound for interval L.

        Returns:
            str: 'P' if schedulable, 'F' otherwise
        """
        # Calculate hyperperiod
        hyperperiod = reduce(
            lambda x, y: x * y // math.gcd(x, y),
            [task.period for task in self.task_set],
        )

        # Calculate L* = (sum((Ti - Di)Ui))/(1-U)
        total_utilization = sum(task.utilization for task in self.task_set)
        if total_utilization > 1:
            return "F"

        # cannot calculate L* if the total utilization is 1 (infinite L*)
        if total_utilization != 1:
            l_star = sum(
                (task.period - task.relative_deadline) * task.utilization
                for task in self.task_set
            ) / (1 - total_utilization)

            # Use the minimum of hyperperiod and L* as the upper bound
            upper_bound = min(hyperperiod, math.ceil(l_star))

        else:
            upper_bound = hyperperiod

        # All possible interval candidates up to the upper bound
        interval_candidates = sorted(
            {
                task.relative_deadline + k * task.period
                for task in self.task_set
                for k in range(upper_bound // task.period + 1)
                if task.relative_deadline + k * task.period <= upper_bound
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

    def analyze(self):
        """
        Analyzes the task set and returns the schedulability result.
        """

        if self.scheduling_algorithm == "EDF":
            if self.analysis == "U":
                return self.utilization_bound_analysis()
            else:  # D
                return self.processor_demand_criterion()
        else:  # RM or DM --> R
            return self.response_time_analysis()


def get_user_input():
    """
    Validates and processes command line arguments.

    Expected format:
    python3 script.py input_file.txt [RM R | DM R | EDF U | EDF D]

    Returns:
        tuple: (input_file, scheduling_algorithm, analysis)

    Raises:
        SystemExit: If validation fails
    """

    error_msgs = []

    # check if the user provided exactly 3 parameters
    if len(sys.argv) != 4:
        print(
            "Usage: python3 2020310083_HW3.py input_file.txt [RM R | DM R | EDF U | EDF D]"
        )
        sys.exit(1)

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

    if error_msgs:
        for message in error_msgs:
            print(message)
        sys.exit(1)

    return input_file, scheduling_algorithm, analysis


def load_tasks(input_file):
    """
    Load task sets from the input file.

    File format:
        First 3 elements each line: <num_of_tasks> <sum_of_utilization> <is_constrained_deadline>
        following elements each line: <period> <WCET> <relative_deadline>

    Returns:
        tuple: (list of task sets, is_constrained_deadline flag)
    """

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

            task_set = [
                Task(
                    index,  # index
                    data[index * 3],  # period
                    data[index * 3 + 1],  # WCET
                    data[index * 3 + 2],  # relative deadline
                )
                for index in range(num_tasks)
            ]

            task_sets.append(task_set)

    return task_sets, is_constrained_deadline


def generate_output_file(result):
    """
    Writes analysis results to output file.

    Args:
        result (list): List of schedulability results ('P' or 'F')

    Creates:
        ./output/2020310083_HW3.txt
    """

    os.makedirs("./output", exist_ok=True)
    output_file = os.path.join("./output", "2020310083_HW3.txt")
    with open(output_file, "w") as file:
        for line in result:
            file.write(line + "\n")


def analyze_task_set(task_set, scheduling_algorithm, analysis):
    """
    Analyzes a single task set using specified algorithm and method.

    Helper function for parallel processing.

    Args:
        task_set (list): List of Task objects
        scheduling_algorithm (str): 'RM', 'DM', or 'EDF'
        analysis (str): 'U', 'R', or 'D'

    Returns:
        str: Schedulability result ('P' or 'F')
    """

    analyzer = TasksetAnalyzer(task_set, scheduling_algorithm, analysis)
    return analyzer.analyze()


def main():
    """
    Main program entry point.

    Workflow:
    1. Validate input arguments
    2. Load task sets from input file
    3. Verify deadline type compatibility
    4. Analyze task sets in parallel
    5. Generate output file
    """

    input_file, scheduling_algorithm, analysis = get_user_input()

    task_sets, is_constrained_deadline = load_tasks(input_file)

    # check if the deadline type is matched with scheduling algorithm, analysis pair
    deadline_type_mapping = {
        "EDF U": 0,
        "EDF D": 1,
        "RM R": 0,
        "DM R": 1,
    }

    if (
        deadline_type_mapping[scheduling_algorithm + " " + analysis]
        == is_constrained_deadline
    ):

        result = []

        with Pool() as pool:

            # use partial to fix the unchanged arguments
            analyze_with_args = partial(
                analyze_task_set,
                scheduling_algorithm=scheduling_algorithm,
                analysis=analysis,
            )

            # Use pool.imap to analyze task sets with multiprocessing
            result = list(pool.imap(analyze_with_args, task_sets))

        generate_output_file(result)

    else:
        print(
            f"Error: [scheduling_algorithm analysis] pair does not match with the deadline type."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

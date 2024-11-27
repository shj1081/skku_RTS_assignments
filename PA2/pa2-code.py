import sys
import os
from functools import reduce
import math
from multiprocessing import Pool
from heapq import heappush, heappop, heapify
import time


class TaskScheduler:
    """
    function to initialize the task scheduler with the given task set and scheduling parameters
    """

    def __init__(self, task_set, scheduling_algorithm, preemptive):

        # scheduling parameters
        self.scheduling_algorithm = scheduling_algorithm
        self.preemptive = preemptive

        # task set parameters
        self.task_set = task_set
        self.num_tasks = len(task_set)
        self.periods = [task[0] for task in task_set]
        self.wcets = [task[1] for task in task_set]
        self.relative_deadlines = [task[2] for task in task_set]

        # initialize runtime parameters
        self.activation_times = [0] * self.num_tasks
        self.absolute_deadlines = self.relative_deadlines[:]
        self.remain_execution_times = self.wcets[:]
        self.next_activations = self.periods[:]
        self.is_active = [True] * self.num_tasks

        # put all tasks in the ready queue (synchronous activation)
        self.ready_queue = [
            (self.get_task_priority(i)[0], i) for i in range(self.num_tasks)
        ]
        heapify(self.ready_queue)
        self.current_task = None

    """
    function to get the priority of a task based on the scheduling algorithm
    """

    def get_task_priority(self, index):
        if self.scheduling_algorithm == "EDF":
            # min absolute deadline
            return self.absolute_deadlines[index], index
        elif self.scheduling_algorithm == "RM":
            # min period
            return self.periods[index], index
        elif self.scheduling_algorithm == "SJF":
            # min remaining execution time
            return self.remain_execution_times[index], index
        else:  # FCFS
            # earliest activation time
            return self.activation_times[index], index

    """
    function to update the task parameters for the next period
    """

    def next_period(self, current_time):
        for i in range(self.num_tasks):
            if current_time >= self.next_activations[i]:
                self.activation_times[i] = self.next_activations[i]
                self.absolute_deadlines[i] = (
                    self.activation_times[i] + self.relative_deadlines[i]
                )
                self.remain_execution_times[i] = self.wcets[i]
                self.is_active[i] = True
                self.next_activations[i] += self.periods[i]

                # Add to ready queue with updated priority
                heappush(self.ready_queue, (self.get_task_priority(i)[0], i))

    """
    function to execute a task for one time unit
    """

    def execute_task(self, index):
        self.remain_execution_times[index] -= 1

        # deactivate the task if execution is complete for the current period
        if self.remain_execution_times[index] <= 0:
            self.is_active[index] = False

    """
    function to calculate the hyperperiod (LCM of periods) of the task set
    https://labex.io/tutorials/python-calculating-least-common-multiple-13682
    """

    def calculate_hyperperiod(self):
        return reduce(lambda x, y: x * y // math.gcd(x, y), self.periods)

    """
    function to simulate the task scheduler
    ready queue is sorted based on the scheduling algorithm
    """

    def simulate(self):
        current_time = 0
        time_limit = min(self.calculate_hyperperiod(), 100000)

        while current_time < time_limit:
            # Check deadline misses
            missed_deadlines = []
            for i in range(self.num_tasks):
                if self.is_active[i] and current_time >= self.absolute_deadlines[i]:
                    missed_deadlines.append((self.get_task_priority(i)[0], i))

            if missed_deadlines:
                # Sort by priority and return the highest priority task index + 1
                return sorted(missed_deadlines)[0][1] + 1

            # Update tasks at their periods more efficiently
            self.next_period(current_time)

            # Non-preemptive scheduling
            if not self.preemptive:
                self._non_preemptive_step()

            # Preemptive scheduling
            else:
                self._preemptive_step()

            current_time += 1

        return 0

    """
    Non-preemptive scheduling logic.
    """

    def _non_preemptive_step(self):

        if self.current_task is not None:
            # Execute the current task
            self.execute_task(self.current_task)
            # Reset if task is not active
            if not self.is_active[self.current_task]:
                self.current_task = None
        elif self.ready_queue:
            # Pick the next task from the ready queue
            _, task_index = heappop(self.ready_queue)
            self.current_task = task_index
            self.execute_task(task_index)
            if not self.is_active[self.current_task]:
                self.current_task = None

    """
    Preemptive scheduling logic.
    """

    def _preemptive_step(self):
        # Remove completed tasks from queue
        while self.ready_queue and not self.is_active[self.ready_queue[0][1]]:
            heappop(self.ready_queue)
        if self.ready_queue:
            _, task_index = heappop(self.ready_queue)
            self.execute_task(task_index)
            if self.is_active[task_index]:
                heappush(
                    self.ready_queue,
                    (self.get_task_priority(task_index)[0], task_index),
                )


"""
function to load the task sets from the input file
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

            # read task set from the subsequent lines
            data = list(map(int, line.split()[3:]))
            task_set = [
                (data[j * 3], data[j * 3 + 1], data[j * 3 + 2])
                for j in range(num_tasks)
            ]

            # append the task set to the tasks list
            tasks.append(task_set)

    return tasks


"""
function to get user input and validate the input arguments
"""


def get_user_input():

    # initialize error messages list to store any validation errors
    error_msgs = []

    # check if the user provided exactly 3 parameters
    if len(sys.argv) != 4:
        print(
            "Usage: python3 2020310083_HW2.py input_file.txt [FCFS|SJF|RM|EDF] [p|np]"
        )
        sys.exit(1)

    # check if the input file exists
    if not os.path.exists(sys.argv[1]):
        error_msgs.append("Error: Input file does not exist.")

    # validate the scheduling algorithm
    if sys.argv[2] not in {"FCFS", "SJF", "RM", "EDF"}:
        error_msgs.append(
            "Error: Invalid scheduling algorithm. Choose from [FCFS|SJF|RM|EDF]."
        )

    # validate the priority type
    if sys.argv[3] not in {"p", "np"}:
        error_msgs.append("Error: Invalid priority type. Choose from [p|np].")

    # print all error messages and exit if any errors exist
    if error_msgs:
        for message in error_msgs:
            print(message)
        sys.exit(1)

    return sys.argv[1], sys.argv[2], sys.argv[3] == "p"


"""
function to process the task set using the task scheduler
used for multiprocessing
"""


def process_task_set(args):
    task_set, scheduling_algorithm, preemptive = args
    scheduler = TaskScheduler(task_set, scheduling_algorithm, preemptive)
    return scheduler.simulate()


"""
function to run the main program
"""


def main():

    # start the timer to measure the execution time
    start = time.time()

    # get user input and load the task sets from the input file
    input_file, scheduling_algorithm, preemptive = get_user_input()
    task_sets = load_tasks(input_file)

    # print information about the execution
    print(f"- Task sets loaded from {input_file}")
    print(f"- Scheduling algorithm: {scheduling_algorithm}")
    print(f"- Priority type: {'Preemptive' if preemptive else 'Non-preemptive'}\n")

    # create the output directory if it does not exist
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/2020310083_HW2.txt"

    # set the arguments for multiprocessing
    task_set_args = [
        (task_set, scheduling_algorithm, preemptive) for task_set in task_sets
    ]

    # process the task sets using multiprocessing using imap (efficient memory usage)
    results = []
    with Pool() as pool:
        for result in pool.imap(process_task_set, task_set_args):
            results.append(result)

    # with Pool() as pool:
    #     results = pool.map(process_task_set, task_set_args)

    # write the results to the output file
    with open(filename, "w") as file:
        for result in results:
            file.write(f"{result}\n")

    # stop the timer and print the execution time
    end = time.time()
    print(f"  Results written to {filename}")
    print(f"  {end - start:.2f} seconds elapsed.")

    return


if __name__ == "__main__":
    main()

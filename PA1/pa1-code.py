import sys
import random
import os

# Validate command line arguments
def validate_user_input():
    error_msg = [] 

    if len(sys.argv) != 4:
        print("Usage: python3 2020310083_hw1.py <n> <U> <v>")
        sys.exit(1)

    # number of tasks > 0 and integer
    try:
        number_of_tasks = int(sys.argv[1])
        if number_of_tasks <= 0:
            error_msg.append("Number of tasks (n) must be an integer greater than 0.")
    except ValueError:
        error_msg.append("Number of tasks (n) must be an integer greater than 0.")

    # sum of utilization > 0 and < 1 and float
    try:
        sum_of_utilization = float(sys.argv[2])
        if not (0 < sum_of_utilization < 1):
            error_msg.append("Sum of utilization (U) must be a float between 0 and 1.")
    except ValueError:
        error_msg.append("Sum of utilization (U) must be a float between 0 and 1.")

    # is_explicit_deadline = 0 or 1
    try:
        is_explicit_deadline = int(sys.argv[3])
        if is_explicit_deadline not in [0, 1]:
            error_msg.append("IS_EXPLICIT_DEADLINE (v) must be either 0 or 1.")
    except ValueError:
        error_msg.append("IS_EXPLICIT_DEADLINE (v) must be either 0 or 1.")
    
    # if there exists any error, print the error and exit
    if error_msg:
        for error in error_msg:
            print(error)
        sys.exit(1)

    return number_of_tasks, sum_of_utilization, is_explicit_deadline

# UUniFast algorithm that generates random utilization values for each task
# E. Bini and G. Buttazzo. 2005. Measuring the performance of schedulability tests
def uunifast_algo(number_of_tasks, sum_of_utilization):
    utilization_of_tasks = []
    sumU = sum_of_utilization
    for i in range(1, number_of_tasks):
        nextSumU = sumU * (random.random() ** (1 / (number_of_tasks - i))) 
        utilization_of_tasks.append(sumU - nextSumU) 
        sumU = nextSumU  
    utilization_of_tasks.append(sumU)

    return utilization_of_tasks

# Generate tasks with random periods, execution times, and deadlines
def generate_tasks(number_of_tasks, sum_of_utilization, is_explicit_deadline):
    utilizations_of_tasks = uunifast_algo(number_of_tasks, sum_of_utilization)
    tasks = []
    for u in utilizations_of_tasks:
        period = random.randint(100, 1000) # period is between 100 and 1000
        wcet = max(1, round(u * period))  # wcet must be > 0 and round to the nearest integer
        relative_deadline = period if is_explicit_deadline == 0 else random.randint(wcet, period)
        tasks.append((period, wcet, relative_deadline))
    return tasks


def main():
    # Get the arguments from the user
    number_of_tasks, sum_of_utilization, is_explicit_deadline = validate_user_input()

    # Create the output directory if it does not exist
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/2020310083_{number_of_tasks}_{sum_of_utilization}_{is_explicit_deadline}.txt"

    # Open the file (write mode) and write the task setss
    with open(filename, "w") as file:
        for i in range(100):
            tasks = generate_tasks(number_of_tasks, sum_of_utilization, is_explicit_deadline)
            file.write(f"{number_of_tasks} {sum_of_utilization} {is_explicit_deadline} ")
            for task in tasks:
                file.write(f"{task[0]} {task[1]} {task[2]} ")
            file.write("\n")
    
main()

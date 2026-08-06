import sys
import math
from decimal import Decimal

# Function to convert float values to int values with 0.001 accuracy -> ie. 1 -> 1000, 1.001 -> 1001, 1.002 -> 1002, etc.
def convert_to_time_units(value): 
    # convert value (0.001 accuracy) to int values so that we don't experience any rounding related issues with float values
    return int(Decimal(value) * 1000)

# Function for reading the workload files (.txt files)
def read_workload_file(filename):
    try:
        # try to open the file and read the contents within the file
        with open(filename, "r", encoding="utf-8") as workload_file:
            lines = workload_file.readlines()

        print("File loaded successfully")
        return lines

    # if unable to open and read file the file, an error is thrown indicating this
    except FileNotFoundError:
        print("File could not be found")
        return None


# assign priorities (highest priority = 0, lowest priority = n-1) to each task based on the RM scheduling algorithm
def assign_priorities(tasks):
    # sort the tasks based on period -> RM scheduling means shorter period = higher priority
    # in my simulator, if the periods (priorities) are the same, then lower task number = higher priority
    tasks_sorted_by_priority = sorted(tasks, key=lambda task: (task["period"], task["task_num"]))

    # for each priority, task in the sorted tasks, assign the priority to the task based on its index in the sorted list
    for priority, task in enumerate(tasks_sorted_by_priority):
        task["priority"] = priority

# based on the periods of the tasks in the workload, calculate the hyperperiod with LCM
def calculate_hyperperiod(tasks):
    # return the LCM of all periods in the workload as the hyperperiod
    periods = [task["period"] for task in tasks]
    return math.lcm(*periods)


# This function takes each line in the workload file and splits the values based on the comma separator locations and stores it into a dictionary list
def parse_tasks(lines):
    # start with empty dict
    tasks = []

    # for each line (starting from 0), go through each line for task_num and line values
    for task_num, line_vals in enumerate(lines, start=0):
        # strip line values of the whitespace(s)
        line_vals = line_vals.strip()

        # split the line vals into execution time, period, and deadline based on the comma separator locations
        exec_time, period, deadline = line_vals.split(",")
        exec_time = float(exec_time)
        period = float(period)
        deadline = float(deadline)

        # for each task, create a dict entry with execution time, 
        task = {
            "task_num": task_num,
            "exec_time": convert_to_time_units(exec_time),
            "period": convert_to_time_units(period),
            "deadline": convert_to_time_units(deadline)
        }

        # for each new task, append it to the tasks dictionary list
        tasks.append(task)

    return tasks

# Function that creates a job based on the release time and abs deadline of the task (all release times are 0 initially)
def create_job (task, release_time):
    return {
        "task_num": task["task_num"],
        "exec_time": task["exec_time"],
        "release_time": release_time,
        "abs_deadline": release_time + task["deadline"],
        "priority": task["priority"]
    }


# function that releases jobs based on the next release time of the task and the current time of the simulation
def release_jobs(tasks, next_release_time, current_time, ready_jobs):
    for task in tasks:
        task_num = task["task_num"]

        if next_release_time[task_num] <= current_time:
            release_time = next_release_time[task_num]
            ready_jobs.append(create_job(task, release_time))
            next_release_time[task_num] += task["period"]


def main():
    # restrict command line args to only have exactly 2 args
    if len(sys.argv) != 2:
        return

    # reading file name based on the command line arg
    workload_filename = sys.argv[1]
    lines =read_workload_file(workload_filename)

    # if there's no lines in the workload file
    if lines is None:
        return

    # parse the tasks from the workload file's lines, assign priorities based on RM, and calculate hyperperiod with LCM
    parsed_tasks = parse_tasks(lines)
    assign_priorities(parsed_tasks)
    hyperperiod = calculate_hyperperiod(parsed_tasks)

    next_release_time = [0] * len(parsed_tasks)  # initialize next release time for each task to 0
    ready_jobs = []  # initialize ready jobs list to store jobs that are ready to be executed

    current_time = 0

    # as long as the current time doesn't exceed the hyperperiod, release jobs based on the next release time
    # of the tasks and the current time of the simulation
    while current_time < hyperperiod:
        release_jobs(parsed_tasks, next_release_time, current_time, ready_jobs)
        current_time += min(next_release_time)

    for jobs in ready_jobs:
        print(jobs)

    # initialize jobs to indicate where they're release and where their deadline is
    # initial_jobs = []

    # for task in parsed_tasks:
    #     initial_jobs.append(create_job(task, 0))

    # print all initial jobs that get released as well as the calculated hyperperiod
    # print("Initial Jobs: ")
    # for job in initial_jobs:
    #         print(job)
    # print("Parsed tasks:")
    # for task in parsed_tasks:
    #     print(task)
    print("Hyperperiod:", hyperperiod)

if __name__ == "__main__":
    main()
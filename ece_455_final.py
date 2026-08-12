import sys
import math
from decimal import Decimal
import heapq

import time

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

        # print("File loaded successfully")
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
        "remaining_time": task["exec_time"],
        "release_time": release_time,
        "abs_deadline": release_time + task["deadline"],
        "priority": task["priority"],
    }

# function that releases jobs based on the next release time of the task and the current time of the simulation
def release_jobs(tasks, release_heap, current_time, ready_jobs, deadline_heap):
    while release_heap and release_heap[0][0] <= current_time:
        release_time, task_num = heapq.heappop(release_heap)

        task = tasks[task_num]
        job = create_job(task, release_time)

        heapq.heappush(ready_jobs, (job["priority"], job["release_time"], job["task_num"], job))
        heapq.heappush(deadline_heap, (job["abs_deadline"], job["task_num"], job["release_time"], job))

        next_release_time = release_time + task["period"]
        heapq.heappush(release_heap, (next_release_time, task_num))

# select the next job to execute according to priority
def select_next_job(ready_jobs):
    # empty queue of ready jobs
    if not ready_jobs:
        return None

    return ready_jobs[0][3]

    # return the job in the ready queue with the higheset priority (smallest value)
    return min(ready_jobs, key=lambda job: (job["priority"], job["release_time"]))

# calculates the time of the next event base on release time of next job, current time, and selected job's remaining time
def calc_next_event_time(release_heap, current_time, selected_job, deadline_heap):
    earliest_release_time = release_heap[0][0]

    # if no selected jobs, return the release time that is the soonest
    if selected_job is None:
        return earliest_release_time

    remove_compeleted_deadlines(deadline_heap)
    earliest_deadline = deadline_heap[0][0]

    # updated completion time to the current time with the reamining time of the selected job added to it
    completion_time = current_time + selected_job["remaining_time"]

    # return the smallest value our of the next release time, completion time, or hyperperiod
    return min(earliest_release_time, completion_time, earliest_deadline)

# function to detect if a deadline is ever missed (failed)
def detect_deadline_miss(deadline_heap, current_time):
    remove_compeleted_deadlines(deadline_heap)

    if deadline_heap and deadline_heap[0][0] <= current_time:
        return deadline_heap[0][3]

    return None

# state storing funciton that, upon call, stores information about the current state
def get_schedule_state(ready_jobs, current_time):
    state = []

    for job_entry in ready_jobs:
        job = job_entry[3]
        state.append((job["task_num"], job["remaining_time"], job["release_time"] - current_time, job["abs_deadline"] - current_time))

    return tuple(sorted(state))

def remove_compeleted_deadlines(deadline_heap):
    while deadline_heap and deadline_heap[0][3]["remaining_time"] == 0:
        heapq.heappop(deadline_heap)


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

    release_heap = []               # create a heap for released jobs and initialize them to (0, task_num)
    for task in parsed_tasks:
        heapq.heappush(release_heap, (0, task["task_num"]))

    ready_jobs = []  # initialize ready jobs list to store jobs that are ready to be executed
    deadline_heap = []

    current_time = 0
    feasible = True
    preemption_count = [0] * len(parsed_tasks)
    running_job = None

    # set of states that we check for repeated states
    seen_state = set()

    sim_start_time = time.perf_counter()
    
    while True:

        # constantly release jobs
        release_jobs(
            parsed_tasks,
            release_heap,
            current_time,
            ready_jobs,
            deadline_heap
        )

        missed_job = detect_deadline_miss(deadline_heap, current_time)

        if missed_job is not None:
            feasible = False
            break

        # check if we get to a repeated state
        if current_time % hyperperiod == 0:
            current_state = get_schedule_state(ready_jobs, current_time)

            if current_state in seen_state:
                # print(f"Scheduled state repeated at {current_time / 1000:.3f}")
                break

            seen_state.add(current_state)


        # choose the next job we need to execute based on the ready jobs and their priorities
        selected_job = select_next_job(ready_jobs)

        if (running_job is not None and selected_job is not None and selected_job is not running_job and current_time < hyperperiod):
            preemption_count[running_job["task_num"]] += 1

        running_job = selected_job

        # calculate the time of the next event
        next_event_time = calc_next_event_time(
            release_heap,
            current_time,
            selected_job,
            deadline_heap
        )

        # if a job is selected, then calcaulted the elapsed time and subtract it from the selected job's remaining time
        if selected_job is not None:
            elapsed_time = next_event_time - current_time
            selected_job["remaining_time"] -= elapsed_time

            # if the current job is done, remove it from select job list
            if selected_job["remaining_time"] == 0:
                heapq.heappop(ready_jobs)
                running_job = None

        # set the current time to the next event time for the next iteration of the loop
        current_time = next_event_time

    sim_stop_time = time.perf_counter()

    if feasible:
        print(1)
        print(",".join(str(individual_counts) for individual_counts in preemption_count))
    if not feasible:
        print(0)
        print()

    sim_time_elapsed = sim_stop_time - sim_start_time
    print(f"simulation run time: {sim_time_elapsed:.6f}s")

if __name__ == "__main__":
    main()
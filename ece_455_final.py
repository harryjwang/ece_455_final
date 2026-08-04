import sys

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
            "exec_time": exec_time,
            "period": period,
            "deadline": deadline
        }

        # for each new task, append it to the tasks dictionary list
        tasks.append(task)

    return tasks

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

    # parse the tasks from the workload file's lines 
    parsed_tasks = parse_tasks(lines)

    # print all parsed tasks obtianed from the workload file
    print("Parsed tasks:")
    for task in parsed_tasks:
        print(task)


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
import openpyxl
from enum import Enum
from collections import defaultdict
import os
import sys

# Constants
SHIFT_END_TIMES = [14, 14, 14, 15, 15, 15, 22, 7]  # End times for shifts: 6:00-14:00, 7:00-15:00, 14:00-22:00, 23:00-7:00
NUM_SHIFTS = len(SHIFT_END_TIMES)
SHIFT_HOURS = 12  # Required 12-hour separation

day_to_index = {
    "Sun": 0,
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6
}

def read_skillset_names(file_path):
    df = pd.read_excel(file_path)
    skills = df.iloc[:, 0].tolist()  # Skills are in the first column
    employees = df.columns[1:].tolist()  # Employees are in the remaining columns
    return skills, employees, df

def read_assignment(file_path):
    df = pd.read_excel(file_path, header=None)
    return df

def create_enums(skills, employees):
    Skills = Enum('Skills', {skill: i for i, skill in enumerate(skills)})
    Employees = Enum('Employees', {employee: i for i, employee in enumerate(employees)})
    return Skills, Employees

def create_adjacency_matrix_skillset(df, skills, employees):
    skill_mapping = {'NS': 0, 'CS': 1, 'PS': 2}
    num_skills = len(skills)
    num_employees = len(employees)

    # Initialize adjacency matrix with zeros
    adj_matrix = np.zeros((num_skills, num_employees), dtype=int)

    # Create a DataFrame that maps skill levels to integers
    skill_levels = df.iloc[:, 1:].replace(skill_mapping)

    # Fill adjacency matrix
    for i, skill in enumerate(skills):
        adj_matrix[i, :] = skill_levels.iloc[i].values

    return adj_matrix

def create_adjacency_matrix_assignment(df, num_days, skills, day_names):
    num_rows = df.shape[0] - 2  # Number of rows in df minus 2 (header and other adjustments)
    num_weeks = (num_days + 6) // 7  # Calculate how many weeks are needed to cover num_days

    # Create an extended matrix to cover all days of the month
    adj_matrix = np.full((num_rows, num_days), -1, dtype=object)

    skill_mapping = {i: skill for i, skill in enumerate(skills)}
    print("Skill Mapping:", skill_mapping)

    # Calculate the start index based on the first day of the month
    first_day = day_names[0]  # Get the first day name
    day_to_index = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
    start_index = day_to_index.get(first_day, 0)  # Get the start index for the first day of the month
    print("Start Index:", start_index)

    # Populate the matrix with weekly data, considering the start index
    for i in range(num_rows):
        for day_idx in range(num_days):
            week_day = (day_idx + start_index) % 7  # Adjust for start index
            task_data = df.iloc[i + 1, week_day + 1]  # Adjust for zero-based indexing
            if pd.notna(task_data):
                task_str = str(task_data).strip()
                if task_str == "-":
                    adj_matrix[i, day_idx] = [-1]
                else:
                    task_numbers = [int(num) for num in task_str.split(',') if num.isdigit()]
                    adjusted_tasks = [task_num - 1 for task_num in task_numbers]
                    adj_matrix[i, day_idx] = adjusted_tasks
            else:
                adj_matrix[i, day_idx] = [-1]

    print("Adjacency Matrix Shape:", adj_matrix.shape)
    print("Sample of Adjacency Matrix:", adj_matrix[:2, :])  # Print a sample for verification

    return adj_matrix



def read_preassigned_off_days(output_file, start_row, start_col, num_employees, num_days):
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active
    preassigned_off_matrix = []
    
    for r in range(start_row, start_row + num_employees):
        row_data = []
        for c in range(start_col, start_col + num_days):
            cell_value = ws.cell(row=r, column=c).value
            row_data.append(cell_value if cell_value else "")  # Handle empty cells
        preassigned_off_matrix.append(row_data)
    
    return preassigned_off_matrix

def get_next_valid_start_time(end_time):
    # Add 12 hours to the end time and wrap around if needed
    return (end_time + SHIFT_HOURS) % 24


def solve_scheduling_problem(skillset_matrix, assignment_matrix, headcount_row, num_employees, num_skills, output_file, preassigned_off_matrix, pre_scheduled_off_days, day_names):
    model = cp_model.CpModel()
    num_days = len(headcount_row)  # Number of days in the scheduling period
    num_slots = assignment_matrix.shape[0]  # Number of time slots
    days_per_week = 7

    # Variables for work assignments and off days
    work = {}
    headcount_deviation = [model.NewIntVar(0, num_employees, f'headcount_deviation_d{d}') for d in range(num_days)]
    off_days_type1 = {}  # "off" days
    off_days_type2 = {}  # "OFF" days

    # Find the starting index in weekly_headcount based on the first day in day_names
    start_day_name = day_names[0]
    first_weekday = day_to_index[start_day_name]
    end_day = first_weekday + (days_per_week - (first_weekday % days_per_week))
    print(end_day)


    # Pre-off day constraints
    #pre_off_array = [1,1,1,1,1,1,1,1]
    #pre_OFF_array = [1,1,1,1,1,1,1,1]

    #for e in range(num_employees):
    #    pre_off = pre_off_array[e]
    #    pre_off_ = pre_OFF_array[e]

    #    if pre_off == 0 and pre_off_ == 0:
    #        # Needs both "off" and "OFF"
    #        model.Add(sum(off_days_type1.get((e, d), 0) for d in range(first_weekday, end_day - 1)) >= 1)
    #        model.Add(sum(off_days_type2.get((e, d), 0) for d in range(first_weekday, end_day - 1)) >= 1)
    #    elif pre_off == 0:
    #        # Needs one "off" day
    #        model.Add(sum(off_days_type1.get((e, d), 0) for d in range(first_weekday, end_day - 1)) >= 1)
    #    elif pre_off_ == 0:
    #        # Needs one "OFF" day
    #        model.Add(sum(off_days_type2.get((e, d), 0) for d in range(first_weekday, end_day - 1)) >= 1)

    # Define work variables and handle pre-assigned off days
    for e in range(num_employees):
        for d in range(num_days):
            if preassigned_off_matrix[e][d] not in ["R", "V"]:
                for t in range(num_slots):
                    work[(e, d, t)] = model.NewBoolVar(f'work_e{e}_d{d}_t{t}')
            else:
                for t in range(num_slots):
                    work[(e, d, t)] = model.NewConstant(-1) # Special value for vacation

    for e in range(num_employees):
        for d in range(num_days):
            off_days_type1[(e, d)] = model.NewBoolVar(f'off1_e{e}_d{d}')
            off_days_type2[(e, d)] = model.NewBoolVar(f'off2_e{e}_d{d}')
            
            # Ensure that if "off" or "OFF" is true, the employee is not working on that day
            model.Add(sum(work.get((e, d, t), 0) for t in range(num_slots)) == 0).OnlyEnforceIf(off_days_type1[(e, d)])
            model.Add(sum(work.get((e, d, t), 0) for t in range(num_slots)) == 0).OnlyEnforceIf(off_days_type2[(e, d)])

    # Constraints

    # Ensure the total number of employees working on each day meets the headcount requirement
    for d in range(num_days):
        total_employees_working = sum(work.get((e, d, t), 0) for e in range(num_employees) for t in range(num_slots))
        model.Add(total_employees_working == headcount_row[d])

    # Define deviation constraints
    for d in range(num_days):
        total_employees_working = sum(work.get((e, d, t), 0) for e in range(num_employees) for t in range(num_slots))
        model.Add(total_employees_working >= headcount_row[d] - headcount_deviation[d])
        model.Add(total_employees_working <= headcount_row[d] + headcount_deviation[d])

    # Ensure each employee works exactly 5 days a week
    for e in range(num_employees):
        for week_start in range(0, num_days, days_per_week):
            # Adjust for the first day of the week
            adjusted_week_start = week_start - first_weekday
            if adjusted_week_start < 0:
                adjusted_week_start += days_per_week
            
            # Collect the work days for the current week using the adjusted week start
            week_work_days = [
                sum(work.get((e, (adjusted_week_start + d) % num_days, t), 0) for t in range(num_slots)) 
                for d in range(days_per_week)
            ]
            
            # Ensure exactly 5 work days per week
            model.Add(sum(week_work_days) >= 4)
            model.Add(sum(week_work_days) <= 5)

    # Ensure exactly one "off" day and one "OFF" day per week
    for e in range(num_employees):
        for week_start in range(0, num_days, days_per_week):
            # Adjust for the first day of the week
            adjusted_week_start = week_start - first_weekday
            if adjusted_week_start < 0:
                adjusted_week_start += days_per_week
            
            # Collect the off days for the current week using the adjusted week start
            week_off_days_type1 = [
                off_days_type1[(e, (adjusted_week_start + d) % num_days)] 
                for d in range(days_per_week)
            ]
            week_off_days_type2 = [
                off_days_type2[(e, (adjusted_week_start + d) % num_days)] 
                for d in range(days_per_week)
            ]

            # Ensure exactly one "off" day and one "OFF" day per week
            model.Add(sum(week_off_days_type1) == 1)
            model.Add(sum(week_off_days_type2) == 1)

    
    # Ensure "off" and "OFF" are not assigned on the same day
    for e in range(num_employees):
        for d in range(num_days):
            model.Add(off_days_type1[(e, d)] + off_days_type2[(e, d)] <= 1)


    # Compute skill scores for prioritizing employees with CS (level 1)
    def compute_skill_scores(skillset_matrix, num_employees, priority_skill_level):
        skill_scores = [0] * num_employees
        for skill in range(skillset_matrix.shape[0]):
            for employee in range(num_employees):
                if skillset_matrix[skill][employee] == priority_skill_level:
                    skill_scores[employee] += 1
        return skill_scores

    # Define priority skill level (CS)
    priority_skill_level = 1

    # Compute scores for prioritizing employees with CS
    skill_scores = compute_skill_scores(skillset_matrix, num_employees, priority_skill_level)

    # Sort employees by skill scores (highest priority first)
    sorted_employees = sorted(range(num_employees), key=lambda e: skill_scores[e], reverse=True)

    # Ensure all required slots are covered
    for d in range(num_days):
        for t in range(num_slots):
            if assignment_matrix[t, d] != [-1]:  # Check if slot is required
                total_assigned_to_slot = sum(work.get((e, d, t), 0) for e in range(num_employees))
                model.Add(total_assigned_to_slot >= 1)  # At least one employee should be assigned to this slot

    # Ensure at least one employee with each required skill is assigned
    for d in range(num_days):
        for t in range(num_slots):
            if assignment_matrix[t, d] != [-1]:
                required_skills = assignment_matrix[t, d]
                model.Add(
                    sum(
                        work.get((e, d, t), 0)
                        for e in range(num_employees)
                        if any(skillset_matrix[skill][e] == priority_skill_level for skill in required_skills if skill >= 0 and skill < num_skills)
                    ) >= 1
                )

    # Ensure at least one employee with the skill levels (1 or 2) is assigned
    for d in range(num_days):
        for t in range(num_slots):
            if assignment_matrix[t, d] != [-1]:
                required_skills = assignment_matrix[t, d]
                model.Add(
                    sum(
                        work.get((e, d, t), 0)
                        for e in sorted_employees
                        if all(skillset_matrix[skill][e] in [1, 2] for skill in required_skills if skill >= 0 and skill < num_skills)
                    ) >= 1
                )

    # Constraint: Ensure employees have at least 12 hours between shifts
    for e in range(num_employees):
        for d in range(num_days):
            for t1 in range(num_slots):
                for t2 in range(num_slots):
                    if t1 != t2:
                        end_time_t1 = SHIFT_END_TIMES[t1]
                        start_time_t2 = SHIFT_END_TIMES[t2]
                        if start_time_t2 < end_time_t1:
                            start_time_t2 += 24  # Wrap around if needed
                        
                        min_time_between_shifts = 12
                        if end_time_t1 + min_time_between_shifts > start_time_t2:
                            model.Add(work.get((e, d, t1), 0) + work.get((e, d, t2), 0) <= 1)


    # Objective: Minimize the total work while ensuring a balance of shifts
    model.Minimize(sum(work.get((e, d, t), 0) for e in range(num_employees) for d in range(num_days) for t in range(num_slots)))
    model.Minimize(sum(headcount_deviation[d] for d in range(num_days)))


    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 180000  # Set a time limit
    status = solver.Solve(model)

    # Print the solution for debugging
    for e in range(num_employees):
        for week_start in range(0, num_days, days_per_week):
            week_end = min(week_start + days_per_week, num_days)
            print(f"Employee {e}, Week {week_start + 1}:")
            for d in range(week_start, week_end):
                if solver.Value(off_days_type1[(e, d)]):
                    print(f"  Off day: {d + 1}")
                if solver.Value(off_days_type2[(e, d)]):
                    print(f"  OFF day: {d + 1}")

    # Debugging: Print out the status of the solution
    if status == cp_model.OPTIMAL:
        print("Optimal schedule found.")
    elif status == cp_model.FEASIBLE:
        print("A feasible solution exists but is not optimal.")
    else:
        print("No optimal solution found.")
        

    # If a solution was found, write the results to Excel
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # Load the existing Excel workbook
        wb = openpyxl.load_workbook(output_file)
        ws = wb.active
        
        # Initialize matrix to store results
        result_matrix = [['' for _ in range(num_days)] for _ in range(num_employees)]

        num_working_employees = [0] * num_days  # Initialize list to track number of working employees per day

        assignments_by_day = defaultdict(list)
        

        for e in range(num_employees):
            for d in range(num_days):
                if preassigned_off_matrix[e][d] == "V":  # Special value for vacation
                    result_matrix[e][d] = "V"
                elif solver.Value(off_days_type1.get((e, d), 0)):
                    result_matrix[e][d] = "off"  # Pre-assigned off day
                elif solver.Value(off_days_type2.get((e, d), 0)):
                    result_matrix[e][d] = "OFF"  # Solver-determined off day
                else:
                    slot_assigned = False
                    for t in range(num_slots):
                        if solver.Value(work.get((e, d, t), 0)):
                            # Determine the time slot based on t
                            time_slot_value = {0: 6, 1: 6, 2: 6, 3: 7, 4: 7, 5: 7, 6: 14, 7: 23}.get(t, "")
                            result_matrix[e][d] = time_slot_value
                            num_working_employees[d] += 1
                            slot_assigned = True
                            
                            # Add to assignments by day
                            assignments_by_day[d].append(f"Employee {e} at time slot {t} (Time: {time_slot_value})")
                            break
                    
                    if not slot_assigned:
                        result_matrix[e][d] = ''  # Leave empty if no slot is assigned or if there's an error

        # Print out assignments sorted by day
        for d in range(num_days):
            print(f"Day {d}:")
            if assignments_by_day[d]:
                for assignment in assignments_by_day[d]:
                    print(f"  {assignment}")
            else:
                print("  No assignments")

        
        # Check headcount and add comments for errors
        for d in range(num_days):
            print("Compare", num_working_employees[d])
            print("With", headcount_row[d])
            if num_working_employees[d] < headcount_row[d]:
                error_message = "H.E"
                ws.cell(row=9, column=7 + d, value=error_message)

        # Write results to Excel
        for e in range(num_employees):
            for d in range(num_days):
                cell_value = result_matrix[e][d]
                cell_row = 10 + e  # Adjusted to start from row 10
                cell_col = 4 + d  # Adjusted to start from column D (4th column)
                
                existing_value = ws.cell(row=cell_row, column=cell_col).value
                if existing_value in [None, ""]:  # Only write if the cell is empty
                    ws.cell(row=cell_row, column=cell_col, value=cell_value)
        
        # Save the workbook
        wb.save(output_file)

        return "Successfully created schedule"
    else:
        return "Failed to create schedule."



def get_day_names_from_pandas(file_path, sheet_name='Original', start_col='D', end_col='AH', row=7):
    """Retrieve day names from an Excel range using pandas."""
    # Load the specified columns into a DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, usecols=f'{start_col}:{end_col}')
    
    # Extract the specified row with dates
    dates_row = df.iloc[row - 1].values
    print("Extracted dates (excluding first three days):", dates_row)

    # Convert to datetime objects and then to day names
    day_names = []
    for date in dates_row:
        if pd.isna(date) or date == '':
            day_names.append('')  # Handle NaN/NaT values
        else:
            try:
                # Convert the value to a datetime object if it's a string
                if isinstance(date, str):
                    dt = pd.to_datetime(date, errors='coerce')
                else:
                    dt = pd.to_datetime(date)
                # Handle coercion result and append the day name
                if pd.isna(dt):
                    day_names.append('')
                else:
                    day_names.append(dt.strftime('%a'))
            except Exception as e:
                print(f"Error converting date {date}: {e}")
                day_names.append('')

    return day_names

def create_full_month_headcount(assignment_df, day_names, num_days):
    # Extract headcount for Monday to Sunday (7 entries)
    weekly_headcount = assignment_df.iloc[9, 1:8].tolist()
    
    # Find the starting index in weekly_headcount based on the first day in day_names
    start_day_name = day_names[0]
    start_index = day_to_index[start_day_name]
    
    # Rotate the weekly headcount to start from the correct day
    rotated_headcount = weekly_headcount[start_index:] + weekly_headcount[:start_index]
    
    # Extend the rotated weekly pattern to cover all num_days (e.g., 31 days)
    full_month_headcount = (rotated_headcount * (num_days // 7)) + rotated_headcount[:num_days % 7]
    
    return full_month_headcount

def print_adjacency_matrix(adj_matrix, days):
    print("Adjacency Matrix:")
    for i, row in enumerate(adj_matrix):
        day_strs = []
        for day_idx, cell in enumerate(row):
            if isinstance(cell, list):
                if cell[0] == -1:
                    formatted_cell = "-"
                else:
                    formatted_cell = f"[{', '.join(map(str, cell))}]"
            else:
                formatted_cell = "-"
            day_strs.append(formatted_cell)
        print(f"Row {i + 1}: {', '.join(day_strs)}")


constants_folder = os.path.join(os.path.dirname(__file__), 'constants')
output_folder = os.path.join(os.path.dirname(__file__), 'output')

def run(output_file):
    # Get the output file path from command-line arguments

    # Access a constant spreadsheet
    skillset_file_path = os.path.join(constants_folder, 'Staff_Skillset.xlsx')

    assignment_file_path = os.path.join(constants_folder, 'assignment.xlsx')
    
    skills, employees, skillset_df = read_skillset_names(skillset_file_path)
    assignment_df = read_assignment(assignment_file_path)

    days = assignment_df.iloc[0, 1:].tolist()
    day_names = get_day_names_from_pandas(output_file)

    pre_scheduled_off_days = [2, 0, 1, 2, 1, 1, 2, 1]
    
    # Create headcount row
    headcount_row = create_full_month_headcount(assignment_df, day_names, len(day_names))
    print(day_names)
    print(headcount_row)
    
    # Create enums
    Skills, Employees = create_enums(skills, employees)
    
    # Create adjacency matrices
    skillset_matrix = create_adjacency_matrix_skillset(skillset_df, skills, employees)
    assignment_matrix = create_adjacency_matrix_assignment(assignment_df, num_days=len(day_names), skills=skills, day_names=day_names)
    
    print_adjacency_matrix(assignment_matrix, len(day_names))

    # Read preassigned off days
    preassigned_off_matrix = read_preassigned_off_days(output_file, start_row=10, start_col=4, num_employees=len(employees), num_days=len(day_names))
    
    # Solve scheduling problem
    result_string = solve_scheduling_problem(skillset_matrix, assignment_matrix, headcount_row, len(employees), len(skills), output_file, preassigned_off_matrix, pre_scheduled_off_days, day_names)

    return result_string

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_final_refix.py <assignment_file>")
        sys.exit(1)

    # Get the output file path from command-line arguments
    output_file = sys.argv[1]

    # Access a constant spreadsheet
    skillset_file_path = os.path.join(constants_folder, 'Staff_Skillset.xlsx')

    assignment_file_path = os.path.join(constants_folder, 'assignment.xlsx')
    
    skills, employees, skillset_df = read_skillset_names(skillset_file_path)
    assignment_df = read_assignment(assignment_file_path)

    days = assignment_df.iloc[0, 1:].tolist()
    day_names = get_day_names_from_pandas(output_file)

    pre_scheduled_off_days = [2, 0, 1, 2, 1, 1, 2, 1]
    
    # Create headcount row
    headcount_row = create_full_month_headcount(assignment_df, day_names, len(day_names))
    print(day_names)
    print(headcount_row)
    
    # Create enums
    Skills, Employees = create_enums(skills, employees)
    
    # Create adjacency matrices
    skillset_matrix = create_adjacency_matrix_skillset(skillset_df, skills, employees)
    assignment_matrix = create_adjacency_matrix_assignment(assignment_df, num_days=len(day_names), skills=skills, day_names=day_names)
    
    print_adjacency_matrix(assignment_matrix, len(day_names))

    # Read preassigned off days
    preassigned_off_matrix = read_preassigned_off_days(output_file, start_row=10, start_col=4, num_employees=len(employees), num_days=len(day_names))
    
    # Solve scheduling problem
    solve_scheduling_problem(skillset_matrix, assignment_matrix, headcount_row, len(employees), len(skills), output_file, preassigned_off_matrix, pre_scheduled_off_days, day_names)

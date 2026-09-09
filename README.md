# Bakery Automated Mechanism (BAM)

A Python-based bakery production scheduling system developed for **Gate Gourmet Japan** (in course CDEV3300)

BAM was designed to automate and simplify the generation of bakery production schedules, replacing repetitive manual scheduling work with a structured optimisation-based workflow.

## Overview

Bakery production involves coordinating multiple products, production requirements, time constraints, and available resources. Managing these schedules manually can become time-consuming and difficult as the number of tasks increases.

The **Bakery Automated Mechanism (BAM)** was developed to streamline this process by processing production data and automatically generating an organised bakery schedule.

The project combines:

* Python-based data processing
* Constraint-based scheduling and optimisation
* Excel file processing
* Automated schedule generation
* A standalone Windows executable for easier deployment

## Features

* Automatically generates bakery production schedules
* Processes operational data from Excel spreadsheets
* Uses optimisation techniques to allocate production tasks
* Reduces repetitive manual scheduling work
* Exports results into an organised spreadsheet format
* Includes a standalone Windows executable
* Includes user documentation for operation and setup

## Technologies

**Language**

* Python

**Libraries / Tools**

* Google OR-Tools
* pandas
* NumPy
* openpyxl
* XlsxWriter
* PyInstaller

OR-Tools is used for the scheduling and optimisation component, while pandas and Excel-related libraries are used for processing and generating production data.

## Repository Structure

```text
Bakery-Automated-Mechanism/
│
├── _internal/
│   └── Runtime files required by the packaged application
│
├── Bakery Automated Mechanism.exe
│   └── Standalone Windows executable
│
├── User Documentation for Bakery Automated Mechanism (BAM).docx
│   └── User guide and operating instructions
│
├── install_modules.bat
│   └── Installs the required Python dependencies
│
└── requirements.txt
    └── Python package dependencies
```

## Running the Application

### Option 1 — Windows Executable

For normal use, run:

```text
Bakery Automated Mechanism.exe
```

The packaged executable allows BAM to be used without manually running the Python environment.

### Option 2 — Install Python Dependencies

If working with the Python environment, ensure Python and `pip` are installed.

Run:

```batch
install_modules.bat
```

Alternatively:

```bash
pip install -r requirements.txt
```

The installation script automatically checks for Python and installs the packages defined in `requirements.txt`.

## How It Works

At a high level, BAM follows the following workflow:

```text
Production Data
      │
      ▼
Data Processing
      │
      ▼
Scheduling Constraints
      │
      ▼
Optimisation Engine
      │
      ▼
Generated Production Schedule
      │
      ▼
Excel Output
```

Production information is processed and converted into scheduling constraints. The optimisation system then determines an appropriate production schedule before exporting the result for operational use.

## Project Motivation

This project was created to solve a real operational scheduling problem.

Rather than manually organising bakery production activities, BAM provides a repeatable software-based scheduling process that can reduce scheduling effort and improve consistency.

The project also provided practical experience in:

* Translating operational requirements into software
* Designing scheduling constraints
* Applying optimisation algorithms to a real-world problem
* Processing structured spreadsheet data
* Building software for non-technical end users
* Packaging Python applications for deployment

## Documentation

Detailed usage instructions are available in:

```text
User Documentation for Bakery Automated Mechanism (BAM).docx
```

## Status

**Completed**

The scheduling system has been developed and packaged into a standalone Windows application.

## Author

**Leo**

Electrical Engineering / Computer Science
University of New South Wales

---

*Developed as a practical software solution for bakery production scheduling at Gate Gourmet Japan.*

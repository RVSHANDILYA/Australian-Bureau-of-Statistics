# Australian Bureau of Statistics Data Analysis

**Note:** This repository demonstrates proficiency in Python programming, data analysis, and statistical computation without relying on external libraries, showcasing fundamental programming skills and mathematical understanding.

## Table of Contents
- [Overview](#overview)
- [Project 1: Australian Demographics Analysis](#project-1-australian-demographics-analysis)
- [Project 2: Population Statistics Analysis](#project-2-population-statistics-analysis)
- [Technologies Used](#technologies-used)
- [File Structure](#file-structure)
- [How to Run](#how-to-run)
- [Key Learning Outcomes](#key-learning-outcomes)
- [Debugging Documentation](#debugging-documentation)
- [Performance Characteristics](#performance-characteristics)
- [Contributing](#contributing)

## Overview

This repository contains two comprehensive Python projects focusing on analyzing Australian demographic and population data. Both projects demonstrate advanced data processing, statistical analysis, and algorithmic problem-solving skills using only core Python features (no external libraries).

The projects work with real-world Australian Bureau of Statistics (ABS) data, processing CSV files containing population information across different statistical areas (SA2, SA3) and states, providing valuable insights for urban planning and resource allocation decisions.

## Project 1: Australian Demographics Analysis

### Objective
Develop a data analysis tool that processes Australian population datasets to generate statistical insights for government and urban planning decisions.

### Key Features
- **Age Group Classification:** Automatically identifies age groups containing specific target ages
- **SA3 Population Statistics:** Calculates mean and standard deviation for population data within Statistical Area Level 3 regions
- **State-Level Analysis:** Identifies SA3 areas with highest populations for specific age groups across all Australian states
- **Correlation Analysis:** Computes Pearson correlation coefficients between age distributions of different SA2 regions

### Core Outputs
1. **Age Bounds:** Lower and upper bounds of age groups (e.g., [25, 29] or [85, None])
2. **SA3 Statistics:** Mean and standard deviation calculations for target age groups
3. **State Maximums:** Highest population SA3 areas per state with proportional analysis
4. **Correlation Coefficient:** Statistical relationship between two SA2 regions' age distributions

### Technical Implementation
- **Data Validation:** Robust input validation for age parameters and SA2 codes
- **CSV Processing:** Efficient parsing of large demographic datasets
- **Statistical Calculations:** Implementation of Pearson correlation and standard deviation formulas
- **Error Handling:** Graceful handling of missing data, zero variance cases, and file errors

### Sample Usage
```python
age_bounds, sa3_stats, state_max_sa3, correlation = main(
    'SampleData_Areas.csv', 
    'SampleData_Populations.csv', 
    25, 
    '401011001', 
    '401021003'
)
```

## Project 2: Population Statistics Analysis

### Objective
Analyze population and area statistics for Australian regions, focusing on demographic patterns and regional similarities across different administrative levels.

### Key Features
- **Multi-Level Analysis:** Comprehensive analysis across State, SA3, and SA2 administrative levels
- **Population Thresholds:** Filters analysis based on minimum population requirements (150,000+)
- **Similarity Detection:** Uses cosine similarity to identify regions with similar demographic profiles
- **Data Cleaning:** Advanced data validation and duplicate removal across multiple datasets

### Core Outputs
1. **OP1 - Maximum Populations:** Identifies State, SA3, and SA2 with largest populations for each age group
2. **OP2 - Regional Analysis:** Finds largest SA2 areas within qualifying SA3 regions, including population totals and age distribution standard deviations
3. **OP3 - Similarity Analysis:** Discovers pairs of SA2 areas with most similar age distributions using **cosine similarity**

### Technical Implementation
- **Advanced Data Structures:** Nested dictionaries for efficient multi-level data organization
- **Cosine Similarity Algorithm:** Mathematical implementation for demographic comparison
- **Population Normalization:** Percentage-based analysis for fair regional comparisons
- **Threshold Filtering:** Dynamic filtering based on population and area count criteria

### Sample Usage
```python
OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')
```

### Sample Output Structure
```python
# OP1: Age group analysis
{
    '0-9': ['western australia', 'wanneroo', 'baldivis - south'],
    '20-29': ['western australia', 'stirling', 'adelaide']
}

# OP2: Regional statistics  
{
    '4': {'40304': ['403041072', 16431, 483.8303]},
    '5': {'50503': ['505031099', 25259, 1002.5155]}
}

# OP3: Similarity analysis
{
    'wanneroo': ['carramar', 'landsdale', 0.9975],
    'onkaparinga': ['aldinga', 'seaford rise - moana', 0.9992]
}
```

## Technologies Used

- **Python 3:** Core programming language
- **File I/O:** CSV processing without external libraries
- **Data Structures:** Lists, dictionaries, sets for efficient data management
- **Mathematical Algorithms:** 
  - Pearson correlation coefficient
  - Sample standard deviation
  - Cosine similarity
- **String Processing:** Case-insensitive data handling and normalization

## File Structure

```
├── 24944809_project1.py          # Project 1 implementation
├── 24944809_project2.py          # Project 2 implementation
├── SampleData_Areas.csv          # Project 1 area data
├── SampleData_Populations.csv    # Project 1 population data
├── SampleData_Areas_P2.csv       # Project 2 area data
├── SampleData_Populations_P2.csv # Project 2 population data
└── README.md                     # This file
```

## How to Run

### Prerequisites
- Python 3.x installed on your system
- Sample CSV data files in the same directory

### Running Project 1
```python
# In Python shell or script
from project1 import main

age_bounds, sa3_stats, state_max_sa3, correlation = main(
    'SampleData_Areas.csv',
    'SampleData_Populations.csv', 
    18,                    # Target age
    '401011001',          # First SA2 code
    '401021003'           # Second SA2 code
)

print("Age bounds:", age_bounds)
print("SA3 statistics:", sa3_stats)
print("State analysis:", state_max_sa3)
print("Correlation:", correlation)
```

### Running Project 2
```python
# In Python shell or script
from project2 import main

OP1, OP2, OP3 = main(
    'SampleData_Areas_P2.csv',
    'SampleData_Populations_P2.csv'
)

print("Age group maximums:", OP1)
print("Regional analysis:", OP2)
print("Similarity analysis:", OP3)
```

## Key Learning Outcomes

### Programming Skills Developed
- **Advanced File Processing:** Efficient handling of large CSV datasets
- **Data Structure Optimization:** Strategic use of dictionaries and lists for performance
- **Algorithm Implementation:** From-scratch implementation of statistical formulas
- **Error Handling:** Comprehensive input validation and graceful error management
- **Code Organization:** Modular function design and clear documentation

### Statistical Concepts Applied
- **Descriptive Statistics:** Mean, standard deviation calculations
- **Correlation Analysis:** Understanding relationships between datasets
- **Similarity Metrics:** Cosine similarity for demographic comparison
- **Data Normalization:** Percentage-based analysis for fair comparisons

### Data Science Fundamentals
- **Data Cleaning:** Handling missing values, duplicates, and invalid entries
- **Multi-dimensional Analysis:** Working with hierarchical administrative data
- **Performance Optimization:** Minimizing data traversal and computational complexity

## Debugging Documentation

Both projects include comprehensive debugging documentation covering significant issues encountered during development:

### Project 1 Debug Examples
- **State Name Case Sensitivity:** Resolved inconsistent string casing in state aggregation
- **Empty CSV Values:** Implemented defensive programming for missing population data
- **Zero Variance Correlation:** Added checks for identical distributions to prevent division by zero

### Project 2 Debug Examples
- **Sample Standard Deviation:** Fixed division by zero for single data points
- **Cosine Similarity Edge Cases:** Handled zero-magnitude vectors in similarity calculations
- **Floating Point Precision:** Resolved early rounding issues affecting final accuracy

### Key Debugging Lessons
- **Defensive Programming:** Always validate input data types and handle edge cases
- **Numerical Stability:** Consider mathematical edge cases in statistical calculations
- **Data Type Consistency:** Ensure proper type conversion when reading from CSV files
- **Early vs. Late Rounding:** Maintain precision throughout calculations, round only final outputs

## Performance Characteristics

- **Time Complexity:** Optimized to O(n) for most operations where n is the number of records
- **Memory Efficiency:** Uses dictionaries for O(1) lookup times
- **Scalability:** Designed to handle large CSV files with thousands of records
- **Robustness:** Comprehensive error handling for real-world data inconsistencies


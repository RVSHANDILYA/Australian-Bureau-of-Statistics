def main(area_csv_path, population_csv_path, target_age, sa2_code_1, sa2_code_2):
    """
    Main function to analyze Australian demographic data.

    Parameters:
    - area_csv_path (str): File path to the area data CSV.
    - population_csv_path (str): File path to the population data CSV.
    - target_age (int): Age to locate in the age distribution.
    - sa2_code_1 (str): First SA2 region code.
    - sa2_code_2 (str): Second SA2 region code.

    Returns:
    - age_bounds (list): Lower and upper age bounds of the group containing the target age.
    - sa3_stats (list): Mean and standard deviation for the target age group within SA3s.
    - state_max_sa3 (list): SA3 with highest proportion of the target age group for each state.
    - correlation (float): Pearson correlation of age distributions between the two SA2 regions.
    """
    #-------------------------------------------------------------------------------------------#

    # Step 1: Validate target age input (let's ensure that it is a non-negative integer)
    try:
        target_age = int(target_age)
        if target_age < 0:
            print("Error: Age must be a non-negative integer.")
            return None
    except ValueError:
        print("Error: Age must be a valid integer.")
        return None

    # Step 2: Validate SA2 codes (let's ensure that they are strings and valid 9-digit codes)
    for sa2_code in [sa2_code_1, sa2_code_2]:
        if not isinstance(sa2_code, str):
            sa2_code = str(sa2_code)      # Convert to string if not already
        if not sa2_code.strip().isdigit() or len(sa2_code.strip()) != 9:
            print(f"Error: SA2 code '{sa2_code}' is invalid. It must be exactly 9 digits.")
            return None

    # Remove leading/trailing whitespace 
    sa2_code_1 = sa2_code_1.strip()
    sa2_code_2 = sa2_code_2.strip()

    # Step 3: Read area and population data from the provided CSV files
    try:
        with open(area_csv_path, "r") as file:
            area_lines = [line.strip() for line in file if line.strip()]
        with open(population_csv_path, "r") as file:
            population_lines = [line.strip() for line in file if line.strip()]
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return None
    except Exception as e:
        print(f"Error reading files: {e}")
        return None

    # Ensure the CSV files contain at least headers and one data row
    if len(area_lines) < 2 or len(population_lines) < 2:
        print("Error: Input files must contain headers and at least one data row.")
        return None

    # Step 4: Extract age group headers from the population CSV (starts from column 3)
    try:
        header_columns = population_lines[0].split(",")
        age_group_labels = [label.strip() for label in header_columns[2:]]
    except Exception as e:
        print(f"Error parsing population CSV headers: {e}")
        return None

    # Step 5: Match the target age to the correct age group
    age_group_label, above_age_limit = match_age_to_group(target_age, age_group_labels)
    if age_group_label is None:
        print("Age group not found.")
        return None

    try:
        age_group_index = age_group_labels.index(age_group_label)  # Find the index of the matched age group
    except ValueError:
        print("Error locating age group in headers.")
        return None

    # Step 6: Parse the area data (SA2 to SA3 mapping, SA3 to state mapping)
    try:
        sa2_to_sa3, sa3_to_state, sa3_to_name, state_to_sa3_map = parse_area_data(area_lines)
    except Exception as e:
        print(f"Error processing area mappings: {e}")
        return None
    
    #----------------------------------------------------------------------------------------------#


# --- Output 1: Determine age group bounds --- #
    try:
        age_bounds = [None, None]  # Default value
        for lower in range(0, 90, 5):
            upper = lower + 4
            if lower <= target_age <= upper or (lower == 85 and target_age >= 85):
                age_bounds = [lower, None if lower == 85 else upper]
                break  # we will exit the loop once we find the matching range
    except Exception as e:
        print(f"Error determining age group bounds: {e}")
        age_bounds = [None, None]

    # --- Output 2: Calculate the SA3 Mean and Std deviation for the target age group --- #
    sa3_stats = []
    for sa2_code in [sa2_code_1, sa2_code_2]:  # Process both input SA2 regions
        # Get SA3 region that contains this SA2 region
        sa3_code = sa2_to_sa3.get(sa2_code)
        if not sa3_code:
            # If SA2 doesn't map to an SA3, store zeros for stats
            sa3_stats.append([sa2_code, 0.0, 0.0])
            continue

        # we will find all SA2 regions that belong to this SA3 region
        same_sa3_sa2s = [k for k, v in sa2_to_sa3.items() if v == sa3_code]
        age_group_counts = []

        # process the population data for all SA2s in this SA3
        for line in population_lines[1:]:  # Skip header row
            try:
                columns = line.split(",")
                sa2 = columns[0].strip()
                if sa2 in same_sa3_sa2s:
                    # Get population count for our target age group
                    age_value = int(columns[age_group_index + 2].strip() or 0)
                    age_group_counts.append(age_value)
            except Exception:
                age_group_counts.append(0)

        # calculate statistics for this SA3 region
        if age_group_counts:
            mean_value = sum(age_group_counts) / len(age_group_counts)
            if len(age_group_counts) > 1:
                # we will calculate sample standard deviation (using n-1)
                variance = sum((x - mean_value) ** 2 for x in age_group_counts) / (len(age_group_counts) - 1)
                std_dev = variance ** 0.5
            else:
                std_dev = 0.0  # we can't calculate std dev with single value
        else:
            mean_value = std_dev = 0.0

        # we will store the SA3 code with rounded statistics
        sa3_stats.append([sa3_code, round(mean_value, 4), round(std_dev, 4)])

    # --- Output 3: Identify SA3 with highest proportion of target age group in each state ---
    try:
        # we use dictionaries to store aggregated population data
        sa3_age_group_total = {}  # total population in target age group per SA3
        sa3_population_total = {}  # total population across all age groups per SA3

        # Aggregate population data for each SA3 region
        for line in population_lines[1:]:
            try:
                columns = line.split(",")
                sa2 = columns[0].strip()
                sa3 = sa2_to_sa3.get(sa2)
                if not sa3:
                    continue
                # Get count for our target age group
                age_count = int(columns[age_group_index + 2].strip() or 0)
                # Calculate total population across all age groups
                total_pop = sum(int(x.strip() or 0) for x in columns[2:] if x.strip().isdigit())
                # Accumulate the totals for this SA3
                sa3_age_group_total[sa3] = sa3_age_group_total.get(sa3, 0) + age_count
                sa3_population_total[sa3] = sa3_population_total.get(sa3, 0) + total_pop
            except Exception:
                continue

        # Find the SA3 with highest count of target age group in each state
        state_max_sa3 = []
        for state in sorted(state_to_sa3_map.keys()):
            max_sa3 = None
            max_age_count = -1
            # let's check all SA3 regions in this state
            for sa3 in state_to_sa3_map[state]:
                age_total = sa3_age_group_total.get(sa3, 0)
                # will track SA3 with highest count (using SA3 code as tiebreaker)
                if age_total > max_age_count or (age_total == max_age_count and sa3 < max_sa3):
                    max_age_count = age_total
                    max_sa3 = sa3
            # let's calculate proportion of population in target age group
            total = sa3_population_total.get(max_sa3, 0)
            proportion = max_age_count / total if total else 0.0
            # Store state, SA3 name, and proportion
            state_max_sa3.append([state, sa3_to_name.get(max_sa3, ""), round(proportion, 4)])
    except Exception as e:
        print(f"Error calculating state statistics: {e}")
        return None

    # --- Output 4: Calculate Pearson Correlation between age distributions of the two SA2 regions ---
    try:
        age_dist_1 = age_dist_2 = None
        # We will find and extract age distribution data for both SA2 regions
        for line in population_lines[1:]:
            columns = line.split(",")
            sa2 = columns[0].strip()
            if sa2 == sa2_code_1:
                age_dist_1 = [int(x.strip() or 0) for x in columns[2:]]  # All age groups for SA2 1
            if sa2 == sa2_code_2:
                age_dist_2 = [int(x.strip() or 0) for x in columns[2:]]  # All age groups for SA2 2

        # Validate we have comparable distributions
        if not age_dist_1 or not age_dist_2 or len(age_dist_1) != len(age_dist_2):
            correlation = 0.0
        else:
            n = len(age_dist_1)
            mean1 = sum(age_dist_1) / n  # Mean of SA2 1's distribution
            mean2 = sum(age_dist_2) / n  # Mean of SA2 2's distribution
            
            # Check for zero variance cases (all values identical)
            if all(x == mean1 for x in age_dist_1) or all(y == mean2 for y in age_dist_2):
                correlation = 0.0
            else:
                # Calculate Pearson correlation coefficient
                numerator = sum((x - mean1) * (y - mean2) for x, y in zip(age_dist_1, age_dist_2))
                denominator = (sum((x - mean1) ** 2 for x in age_dist_1) * sum((y - mean2) ** 2 for y in age_dist_2)) ** 0.5
                correlation = round(numerator / denominator if denominator else 0.0, 4)
    except Exception as e:
        print(f"Error calculating correlation: {e}")
        return None

    # Return all calculated outputs:
    # 1. Age group bounds (e.g., [25, 29])
    # 2. SA3 statistics for both input SA2 regions
    # 3. State-level statistics for target age group
    # 4. Correlation between the two SA2 regions' age distributions
    return age_bounds, sa3_stats, state_max_sa3, correlation


def match_age_to_group(age, age_group_labels):
    """
    This function matches a specific age to its corresponding age group label.

    Parameters:
    - age (int): Age to be classified.
    - age_group_labels (list): List of age group strings from CSV header.

    Returns:
    - (str, bool): Tuple of matched age group label and open-ended status (e.g., 85+).
    """
    for label in age_group_labels:
        try:
            # Check for the open-ended age group like "85 and over"
            if "85 and over" in label.lower():
                if age >= 85:
                    return label, True
                continue
            range_clean = "".join(c if c.isdigit() or c == "-" else "" for c in label)
            bounds = range_clean.split("-")
            if len(bounds) == 2 and bounds[0].isdigit() and bounds[1].isdigit():
                low = int(bounds[0])
                high = int(bounds[1])
                if low <= age <= high:
                    return label, False
        except:
            continue
    return None, False


def parse_area_data(area_lines):
    """
    we will extract mapping dictionaries from the area (CSV data).

    Parameters:
    - area_lines (list): Rows from the area data CSV.

    Returns:
    - Tuple:
        sa2_to_sa3 (dict): Maps SA2 code to SA3 code.
        sa3_to_state (dict): Maps SA3 code to state name.
        sa3_to_name (dict): Maps SA3 code to SA3 name.
        state_to_sa3_map (dict): Maps state name to list of SA3 codes.
    """
    sa2_to_sa3 = {}
    sa3_to_state = {}
    sa3_to_name = {}
    state_to_sa3_map = {}
    seen_sa2_codes = set()

    # Process each line in the area data CSV
    for line in area_lines[1:]:
        try:
            fields = line.split(",")
            if len(fields) < 5:
                continue
            state_name = fields[1].strip().lower()
            sa3_code = fields[2].strip()
            sa3_name = fields[3].strip().lower()
            sa2_code = fields[4].strip()
            if sa2_code in seen_sa2_codes:
                continue
            seen_sa2_codes.add(sa2_code)

            # Populate mapping dictionaries
            sa2_to_sa3[sa2_code] = sa3_code
            sa3_to_state[sa3_code] = state_name
            sa3_to_name[sa3_code] = sa3_name
            state_to_sa3_map.setdefault(state_name, []).append(sa3_code)
        except:
            continue

    # Remove duplicates and sort SA3s per state
    for state in state_to_sa3_map:
        state_to_sa3_map[state] = sorted(set(state_to_sa3_map[state]))

    return sa2_to_sa3, sa3_to_state, sa3_to_name, state_to_sa3_map


'''
Debugging Documentation:

Issue 1 (Date: 4 April 2025 ):
Error Description: Incorrect SA3-to-State Mapping
The program failed to correctly aggregate SA3 regions by state due to case sensitivity in state name 
comparisons.

Erroneous Code Snippet:
    state_name = fields[1].strip().lower()  
    sa3_to_state[sa3_code] = state_name    

Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 25, '401011001', '401021003')
# Expected: Group all "South Australia" SA3s together  
# Actual: "south australia" and "South Australia" treated as separate states

Root Cause:
State names in state_to_sa3_map used inconsistent casing (e.g., "South Australia" vs "south australia").
This caused incorrect aggregation in state_max_sa3 calculations.

Fix:
state_name = fields[1].strip().lower()  # Normalize to lowercase early
state_to_sa3_map.setdefault(state_name, []).append(sa3_code)  # Consistent keys

Reflection: 
Learned to normalize string keys for dictionaries when performing aggregations. 
Added case conversion during initial data parsing.

---

Issue 2 (Date: 6 April 2025 ):
Error Description: 
Empty Age Group Values in Population Data
The code crashed when encountering empty/missing values in population age groups.

Erroneous Code Snippet: 
age_value = int(columns[age_group_index + 2].strip())  (no handling for empty strings)

Test Case: 
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 30, '402041039', '402041042')
# Input data contained ",," for empty age groups in Dry Creek areas

Error Manifestation:
ValueError: invalid literal for int() with base 10: ''

Fix:
age_value = int(columns[age_group_index + 2].strip() or 0)  # Default to 0 for empty values

Reflection: 
Implemented defensive programming for CSV parsing. Now treats missing data as zero population, 
which matches the problem requirements.

---

"""
Issue 3 (Date: 8 April 2025):

Error Description: 
ZeroDivisionError during Pearson Correlation calculation.
When comparing two SA2 regions with **identical age distributions**, the denominator in the 
Pearson correlation formula became zero due to **zero variance** in both datasets.

Erroneous Code Snippet:
    denominator = (sum((x - mean1)**2 for x in age_dist_1) * 
                   sum((y - mean2)**2 for y in age_dist_2)) ** 0.5
    correlation = numerator / denominator

Test Case:
    main('SampleData_Areas.csv', 'SampleData_Populations.csv', 20, '401011001', '401011001')
    # This compares an SA2 region with itself, resulting in identical distributions.

Error Manifestation:
    ZeroDivisionError: float division by zero

Fix:
    # Added a zero-variance check before computing the correlation
    if all(x == mean1 for x in age_dist_1) or all(y == mean2 for y in age_dist_2):
        correlation = 0.0
    else:
        correlation = round(numerator / denominator if denominator else 0.0, 4)

Reflection:
I learned that when working with real-world data, statistical calculations must consider edge cases
like zero variance.and adding a pre-check for uniform data distributions prevents runtime errors and 
produces meaningful default output (0.0 correlation).

'''

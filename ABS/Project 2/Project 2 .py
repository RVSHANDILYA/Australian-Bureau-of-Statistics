"""This code analyses Population and area statistics for Australian regions:
first we read two CSV files:
1. Area information relating to SA2s, SA3, and States
2. SA2s population data by age group

Three outputs are produced by it:
OP1: Which State, SA3, and SA2 have the biggest populations for each age group?
OP2: The largest SA2, its population, and the sample standard deviation of its age counts for each State -> SA3 
(if SA3 total population >= 150,000).
OP3: The pair of SA2s with the most similar age distributions (cosine similarity) for each SA3 with at least 15 SA2s
"""

def read_area_file(area_filename):
    #Reads the area CSV and returns a list of area rows (dicts).
    """
    Reads the population CSV file and returns a list of population records.
    Args:
        pop_filename (str): Path to the population CSV file.
    Returns:
        List[dict]: List of population records, each dict has keys:
                    'sa2 name', 'sa2 code', 'age', 'population'.
                    Returns empty list if file can't be read or is empty.
    """

    area_rows = []
    try:
        with open(area_filename, encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
        if not lines:
            return []
    except IOError:
        return []

    header = [col.lower() for col in lines[0].split(",")]
    for line in lines[1:]:
        values = [val.strip() for val in line.split(",")]
        row = dict(zip(header, values))
        # Normalise column names
        if "s_t code" in row:
            row["state code"] = row["s_t code"]
        if "s_t name" in row:
            row["state name"] = row["s_t name"]
        area_rows.append(row)
    return area_rows

def read_population_file(pop_filename):
    #Reads the population CSV and returns a list of population records (dicts)
    """
    Reads the population CSV file and returns a list of population records.
    Args:
        pop_filename (str): Path to the population CSV file.
    Returns:
        List[dict]: List of population records, each dict has keys:
                    'sa2 name', 'sa2 code', 'age', 'population'.
                    Returns empty list if file can't be read or is empty.
    """

    pop_rows = []
    try:
        with open(pop_filename, encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
        if not lines:
            return []
    except IOError:
        return []

    header = [col.strip() for col in lines[0].split(",")]
    for line in lines[1:]:
        row = dict(zip(header, [val.strip() for val in line.split(",")]))
        sa2_name = row.get("Area_Name_Level2", "").lower()
        sa2_code = row.get("Area_Code_Level2", "").lower()
        # Each age column is a separate record
        for col in header[2:]:
            age_label = col.lower().replace("age ", "").replace(" and over", "-None")
            if "-" not in age_label:
                continue
            pop_val = row.get(col, "")
            if not pop_val:
                continue
            try:
                count = int(pop_val)
                if count < 0:
                    continue
            except ValueError:
                continue
            pop_rows.append({
                "sa2 name": sa2_name,
                "sa2 code": sa2_code,
                "age": age_label,
                "population": count,
            })
    return pop_rows

def clean_data(area_rows, pop_rows):
    # Retains only records that appear in both area and pop files. Removes duplicates.
    """
    Retains only records present in both area and population data, and removes duplicates.
    Args:
        area_rows (list[dict]): List of area records.
        pop_rows (list[dict]): List of population records.
    Returns:
        Tuple[List[dict], List[dict]]: Two lists - cleaned area records and cleaned population records.
    """

    sa2_code_to_area = {}
    for row in area_rows:
        sa2_code_to_area[row["sa2 code"].lower()] = row

    seen = set()
    cleaned_areas = []
    cleaned_pops = []
    for record in pop_rows:
        code = record["sa2 code"]
        age = record["age"]
        if code not in sa2_code_to_area:
            continue
        key = code + age
        if key in seen:
            continue
        seen.add(key)
        # Attach correct SA2 name (from pop)
        area_row = sa2_code_to_area[code].copy()
        area_row["sa2 name"] = record["sa2 name"]
        cleaned_areas.append(area_row)
        cleaned_pops.append(record)
    return cleaned_areas, cleaned_pops


def create_area_lookup(area_rows):
    # Builds a lookup from SA2 name to info about State, SA3, and codes.
    """
    Builds a lookup dictionary mapping SA2 names to related State, SA3 names and their codes.
    Args:
        area_rows (list[dict]): List of cleaned area records.
    Returns:
        dict: Dictionary mapping lowercase SA2 name to dictionary of related info including:
              'state name', 'sa3 name', 'state code', 'sa3 code', 'sa2 code'.
    """

    lookup = {}
    for area in area_rows:
        key = area["sa2 name"].lower()
        lookup[key] = {}
        lookup[key]["state name"] = area["state name"].lower()
        lookup[key]["sa3 name"] = area["sa3 name"].lower()
        lookup[key]["state code"] = area["state code"].lower()
        lookup[key]["sa3 code"] = area["sa3 code"].lower()
        lookup[key]["sa2 code"] = area["sa2 code"].lower()
    return lookup


def output_OP1(pop_rows, area_lookup):
    # For every age group, finds which State, SA3, and SA2 has the largest population
    """
    For every age group, finds which State, SA3, and SA2 has the largest population.
    Args:
        pop_rows (list[dict]): List of cleaned population records.
        area_lookup (dict): Lookup dictionary mapping SA2 names to area info.
    Returns:
        dict: Mapping age group to list of [state, sa3, sa2] with the largest population.
    """

    results = {}
    for record in pop_rows:
        age = record["age"]
        sa2 = record["sa2 name"].lower()
        if sa2 not in area_lookup:
            continue
        state = area_lookup[sa2]["state name"]
        sa3 = area_lookup[sa2]["sa3 name"]
        pop = record["population"]

        if age not in results:
            results[age] = {"state": {}, "sa3": {}, "sa2": {}}

        for level, name in (("state", state), ("sa3", sa3), ("sa2", sa2)):
            if name not in results[age][level]:
                results[age][level][name] = 0
            results[age][level][name] += pop

    op1 = {}
    for age in results:
        # Find max state(s)
        max_state_value = None
        max_states = []
        for k in results[age]["state"]:
            v = results[age]["state"][k]
            if (max_state_value is None) or (v > max_state_value):
                max_state_value = v
                max_states = [k]
            elif v == max_state_value:
                max_states.append(k)
        max_states.sort()
        max_state = max_states[0]

        # Find max sa3(s)
        max_sa3_value = None
        max_sa3s = []
        for k in results[age]["sa3"]:
            v = results[age]["sa3"][k]
            if (max_sa3_value is None) or (v > max_sa3_value):
                max_sa3_value = v
                max_sa3s = [k]
            elif v == max_sa3_value:
                max_sa3s.append(k)
        max_sa3s.sort()
        max_sa3 = max_sa3s[0]

        # Find max sa2(s)
        max_sa2_value = None
        max_sa2s = []
        for k in results[age]["sa2"]:
            v = results[age]["sa2"][k]
            if (max_sa2_value is None) or (v > max_sa2_value):
                max_sa2_value = v
                max_sa2s = [k]
            elif v == max_sa2_value:
                max_sa2s.append(k)
        max_sa2s.sort()
        max_sa2 = max_sa2s[0]

        op1[age] = [max_state, max_sa3, max_sa2]
    return op1


def calculate_sample_sd(numbers):
    # Returns the sample standard deviation for a list of numbers.
    """
    Calculates the sample standard deviation of a list of numbers.
    Args:
        numbers (list[int]): List of numerical values.
    Returns:
        float: Sample standard deviation rounded to 4 decimal places.
               Returns 0.0 if less than two data points.
    """

    n = 0
    for i in numbers:
        n += 1
    if n < 2:
        return 0.0

    # Calculate mean
    total = 0.0
    for x in numbers:
        total += x
    mean = total / n

    # Calculate variance (sum of squared differences)
    squared_diff_sum = 0.0
    for x in numbers:
        squared_diff = (x - mean) * (x - mean)
        squared_diff_sum += squared_diff

    variance = squared_diff_sum / (n - 1)

    # Calculate standard deviation
    std = variance ** 0.5
    return round(std, 4)


def output_OP2(pop_rows, area_lookup):
    # For every State -> SA3 (with total pop >= 150,000), finds the largest SA2 
    # its population and the sample SD of its age distribution.
    """
    For every State -> SA3 (with total population >= 150,000), finds the largest SA2,
    its population and the sample standard deviation of its age distribution.
    Args:
        pop_rows (list[dict]): List of cleaned population records.
        area_lookup (dict): Lookup dictionary mapping SA2 names to area info.
    Returns:
        dict: Nested dictionary mapping state_code to dictionaries mapping sa3_code to
              [largest_sa2_code, population, sample_std_dev].
    """


    structure = {}
    for record in pop_rows:
        sa2 = record["sa2 name"].lower()
        if sa2 not in area_lookup:
            continue
        state_code = area_lookup[sa2]["state code"]
        sa3_code = area_lookup[sa2]["sa3 code"]
        sa2_code = area_lookup[sa2]["sa2 code"]
        age = record["age"]
        pop = record["population"]
        if state_code not in structure:
            structure[state_code] = {}
        if sa3_code not in structure[state_code]:
            structure[state_code][sa3_code] = {}
        if sa2_code not in structure[state_code][sa3_code]:
            structure[state_code][sa3_code][sa2_code] = {}
        structure[state_code][sa3_code][sa2_code][age] = pop

    op2 = {}
    state_codes = []
    for s_code in structure:
        state_codes.append(s_code)
    state_codes.sort(key=str)

    for state_code in state_codes:
        op2[state_code] = {}
        for sa3_code in structure[state_code]:
            total_pop = 0
            for sa2_code in structure[state_code][sa3_code]:
                ages = structure[state_code][sa3_code][sa2_code]
                sa2_total = 0
                for value in ages.values():
                    sa2_total += value
                total_pop += sa2_total
            if total_pop < 150000:
                continue


            max_pop = None
            biggest_sa2s = []
            for sa2_code in structure[state_code][sa3_code]:
                ages = structure[state_code][sa3_code][sa2_code]
                sa2_total = 0
                for value in ages.values():
                    sa2_total += value
                if (max_pop is None) or (sa2_total > max_pop):
                    max_pop = sa2_total
                    biggest_sa2s = [sa2_code]
                elif sa2_total == max_pop:
                    biggest_sa2s.append(sa2_code)
            biggest_sa2s.sort()
            biggest_sa2 = biggest_sa2s[0]

            biggest_pop = 0
            age_counts = []
            for val in structure[state_code][sa3_code][biggest_sa2].values():
                biggest_pop += val
                age_counts.append(val)

            sd = calculate_sample_sd(age_counts)
            op2[state_code][sa3_code] = [biggest_sa2, biggest_pop, sd]
    return op2


def cosine_similarity(list1, list2):
    # Returns the cosine similarity between two lists of numbers
    """
    Computes the cosine similarity between two numerical vectors.
    Args:
        list1 (list[float]): First vector.
        list2 (list[float]): Second vector.
    Returns:
        float: Cosine similarity rounded to 4 decimal places. Returns 0.0 if either vector has zero magnitude.
    """
    
    dot = 0.0
    for i in range(len(list1)):
        dot += list1[i] * list2[i]

    norm1 = 0.0
    for i in range(len(list1)):
        norm1 += list1[i] * list1[i]
    norm1 = norm1 ** 0.5

    norm2 = 0.0
    for i in range(len(list2)):
        norm2 += list2[i] * list2[i]
    norm2 = norm2 ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0
    else:
        return round(dot / (norm1 * norm2), 4)


def output_OP3(pop_rows, area_lookup):
    # For every SA3 with at least 15 SA2s, finds the pair of SA2s with the most similar age structures.
    """
    For every SA3 with at least 15 SA2s, finds the pair of SA2s with the most similar age structures
    based on cosine similarity.
    Args:
        pop_rows (list[dict]): List of cleaned population records.
        area_lookup (dict): Lookup dictionary mapping SA2 names to area info.
    Returns:
        dict: Mapping SA3 names to list [sa2_name1, sa2_name2, similarity] representing
              the pair of SA2s with highest cosine similarity.
              Results sorted alphabetically by SA3 name.
    """

    sa3_to_sa2 = {}
    for record in pop_rows:
        sa2 = record["sa2 name"].lower()
        if sa2 not in area_lookup:
            continue
        sa3 = area_lookup[sa2]["sa3 name"]
        age = record["age"]
        pop = record["population"]
        if sa3 not in sa3_to_sa2:
            sa3_to_sa2[sa3] = {}
        if sa2 not in sa3_to_sa2[sa3]:
            sa3_to_sa2[sa3][sa2] = {}
        sa3_to_sa2[sa3][sa2][age] = pop

    results = {}
    for sa3 in sa3_to_sa2:
        if len(sa3_to_sa2[sa3]) < 15:
            continue
        sa2_list = list(sa3_to_sa2[sa3].keys())
        sa2_list.sort()
        pairs = []
        for i in range(len(sa2_list)):
            for j in range(i+1, len(sa2_list)):
                sa2a = sa2_list[i]
                sa2b = sa2_list[j]
                all_ages_set = {}
                for age in sa3_to_sa2[sa3][sa2a]:
                    all_ages_set[age] = True
                for age in sa3_to_sa2[sa3][sa2b]:
                    all_ages_set[age] = True
                all_ages = list(all_ages_set.keys())
                all_ages.sort()
                pop_a = [sa3_to_sa2[sa3][sa2a].get(age, 0) for age in all_ages]
                pop_b = [sa3_to_sa2[sa3][sa2b].get(age, 0) for age in all_ages]

                sum_a = sum(pop_a)
                sum_b = sum(pop_b)
                if sum_a == 0 or sum_b == 0:
                    continue

                norm_a = [x / sum_a for x in pop_a]
                norm_b = [y / sum_b for y in pop_b]
                similarity_score = cosine_similarity(norm_a, norm_b)
                pairs.append((sa2a, sa2b, similarity_score))
        if not pairs:
            continue

        max_similarity = None
        for p in pairs:
            if max_similarity is None or p[2] > max_similarity:
                max_similarity = p[2]

        top_pairs = [p for p in pairs if p[2] == max_similarity]

        def pair_sort_key(pair):
            pop_a = sum(sa3_to_sa2[sa3][pair[0]].values())
            pop_b = sum(sa3_to_sa2[sa3][pair[1]].values())
            first, second = (pair[0], pair[1]) if pair[0] < pair[1] else (pair[1], pair[0])
            return (-(pop_a + pop_b), first, second)

        best_idx = 0
        best_key = pair_sort_key(top_pairs[0])
        for idx in range(1, len(top_pairs)):
            key = pair_sort_key(top_pairs[idx])
            if key < best_key:
                best_idx = idx
                best_key = key
        top_pair = top_pairs[best_idx]

        if top_pair[0] < top_pair[1]:
            results[sa3] = [top_pair[0], top_pair[1], top_pair[2]]
        else:
            results[sa3] = [top_pair[1], top_pair[0], top_pair[2]]

    # Return results for all qualifying SA3s sorted alphabetically
    output = {}
    sa3_names = list(results.keys())
    sa3_names.sort()

    for name in sa3_names:
        output[name] = results[name]

    return output


def main(csvfile_1, csvfile_2):
    #Main function to run the analysis. Returns (OP1, OP2, OP3)
    area_rows = read_area_file(csvfile_1)
    pop_rows = read_population_file(csvfile_2)
    cleaned_areas, cleaned_pops = clean_data(area_rows, pop_rows)
    area_lookup = create_area_lookup(cleaned_areas)

    op1 = output_OP1(cleaned_pops, area_lookup)
    op2 = output_OP2(cleaned_pops, area_lookup)
    op3 = output_OP3(cleaned_pops, area_lookup)
    return op1, op2, op3

"""
Debugging Documentation:

Issue 1 (Date 2025 May 05):
-> Error Description:
 When computing sample standard deviation on SA2s with only one age group, 
 the program crashed with ZeroDivisionError.
-> Erroneous Code Snippet: variance = sum((x - mean) ** 2 for x in ages) / (n - 1)
-> Test Case:OP2 computation on a SA2 with a population of one age group is the test case.
-> Reflection:I discovered that in order to calculate the sample standard deviation without dividing by zero, 
at least two data points are needed. In order to ensure that the program processes little amounts of data 
gracefully and without crashing, a check to return 0.0 if count < 2 was included.
This event enhanced my defensive programming abilities and reaffirmed the significance of confirming 
input sizes prior to mathematical computations. It also demonstrated how, even in circumstances where the main
logic seems to be fine, corner cases can result in runtime mistakes.

Issue 2 (Date 2025 May 12):
-> Error Description:Some SA2 pairs were unexpectedly omitted since the cosine similarity algorithm returned an 
inaccurate zero for vectors with entirely zero values.
-> Erroneous Code Snippet:
norm1 = sum(x * x for x in list1) ** 0.5
norm2 = sum(y * y for y in list2) ** 0.5
if norm1 == 0 or norm2 == 0:
    return 0.0
-> Test Case: OP3 processing SA3 regions with zero populations of SA2s across all age groups is the test case.
-> Reflection:Acknowledged that undefined cosine similarity is produced by vectors with 0 magnitude. To avoid 
unintentionally excluding acceptable comparisons, the algorithm was updated to detect and handle these 
circumstances by returning 0.0 similarity while processing other pairs. This made it easier for me to see how 
similarity metrics are interpreted geometrically and why vector math requires handling degenerate cases.
It also underlined how crucial it is to guarantee statistical computations' robustness while working with noisy 
data from the actual world.

Issue 3 (Date 2025 May 19):
-> Error Description:The output did not match the sample findings that were provided because floating-point 
integers were rounded too early during intermediate computation
-> Erroneous Code Snippet:
  sd = round(variance ** 0.5, 4)  # Inside loops before final output
-> Test Case: Comparison of the output with the project's sample dataset.
-> Reflection:  found that small numerical differences result from calculations that round too soon. enhanced 
accuracy and precisely matched expected outputs by changing the software to do all computations with complete 
precision, rounding only the final results when generating the output.I learned from this the importance of 
numerical accuracy in analytics as well as the dangers of rounding too early.Additionally, it reaffirmed data 
science workflow best practices for preserving data integrity up until final reporting.

"""
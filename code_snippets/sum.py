def sum_numbers_from_file(file_path):
    total_sum = 0
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Convert each line to int and add to the total sum
                total_sum += int(line.strip())
            except ValueError:
                # If the line can't be converted to a number, skip it
                print(f"Skipping non-numeric line: {line.strip()}")
    print(f"The sum of all numbers is: {total_sum}")

# Usage example
file_path = 'num.dat'  # Replace with your actual file path
sum_numbers_from_file(file_path)


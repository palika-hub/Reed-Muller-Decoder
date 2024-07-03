import numpy as np
import itertools
from collections import Counter
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import math

def most_common_value(matrix):
    # Extract the first column of the matrix
    first_column = [row[0] for row in matrix]
    
    # Count occurrences of each value in the first column
    counts = Counter(first_column)
    
    # Find the most common value and its count
    most_common = counts.most_common(1)
    
    # Return the most common value
    return most_common[0][0]

def extract_variable_and_coefficient(term):
    variables = [var for var in term[:-1] if var.startswith('x')]
    coefficient = term[-1]
    return variables, coefficient

# Generate combinations of binary strings
def generate_variable_combinations(num_variables):
    variables = ['0', '1']  # Variables can take values of 0 or 1
    variable_combinations = list(itertools.product(variables, repeat=num_variables))
    return [''.join(combination) for combination in variable_combinations]

# Generate the exact number of terms required by k
def generate_multilinear_terms(v, k):
    terms = [(0,)]  # Degree 0 term (constant 1)
    degree = 1
    while len(terms) < k:
        combinations = itertools.combinations(range(1, v + 1), degree)
        terms.extend(list(combinations))
        degree += 1
    return terms[:(k)]  # Return the exact number of terms required

def mod2_first_column(matrix):
    for row in matrix:
        row[0] = str(int(row[0]) % 2)
    return matrix

def remove_duplicate_rows(matrix):
    unique_matrix = np.copy(matrix)  # Create a copy to avoid modifying the original matrix
    rows_to_delete = []  # Store the indices of rows to be deleted

    while True:
        found_duplicates = False  # Flag to track if any duplicates were found in this iteration

        # Iterate through rows to find duplicates
        for i in range(len(unique_matrix)):
            if i in rows_to_delete:  # Skip rows that are already marked for deletion
                continue

            for j in range(i + 1, len(unique_matrix)):
                if np.array_equal(unique_matrix[i, 1:], unique_matrix[j, 1:]):
                    # Add the elements of the first column
                    unique_matrix[i, 0] = str(int(unique_matrix[i, 0]) + int(unique_matrix[j, 0]) )
                    # Mark the duplicate row for deletion
                    rows_to_delete.append(j)
                    found_duplicates = True

        if not found_duplicates:
            break  # If no duplicates were found in this iteration, exit the loop

        # Remove duplicate rows marked for deletion
        unique_matrix = np.delete(unique_matrix, rows_to_delete, axis=0)
        rows_to_delete = []  # Clear the list of rows to delete for the next iteration
        unique_matrix = mod2_first_column(unique_matrix)

    return unique_matrix

def calculate_multilinear_function(n, k, b_c):
    v = int(math.log2(n))
    t = 0
    current_sum = 0
    evaluations = []  # List to store evaluations

    # Iterate through different values of t until the sum equals k
    while current_sum < k:
        current_sum = np.sum([math.comb(v, i) for i in range(t + 1)])
        t += 1
    t = t-1
    print("v:")
    print(v)
    print("t:")
    print(t)
    print("\n")
    terms = generate_multilinear_terms(v, k)
    variables = ['x' + str(i) for i in range(1, v + 1)]
    # variables = list(reversed(variable))
    # Define coefficients
    coefficients = ['C' + str(i) for i in range(1, k + 1)]
 
    # Replace integer terms with corresponding variable names
    for i, term in enumerate(terms):
        terms[i] = tuple([variables[idx - 1] if idx != 0 else '1' for idx in term]) + (coefficients[i],)
    print(terms)
    binary_combinations = generate_variable_combinations(v)
    assigned_terms = assign_values_to_terms(terms, binary_combinations, b_c, list(reversed(variables)))

    # Convert assigned terms into a matrix without changing the values
    help_matrix = []
    for term in assigned_terms:
        row = term[:-1]  # Exclude the coefficient
        row.append(term[-1])  # Add the coefficient
        help_matrix.append(row)

    # Convert the list of lists into a NumPy array
    help_matrix = np.array(help_matrix)

    coefficients_matrices = {}
    for term in terms:
        variables, coefficient = extract_variable_and_coefficient(term)
        if coefficient != 'C1':
            if coefficient not in coefficients_matrices:
                coefficients_matrices[coefficient] = []

            coefficients_matrices[coefficient].append(variables)

    C1 = most_common_value(help_matrix)
    evaluations.append(f"C1: {C1}")  # Append evaluation of C1
    list_ = [C1]
    for coefficient, variable_lists in coefficients_matrices.items():
        if coefficient != 'C1':
            columns_to_remove = [int(var[1:]) for sublist in variable_lists for var in sublist]
            submatrix = np.delete(help_matrix, columns_to_remove, axis=1)
        else:
            submatrix = help_matrix
        
        unique_matrix = remove_duplicate_rows(submatrix)
        mode_value = most_common_value(unique_matrix)
        list_.append(mode_value)
        evaluations.append(f"{coefficient}: {mode_value}")  # Append evaluation of each coefficient
        
        # Append evaluation of unique matrix
        evaluations.append(f"\nUnique Matrix Evaluations for {coefficient}:")
        for row in unique_matrix:
            evaluations.append(' '.join(row))

    # Append help matrix evaluation
    evaluations.append("\nHelp Matrix:")
    for row in help_matrix:
        evaluations.append(' '.join(row))

    # Construct the multilinear function
    function = construct_multilinear_function(terms, list_)
    coefficients_string = ''.join(list_[1:])  # Concatenate coefficients C1, C2, ...

    return function, coefficients_string, C1, evaluations

def assign_values_to_terms(terms, binary_combinations, buggy_codeword, variables):
    assigned_terms = []
    for i, binary_string in enumerate(binary_combinations):
        assigned_term = []
        for j, char in enumerate(binary_string):
            if char == '0':
                assigned_term.append('0')
            else:
                assigned_term.append(variables[j])
        assigned_term.append(buggy_codeword[i])  # Append the buggy codeword value
        assigned_terms.append(list(reversed(assigned_term)))
    return assigned_terms

def construct_multilinear_function(terms, coefficients):
    function_terms = []
    for i, term in enumerate(terms):
        variables, coefficient = extract_variable_and_coefficient(term)
        if coefficient != 0:  # Only include terms with non-zero coefficients
            term_string = ""
            for variable in variables:
                term_string += variable
            if len(term_string) == 0:
                term_string = '1'  # Handle the constant term
        function_terms.append(f"{coefficients[i]} * {term_string}")
    function = " + ".join(function_terms)
    return function

def validate_input(n, k, b_c):
    if not math.log2(n).is_integer():
        messagebox.showerror("Error", "n must be a power of 2.")
        return False
    if len(b_c) > n:
        messagebox.showerror("Error", "Buggy codeword length cannot exceed n.")
        return False
    return True

def submit():
    n = int(entry_n.get())
    k = int(entry_k.get())
    b_c = entry_b_c.get()

    if validate_input(n, k, b_c):
        function, coefficients_string, C1, evaluations = calculate_multilinear_function(n, k, b_c)
        
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, function)

        coefficients_text.delete("1.0", tk.END)
        coefficients_text.insert(tk.END, f"Message: {C1}{coefficients_string}")

        # Display evaluations
        evaluations_text.delete("1.0", tk.END)
        for eval in evaluations:
            evaluations_text.insert(tk.END, eval + "\n")
            # print(eval)  # Print the evaluation to console

def reset():
    entry_n.delete(0, tk.END)
    entry_k.delete(0, tk.END)
    entry_b_c.delete(0, tk.END)
    output_text.delete("1.0", tk.END)
    coefficients_text.delete("1.0", tk.END)
    evaluations_text.delete("1.0", tk.END)
# GUI Setup
root = tk.Tk()
root.title("Decoding Reed-Muller Code")
root.attributes('-zoomed', True)  # Maximize window
root.configure(bg="black", highlightbackground="black", highlightthickness=5)

style = ttk.Style()
style.theme_use("clam")

frame_input = tk.Frame(root, bg="black")
frame_input.pack(pady=10)

label_n = tk.Label(frame_input, text="Enter the value of n:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_n.grid(row=0, column=0, padx=10, pady=10, sticky="e")

entry_n = tk.Entry(frame_input, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
entry_n.grid(row=0, column=1, padx=10, pady=10)

label_k = tk.Label(frame_input, text="Enter the value of k:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_k.grid(row=1, column=0, padx=10, pady=10, sticky="e")

entry_k = tk.Entry(frame_input, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
entry_k.grid(row=1, column=1, padx=10, pady=10)

label_b_c = tk.Label(frame_input, text="Enter the value of buggy codeword:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_b_c.grid(row=2, column=0, padx=10, pady=10, sticky="e")

entry_b_c = tk.Entry(frame_input, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
entry_b_c.grid(row=2, column=1, padx=10, pady=10)

button_submit = tk.Button(frame_input, text="Submit", command=submit, bg="#F1F4FF", fg="#85B3D1",font=("Helvetica", 16))
button_submit.grid(row=3, columnspan=2, pady=10)

button_reset = tk.Button(frame_input, text="Reset", command=reset, bg="#F1F4FF", fg="#85B3D1",font=("Helvetica", 16))
button_reset.grid(row=4, columnspan=2)

frame_output = tk.Frame(root, bg="black")
frame_output.pack(pady=10)

label_output = tk.Label(frame_output, text="Multilinear Function:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_output.pack()

output_text = tk.Text(frame_output, height=5, width=50, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
output_text.pack()

label_coefficients = tk.Label(root, text="Message:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_coefficients.pack()

coefficients_text = tk.Text(root, height=2, width=50, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
coefficients_text.pack()

label_evaluations = tk.Label(root, text="Evaluations:", bg="black", fg="#C7D3D4",font=("Helvetica", 16))
label_evaluations.pack()

evaluations_text = tk.Text(root, height=15, width=60, font=("Helvetica", 16), highlightbackground="black", highlightthickness=1)
evaluations_text.pack()

root.mainloop()
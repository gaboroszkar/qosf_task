# Import libraries.
import qiskit
import numpy

# Quantum Fourier Transform
# =========================
#
# Example: create_qft_circuit(4)
#
#                                                                           ┌───┐   
# q_0: ─────────────────────────────■─────────────────■─────────────■───────┤ H ├─X─
#                                   │                 │       ┌───┐ │P(π/2) └───┘ │ 
# q_1: ───────────────■─────────────┼────────■────────┼───────┤ H ├─■─────────X───┼─
#                     │       ┌───┐ │        │P(π/2)  │P(π/4) └───┘           │   │ 
# q_2: ──────■────────┼───────┤ H ├─┼────────■────────■───────────────────────X───┼─
#      ┌───┐ │P(π/2)  │P(π/4) └───┘ │P(π/8)                                       │ 
# q_3: ┤ H ├─■────────■─────────────■─────────────────────────────────────────────X─
#      └───┘                                                                        
def create_qft_circuit(n):
    qc = qiskit.QuantumCircuit(n)
    
    # Applying the phases.
    for i in range(n - 1, -1, -1):
        for j in range(i, -1, -1):
            if i == j:
                qc.h(i)
            else:
                qc.cp(numpy.pi / (2 ** (i - j)), i, j)
                
    # Swapping the output qubits.
    for i in range(n // 2):
        qc.swap(i, n - i - 1)

    return qc
def create_qft_gate(n):
    qc = create_qft_circuit(n)
    gate = qc.to_gate()
    gate.label = "QFT"
    return gate
def create_qft_inverse_gate(n):
    qc = create_qft_circuit(n)
    gate = qc.to_gate().inverse()
    gate.label = "QFT Inv"
    return gate

# QFT addition
# ============
# Modified implementation of https://arxiv.org/abs/quant-ph/0008033.
#
# Example create_qft_add_circuit(7, 5)
#
#      ┌────────┐┌────────┐
# f_0: ┤ P(π/2) ├┤ P(π/4) ├
#      └┬──────┬┘├────────┤
# f_1: ─┤ P(π) ├─┤ P(π/2) ├
#       ├──────┤ └────────┘
# f_2: ─┤ P(π) ├───────────
#       └──────┘           
# f_3: ────────────────────
#                          
def create_qft_add_circuit(a, digits):
    # The number "a" and the fourier transformed number "f" ("digits" bits) to be added.
    # "a" has be able to be represented on "digits" bits.
    
    # Convert "a" to binary in reverse, so a_binary[i] = a_i,
    # where a = sum_i 2^i * a_i.
    a_binary = format(a, "0" + str(digits) + "b")[::-1]
    
    # Setup qubits.
    qreg_f = qiskit.QuantumRegister(digits, "f")
    qc = qiskit.QuantumCircuit(qreg_f)

    # Applying the phases.
    for i in range(digits - 1, -1, -1):
        for j in range(i, -1, -1):
            if a_binary[j] == "1":
                # Note, (digits-i-1) corresponds to i in the referred article,
                # because our QFT swaps the output qubits.
                qc.p(numpy.pi / (2 ** (i - j)), qreg_f[digits - i - 1])

    return qc
def create_qft_add_gate(a, digits):
    qc = create_qft_add_circuit(a, digits)
    gate = qc.to_gate()
    gate.label = "QFT Add"
    return gate
def create_qft_add_controlled_gate(a, digits):
    gate = create_qft_add_gate(a, digits).control()
    return gate

# Addition
# ========
#
# Example create_add_circuit([1, 2, 3], 4)
#
#                                                                
#      x_0: ──────────■──────────────────────────────────────────
#                     │                                          
#      x_1: ──────────┼───────────■──────────────────────────────
#                     │           │                              
#      x_2: ──────────┼───────────┼───────────■──────────────────
#           ┌───┐┌────┴─────┐┌────┴─────┐┌────┴─────┐┌──────────┐
# target_0: ┤ H ├┤0         ├┤0         ├┤0         ├┤0         ├
#           ├───┤│          ││          ││          ││          │
# target_1: ┤ H ├┤1         ├┤1         ├┤1         ├┤1         ├
#           ├───┤│  QFT Add ││  QFT Add ││  QFT Add ││  QFT Inv │
# target_2: ┤ H ├┤2         ├┤2         ├┤2         ├┤2         ├
#           ├───┤│          ││          ││          ││          │
# target_3: ┤ H ├┤3         ├┤3         ├┤3         ├┤3         ├
#           └───┘└──────────┘└──────────┘└──────────┘└──────────┘
def create_add_circuit(numbers, digits):
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    qc = qiskit.QuantumCircuit(qreg_x, qreg_target)
    
    # First, we apply a QFT on |target>.
    #qc.append(create_qft_gate(digits), target)
    # We assume, that the |target initially is |0>, so we only need Hadamards.
    qc.h(qreg_target)
    
    for i in range(len(numbers)):
        qc.append(create_qft_add_controlled_gate(numbers[i], digits),
            [qreg_x[i]] + qreg_target[:])
    
    qc.append(create_qft_inverse_gate(digits), qreg_target)

    return qc
def create_add_gate(numbers, digits):
    qc = create_add_circuit(numbers, digits)
    gate = qc.to_gate()
    gate.label = "Add"
    return gate

# Checker
# =======
#
# Example create_checker_circuit(7, 5)
#
#                
# target_0: ─────
#                
# target_1: ─────
#                
# target_2: ─────
#           ┌───┐
# target_3: ┤ X ├
#           ├───┤
# target_4: ┤ X ├
#           └───┘
def create_checker_circuit(expected_sum, digits):
    qc = qiskit.QuantumCircuit(digits)
    formatted = format(expected_sum, "0" + str(digits) + "b")
    for i in range(digits):
        if formatted[i] == "0":
            qc.x(digits - i - 1)
    return qc
def create_checker_gate(expected_sum, digits):
    qc = create_checker_circuit(expected_sum, digits)
    gate = qc.to_gate()
    gate.label = "Checker"
    return gate

# Validator
# =========
#
# Example create_validator_circuit([2, 4], 6, 3)
#
#           ┌──────┐            
#      x_0: ┤0     ├────────────
#           │      │            
#      x_1: ┤1     ├────────────
#           │      │┌──────────┐
# target_0: ┤2 Add ├┤0         ├
#           │      ││          │
# target_1: ┤3     ├┤1 Checker ├
#           │      ││          │
# target_2: ┤4     ├┤2         ├
#           └──────┘└──────────┘
def create_validator_circuit(numbers, expected_sum, digits):
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    qc = qiskit.QuantumCircuit(qreg_x, qreg_target)
    
    # Add the numbers together.
    qc.append(create_add_gate(numbers, digits),
        qreg_x[:] + qreg_target[:])

    # Check whether the result is the expected sum.
    qc.append(create_checker_gate(expected_sum, digits),
        qreg_target)

    return qc
def create_validator_gate(numbers, expected_sum, digits):
    qc = create_validator_circuit(numbers, expected_sum, digits)
    gate = qc.to_gate()
    gate.label = "Validator"
    return gate
def create_validator_inverse_gate(numbers, expected_sum, digits):
    qc = create_validator_circuit(numbers, expected_sum, digits)
    gate = qc.to_gate().inverse()
    gate.label = "Validator Inv"
    return gate

# Grover Oracle
# =============
# |x> |y> |target>  ->  |x> |f(x)+y> |target>, where f(x)+y is modulo 2 addition,
# and f(x) = 1 if and only if the combination of the numbers in the list (indexed by x)
# adds up the expected_sum.
#
# Example create_grover_oracle_circuit([2, 4], 6, 3)
#
#           ┌────────────┐     ┌────────────────┐
#      x_0: ┤0           ├─────┤0               ├
#           │            │     │                │
#      x_1: ┤1           ├─────┤1               ├
#           │            │┌───┐│                │
#        y: ┤            ├┤ X ├┤                ├
#           │  Validator │└─┬─┘│  Validator Inv │
# target_0: ┤2           ├──■──┤2               ├
#           │            │  │  │                │
# target_1: ┤3           ├──■──┤3               ├
#           │            │  │  │                │
# target_2: ┤4           ├──■──┤4               ├
#           └────────────┘     └────────────────┘
def create_grover_oracle_circuit(numbers, expected_sum, digits):
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_y = qiskit.QuantumRegister(1, "y")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    qc = qiskit.QuantumCircuit(qreg_x, qreg_y, qreg_target)
    
    qc.append(create_validator_gate(numbers, expected_sum, digits),
        qreg_x[:] + qreg_target[:])
    
    # Create a multi controlled not gate on the target, which is |y>, and the controls are the outputs of the checker.
    qc.mcx(qreg_target[:], qreg_y)
    
    qc.append(create_validator_inverse_gate(numbers, expected_sum, digits),
        qreg_x[:] + qreg_target[:])
    
    return qc
def create_grover_oracle_gate(numbers, expected_sum, digits):
    qc = create_grover_oracle_circuit(numbers, expected_sum, digits)
    gate = qc.to_gate()
    gate.label = "Grover Oracle"
    return gate

# Diffuser
# ========
#
# Example create_diffuser_circuit(3)
#
#      ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐
# x_0: ┤ H ├┤ X ├┤ H ├┤ X ├┤ H ├┤ X ├┤ H ├┤ Z ├┤ X ├┤ Z ├┤ X ├
#      ├───┤├───┤└───┘└─┬─┘├───┤├───┤└───┘└───┘└───┘└───┘└───┘
# x_1: ┤ H ├┤ X ├───────■──┤ X ├┤ H ├─────────────────────────
#      ├───┤├───┤       │  ├───┤├───┤                         
# x_2: ┤ H ├┤ X ├───────■──┤ X ├┤ H ├─────────────────────────
#      └───┘└───┘          └───┘└───┘                         
def create_diffuser_circuit(n):
    qc = qiskit.QuantumCircuit(n)
    
    qc.h(range(n))
    qc.x(range(n))
    
    # HXH = Z, so this is a multi controlled Z gate.
    qc.h(0)
    qc.mcx(list(range(1, n)), 0)
    qc.h(0)
    
    qc.x(range(n))
    qc.h(range(n))
    
    # ZXZX = -1
    qc.z(0)
    qc.x(0)
    qc.z(0)
    qc.x(0)
    
    return qc
def create_diffuser_gate(n):
    qc = create_diffuser_circuit(n)
    gate = qc.to_gate()
    gate.label = "Diffuser"
    return gate

# Grover iterator
# ===============
#
# Example create_grover_circuit([2, 4], 6, 3)
#
#           ┌────────────────┐┌───────────┐
#      x_0: ┤0               ├┤0          ├
#           │                ││  Diffuser │
#      x_1: ┤1               ├┤1          ├
#           │                │└───────────┘
#        y: ┤2               ├─────────────
#           │  Grover Oracle │             
# target_0: ┤3               ├─────────────
#           │                │             
# target_1: ┤4               ├─────────────
#           │                │             
# target_2: ┤5               ├─────────────
#           └────────────────┘             
def create_grover_circuit(numbers, expected_sum, digits):
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_y = qiskit.QuantumRegister(1, "y")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    qc = qiskit.QuantumCircuit(qreg_x, qreg_y, qreg_target)

    # Apply Grover Oracle
    qc.append(create_grover_oracle_gate(numbers, expected_sum, digits),
        qreg_x[:] + qreg_y[:] + qreg_target[:])

    qc.append(create_diffuser_gate(len(numbers)), qreg_x)

    return qc
def create_grover_gate(numbers, expected_sum, digits):
    qc = create_grover_circuit(numbers, expected_sum, digits)
    gate = qc.to_gate()
    gate.label = "Grover"
    return gate

def create_controlled_grover_gate(numbers, expected_sum, digits):
    gate = create_grover_gate(numbers, expected_sum, digits).control()
    gate.label = "Grover"
    return gate

# Counter
# =======
#
# Example
#
#           ┌───┐                                                                                  ┌──────────┐
#      t_0: ┤ H ├──────────■───────────────────────────────────────────────────────────────────────┤0         ├
#           ├───┤          │                                                                       │          │
#      t_1: ┤ H ├──────────┼──────────■──────────■─────────────────────────────────────────────────┤1 QFT Inv ├
#           ├───┤          │          │          │                                                 │          │
#      t_2: ┤ H ├──────────┼──────────┼──────────┼──────────■──────────■──────────■──────────■─────┤2         ├
#           ├───┤     ┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐└──────────┘
#      x_0: ┤ H ├─────┤0        ├┤0        ├┤0        ├┤0        ├┤0        ├┤0        ├┤0        ├────────────
#           ├───┤     │         ││         ││         ││         ││         ││         ││         │            
#      x_1: ┤ H ├─────┤1        ├┤1        ├┤1        ├┤1        ├┤1        ├┤1        ├┤1        ├────────────
#           ├───┤┌───┐│         ││         ││         ││         ││         ││         ││         │            
#        y: ┤ X ├┤ H ├┤2        ├┤2        ├┤2        ├┤2        ├┤2        ├┤2        ├┤2        ├────────────
#           └───┘└───┘│  Grover ││  Grover ││  Grover ││  Grover ││  Grover ││  Grover ││  Grover │            
# target_0: ──────────┤3        ├┤3        ├┤3        ├┤3        ├┤3        ├┤3        ├┤3        ├────────────
#                     │         ││         ││         ││         ││         ││         ││         │            
# target_1: ──────────┤4        ├┤4        ├┤4        ├┤4        ├┤4        ├┤4        ├┤4        ├────────────
#                     │         ││         ││         ││         ││         ││         ││         │            
# target_2: ──────────┤5        ├┤5        ├┤5        ├┤5        ├┤5        ├┤5        ├┤5        ├────────────
#                     └─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘            
def create_counter_circuit(numbers, expected_sum, digits, digits_counter):
    qreg_t = qiskit.QuantumRegister(digits_counter, "t")
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_y = qiskit.QuantumRegister(1, "y")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    qc = qiskit.QuantumCircuit(qreg_t, qreg_x, qreg_y, qreg_target)

    # Set the |x> and |t> to the superposition of all possible combinations.
    qc.h(qreg_x)
    qc.h(qreg_t)

    # Set the |y> to |->.
    qc.x(qreg_y)
    qc.h(qreg_y)

    # Apply Grover iterator n times
    
    n = 1
    for i in range(digits_counter):
        for j in range(n):
            qc.append(create_controlled_grover_gate(numbers, expected_sum, digits),
                [qreg_t[i]] + qreg_x[:] + qreg_y[:] + qreg_target[:])
        n *= 2

    qc.append(create_qft_inverse_gate(digits_counter), qreg_t)
    
    return qc
def create_counter_gate(numbers, expected_sum, digits, digits_counter):
    qc = create_counter_circuit(numbers, expected_sum, digits, digits_counter)
    gate = qc.to_gate()
    gate.label = "Counter"
    return gate

# Returns with the approximate number of solutions,
# and with the optimal number of iterations for the Grover algorithm.
def calculate_counter_result(result, len_numbers, digits_counter):
    theta = numpy.pi * result / 2 ** digits_counter
    number_of_solutions = 2 ** len_numbers * numpy.sin(theta) ** 2
    
    # There are two solutions we can measure: theta or pi-theta,
    # and 0 <= theta <= pi/2.
    # If we measured >pi/2, we make a correction.
    if theta > numpy.pi / 2:
        theta = numpy.pi - theta
    optimal_number_of_iterations = numpy.pi / (4 * theta) - 0.5
    
    return (number_of_solutions, optimal_number_of_iterations)

def count_optimal_iterations(numbers, expected_sum, digits, digits_counter, shots_counter):
    qreg_t = qiskit.QuantumRegister(digits_counter, "t")
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_y = qiskit.QuantumRegister(1, "y")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    creg_t = qiskit.ClassicalRegister(digits_counter, "creg_t")
    qc = qiskit.QuantumCircuit(qreg_t, qreg_x, qreg_y, qreg_target, creg_t)

    # Applying the counter.
    qc.append(create_counter_gate(numbers, expected_sum, digits, digits_counter),
        qreg_t[:] + qreg_x[:] + qreg_y[:] + qreg_target[:])

    # We only want to measure the values of |x>, the combinations.
    qc.measure(qreg_t, creg_t)

    # Execute the circuit, print outcomes.
    job = qiskit.execute(qc, qiskit.Aer.get_backend("qasm_simulator"), shots = shots_counter)
    counts = job.result().get_counts(qc)
    
    # If there's no solutions, we return with False.
    # No solutions, if the no solutions has more than 0.5 probability.
    if ("0" * digits_counter) in counts and counts["0" * digits_counter] > shots_counter / 2:
        return False

    # Format the result.
    counts_int = {}
    for key in counts:
        new_key = int(key[0:digits_counter], 2)
        if new_key != 0:
            counts_int[new_key] = counts[key]
    result = max(counts_int)
    return calculate_counter_result(result, len(numbers), digits_counter)

def find_indices(numbers, expected_sum, digits, digits_counter, shots, shots_counter):
    # First, we decide how many times Grover iterator needs to be applied.
    counter_results = count_optimal_iterations(numbers, expected_sum, digits, digits_counter, shots_counter)
    if not counter_results:
        return False

    (number_of_solutions, optimal_number_of_iterations) = counter_results

    #print("approximate number of solutions: " + str(number_of_solutions))
    #print("optimal number of iterations: " + str(optimal_number_of_iterations))

    # Setup qubits.
    qreg_x = qiskit.QuantumRegister(len(numbers), "x")
    qreg_y = qiskit.QuantumRegister(1, "y")
    qreg_target = qiskit.QuantumRegister(digits, "target")
    creg_x = qiskit.ClassicalRegister(len(numbers), "creg_x")
    qc = qiskit.QuantumCircuit(qreg_x, qreg_y, qreg_target, creg_x)

    # Set the |x> to the superposition of all possible combinations.
    qc.h(qreg_x)

    # Set the |y> to |->.
    qc.x(qreg_y)
    qc.h(qreg_y)

    # Apply Grover iterator n times
    for i in range(round(optimal_number_of_iterations)):
        qc.append(create_grover_gate(numbers, expected_sum, digits),
            qreg_x[:] + qreg_y[:] + qreg_target[:])

    # We only want to measure the values of |x>, the combinations.
    qc.measure(qreg_x, creg_x)

    # Execute the circuit, print outcomes.
    job = qiskit.execute(qc, qiskit.Aer.get_backend("qasm_simulator"), shots = shots)
    counts = job.result().get_counts(qc)

    # Format result. Flip the binary of |x>.
    counts_formatted = {}
    for key in counts:
        key_formatted = key[::-1]
        counts_formatted[key_formatted] = counts[key]
    return counts_formatted

if __name__ == "__main__":
    # Setup parameters for the calculation.
    numbers = [5, 7, 8, 9, 1]
    expected_sum = 16
    digits = 5
    # Let's set the counter qubits to ceil(numbers/2).
    # We need to apply the Grover iterator 2^digits_counter-1 times,
    # and to get the complexity similar to the Grover search,
    # we set it to roughly sqrt(2^len(numbers)).
    # For small lists, this parameter is crucial, we add +1.
    digits_counter = int(numpy.ceil(len(numbers) / 2)) + 1
    #digits_counter = 5
    # Number of measurements.
    shots = 100
    shots_counter = 100

    results = find_indices(numbers, expected_sum, digits, digits_counter, shots, shots_counter)
    print(results)
# qosf_task
Screening task solution for the Quantum Open Source Foundation mentorship program.

`qosf_task_1.{py,ipynb,html}` both contain the same source in different formats.
This is the solution for Task 1. Given a list of numbers, and one expected sum,
the program will output the indices of the numbers which add up to the expected sum.
The output is the number of measurements for the combination of indices in a binary format.
For example if the program measures `01001` with high probability, that means, that
the second and the last numbers add up to the expected sum.

The program uses the well known Grover, and the Quantum Counting algorithms.

The `.ipynb` and `.html` files contain a little bit of documentation compared to the source code `.py`.

`qosf_task_1_unoptimized.ipynb` is an unoptimized version of the algorithm.
It is included, in case this is what's needed.
This unoptimized version uses much more qubits,
because practically it stores all the input numbers
in qubits, adding `numbers * digits` more qubits.
I said practically, because the input numbers are still hardcoded in the gates,
there is still some optimization in this algorithm.
I didn't make an algorithm where the numbers are stored in the initial state of the qubits.

from qiskit import QuantumCircuit
from qiskit_aer import Aer
import random

def generate_key(num_bits=512):
    backend = Aer.get_backend("aer_simulator")
    key = []

    for _ in range(num_bits):
        alice_bit = random.randint(0, 1)
        alice_basis = random.choice(['X', 'Z'])
        bob_basis = random.choice(['X', 'Z'])

        qc = QuantumCircuit(1, 1)
        if alice_bit == 1:
            qc.x(0)
        if alice_basis == 'X':
            qc.h(0)
        qc.barrier()
        if bob_basis == 'X':
            qc.h(0)
        qc.measure(0, 0)

        job = backend.run(qc, shots=1, memory=True)
        result = job.result()
        measured_bit = int(result.get_memory()[0])

        if alice_basis == bob_basis:
            key.append(measured_bit)

    return key

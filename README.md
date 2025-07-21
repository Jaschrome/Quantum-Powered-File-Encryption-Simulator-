# Quantum Key Distribution Simulator

This Streamlit app simulates Quantum Key Distribution (QKD) using the BB84 protocol and lets you encrypt/decrypt files with a quantum-generated key.

## Features

- Simulates QKD key generation using Qiskit
- Encrypts files with a one-time pad using the quantum key
- Packages encrypted file and key for download
- Decrypts files using the provided key
- update 1 - added an on devie BB84 simulation that runs on the CPU instead of qiskit. Also supports multithreading

## How it works

1. Generate a quantum key using a simulated quantum circuit (BB84 protocol)
2. Encrypt your uploaded file with the key (one-time pad)
3. Download both the encrypted file and the key as a ZIP
4. Decrypt by uploading both files

## Quickstart

```bash
git clone https://github.com/Jaschrome/qkd-sim.git
cd qkd-sim
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
streamlit run app.py
```

## Requirements

- Python 3.8+
- streamlit
- qiskit
- qiskit-aer

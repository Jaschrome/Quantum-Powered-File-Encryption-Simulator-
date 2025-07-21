import streamlit as st
from qkd_qiskit import generate_key
from encryptor import encrypt_bytes
from decryptor import decrypt_bytes
import io
import zipfile
import random
import threading
import time

def bb84_cpu_simulation(num_bits, update_callback):
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(['X', 'Z']) for _ in range(num_bits)]
    bob_bases = [random.choice(['X', 'Z']) for _ in range(num_bits)]
    bob_results = [None] * num_bits
    sifted_key = []

    def measure_bit(i):
        # Simulate quantum measurement delay
        time.sleep(0.01)
        if alice_bases[i] == bob_bases[i]:
            bob_results[i] = alice_bits[i]
        else:
            bob_results[i] = random.randint(0, 1)
        # Update progress in UI
        update_callback(i, alice_bits, alice_bases, bob_bases, bob_results)

    threads = []
    for i in range(num_bits):
        t = threading.Thread(target=measure_bit, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Sift key
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_key.append(bob_results[i])
    return alice_bits, alice_bases, bob_bases, bob_results, sifted_key

st.title("Quantum-Powered File Encryption Simulator")

with st.expander("ℹ️ How does this work?"):
    st.markdown("""
    **Quantum Key Distribution (QKD) Simulation (built by Juno):**
    1. A quantum key is generated using a simulated quantum circuit (BB84 protocol) or a CPU-based BB84 simulation.
    2. This key is used as a one-time pad to encrypt your uploaded file.
    3. Both the encrypted file and the key are packaged together for download.
    4. For decryption, you upload both the encrypted file and the key.
    **Process Flow:**
    ```
    [Alice: Quantum Key Generation] ---(Key)---> [Encryption] ---(Encrypted File + Key)---> [Bob: Decryption]
    ```
    """)

mode = st.radio("Choose operation:", ["Encrypt", "Decrypt"])

st.markdown("### ⚙️ Settings")
num_bits = st.slider("Quantum Key Length (bits)", 128, 2048, 512, step=128)
encryption_method = st.radio("Encryption Method", ["Base64", "BB84 (Quantum Key)", "BB84 (CPU Simulated)"])

# Ensure the key is generated and stored in the session state
if "key" not in st.session_state or st.session_state.get("last_num_bits") != num_bits or st.session_state.get("last_method") != encryption_method:
    if encryption_method == "BB84 (CPU Simulated)":
        # Run CPU BB84 simulation and use the sifted key
        def dummy_update(*args, **kwargs): pass  # No UI update needed here
        _, _, _, _, sifted_key = bb84_cpu_simulation(num_bits, dummy_update)
        st.session_state["key"] = sifted_key
    else:
        st.session_state["key"] = generate_key(num_bits)
    st.session_state["last_num_bits"] = num_bits
    st.session_state["last_method"] = encryption_method

if mode == "Encrypt":
    uploaded_file = st.file_uploader("Upload a file to encrypt", type=["txt", "bin"])
    if uploaded_file:
        with st.expander("🔎 See how encryption works step-by-step"):
            st.markdown("**Step 1: Quantum Key Generation**")
            st.code(f"Key (first 32 bits): {st.session_state['key'][:32]} ...", language="python")
            st.markdown("**Step 2: File is read as bytes**")
            file_bytes = uploaded_file.read()
            st.code(f"File bytes (first 32): {list(file_bytes[:32])} ...", language="python")
            st.markdown(f"**Step 3: {'Base64 encoding' if encryption_method == 'Base64' else 'One-time pad (BB84 key) XOR'}**")
            st.markdown("The file is encrypted using the selected method and the generated key.")

        if st.button("Encrypt"):
            key = st.session_state["key"]
            use_base64 = (encryption_method == "Base64")
            with st.spinner("Encrypting..."):
                encrypted = encrypt_bytes(file_bytes, key, use_base64)
            st.success("Encryption Complete!")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr("encrypted_output.txt", encrypted)
                zip_file.writestr("key.bin", bytes(key))
            zip_buffer.seek(0)
            st.download_button(
                "Download Encrypted File & Key (ZIP)",
                zip_buffer,
                file_name="encrypted_and_key.zip",
                mime="application/zip"
            )

elif mode == "Decrypt":
    st.info("Select the same decryption method that was used for encryption.")
    encrypted_file = st.file_uploader("Upload encrypted file", type=["txt", "bin"])
    key_file = st.file_uploader("Upload key file", type=["bin"])
    decryption_method = st.radio("Decryption Method", ["Base64", "BB84 (Quantum Key)", "BB84 (CPU Simulated)"])
    use_base64 = (decryption_method == "Base64")
    if encrypted_file and key_file:
        with st.expander("🔎 See how decryption works step-by-step"):
            st.markdown("**Step 1: Key file is read as bytes**")
            key_bytes = key_file.read()
            st.code(f"Key (first 32 bits): {list(key_bytes[:32])} ...", language="python")
            st.markdown("**Step 2: Encrypted file is read as bytes**")
            encrypted_bytes = encrypted_file.read()
            st.code(f"Encrypted bytes (first 32): {list(encrypted_bytes[:32])} ...", language="python")
            st.markdown(f"**Step 3: {'Base64 decoding' if use_base64 else 'One-time pad (BB84 key) XOR'}**")
            st.markdown("The file is decrypted using the selected method and the provided key.")

        if st.button("Decrypt"):
            try:
                key = list(key_bytes)
                decrypted = decrypt_bytes(encrypted_bytes, key, use_base64)
                st.success("Decryption successful!")
                st.download_button("Download Decrypted File", decrypted, "decrypted_output.txt")
            except Exception as e:
                st.error(f"Decryption failed: {e}")

# --- BB84 CPU Simulation Visualizer ---
if st.button("Simulate BB84 on CPU (Multithreaded)"):
    st.markdown("### BB84 Simulation (CPU, Multithreaded)")
    sim_bits = st.slider("Number of bits to simulate", 16, 128, 32, step=8)
    progress_bar = st.progress(0)
    status_text = st.empty()
    table_placeholder = st.empty()
    details_placeholder = st.empty()

    def update_ui(i, alice_bits, alice_bases, bob_bases, bob_results):
        progress_bar.progress((i + 1) / sim_bits)
        table_placeholder.table({
            "Bit #": list(range(sim_bits)),
            "Alice Bit": alice_bits,
            "Alice Basis": alice_bases,
            "Bob Basis": bob_bases,
            "Bob Result": bob_results
        })
        # Show calculation details for the current bit
        details_placeholder.markdown(
            f"""
            **Bit {i+1} Calculation:**
            - Alice's bit: `{alice_bits[i]}`
            - Alice's basis: `{alice_bases[i]}`
            - Bob's basis: `{bob_bases[i]}`
            - {'Bases match' if alice_bases[i] == bob_bases[i] else 'Bases do NOT match'}
            - Bob's result: `{bob_results[i]}`
            """
        )
        status_text.write(f"Measured bit {i+1}/{sim_bits}")

    alice_bits, alice_bases, bob_bases, bob_results, sifted_key = bb84_cpu_simulation(
        sim_bits, update_ui
    )
    st.success(f"Simulation complete! Sifted key length: {len(sifted_key)}")
    st.code(f"Sifted key: {sifted_key}", language="python")

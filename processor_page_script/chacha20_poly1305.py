from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
import time
import base64
import platform
import subprocess
import re
from datetime import datetime

def encrypt_file_chacha20_poly1305(file_path):
    try:
        execution_time = time.perf_counter()
        key = os.urandom(32)  # 256-bit key for ChaCha20-Poly1305
        nonce = os.urandom(12)  # 12-byte nonce
        chacha = ChaCha20Poly1305(key)

        with open(file_path, 'rb') as file:
            file_data = file.read()

        start_time = time.perf_counter()
        encrypted_data = chacha.encrypt(nonce, file_data, None)
        encryption_time = time.perf_counter() - start_time

        # Save encrypted data for decryption test
        encrypted_file_path = file_path + ".enc"
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)

        execution_time_enc = time.perf_counter() - execution_time

        return {
            "encryption_time": encryption_time,
            "execution_time_enc": execution_time_enc,
            "key": base64.b64encode(key).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "encrypted_file_path": encrypted_file_path
        }
    except Exception as e:
        return {"error": f"Encryption failed: {str(e)}"}

def decrypt_file_chacha20_poly1305(filepath, key_b64, nonce_b64):
    try:
        execution_time = time.perf_counter()
        key = base64.b64decode(key_b64)
        nonce = base64.b64decode(nonce_b64)
        chacha = ChaCha20Poly1305(key)

        with open(filepath, 'rb') as file:
            encrypted_data = file.read()

        start_time = time.perf_counter()
        decrypted_data = chacha.decrypt(nonce, encrypted_data, None)
        decryption_time = time.perf_counter() - start_time
        execution_time_dec = time.perf_counter() - execution_time

        # Clean up the encrypted file
        os.remove(filepath)

        return {
            "decryption_time": decryption_time,
            "execution_time_dec": execution_time_dec
        }
    except Exception as e:
        return {"error": f"Decryption failed: {str(e)}"}

def get_system_info():
    try:
        # Extract raw CPU model name from lscpu
        cpu_model = subprocess.check_output(
            "lscpu | grep 'Model name' | awk -F ':' '{print $2}'", 
            shell=True, text=True
        ).strip()

        # Clean up the model name for consistency
        cpu_model = re.sub(r'\s*$$R$$|\s*$$TM$$|\s*Core|Processor', '', cpu_model)  # Remove (R), (TM), "Core", "Processor"
        cpu_model = re.sub(r'\s+', ' ', cpu_model).strip()  # Normalize spaces
    except Exception as e:
        cpu_model = platform.processor()
    
    os_name = platform.system()
    return cpu_model, os_name

def create_test_file(size_mb):
    """Create a test file of specified size in MB"""
    size_bytes = size_mb * 1024 * 1024  # Convert MB to bytes
    test_file_path = f"test_data/{size_mb}MB.txt"
    
    # Create test_data directory if it doesn't exist
    os.makedirs("test_data", exist_ok=True)
    
    # Create file with random data
    with open(test_file_path, 'wb') as f:
        f.write(os.urandom(size_bytes))
    
    return test_file_path

def save_benchmark_result(result, benchmark_folder):
    """Save benchmark result to a text file"""
    # Create the benchmark results directory if it doesn't exist
    os.makedirs(benchmark_folder, exist_ok=True)
    
    # Create a filename based on the algorithm and file size
    filename = f"chacha20_poly1305_{result['file_size']}.txt"
    filepath = os.path.join(benchmark_folder, filename)
    
    # Format the result as a single line with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_line = f"{timestamp},{result['cpu_model']},{result['os_name']},{result['file_size']},{result['encryption_time']},{result['decryption_time']},{result['execution_time']}\n"
    
    # Append the result to the file
    with open(filepath, 'a') as f:
        f.write(result_line)
    
    return filepath

def run_chacha20_poly1305_benchmark(file_size, benchmark_folder="benchmark_results"):
    try:
        # Convert file size string to number
        size_mb = int(file_size.replace("MB", ""))
        
        # Create test file
        file_path = create_test_file(size_mb)
        
        # Get system info
        cpu_model, os_name = get_system_info()
        
        # Run encryption benchmark
        encryption_result = encrypt_file_chacha20_poly1305(file_path)
        
        if "error" in encryption_result:
            return {"error": encryption_result["error"]}
        
        # Run decryption benchmark
        decryption_result = decrypt_file_chacha20_poly1305(
            encryption_result["encrypted_file_path"],
            encryption_result["key"],
            encryption_result["nonce"]
        )
        
        if "error" in decryption_result:
            return {"error": decryption_result["error"]}
        
        # Calculate total execution time
        execution_time = encryption_result["execution_time_enc"] + decryption_result["execution_time_dec"]
        
        # Clean up test file
        try:
            os.remove(file_path)
        except:
            pass
        
        # Format the results
        result = {
            "cpu_model": cpu_model,
            "os_name": os_name,
            "file_size": file_size,
            "encryption_time": round(encryption_result["encryption_time"], 3),
            "decryption_time": round(decryption_result["decryption_time"], 3),
            "execution_time": round(execution_time, 3)
        }
        
        # Save the result to a text file
        save_benchmark_result(result, benchmark_folder)
        
        return result
    except Exception as e:
        return {"error": str(e)}


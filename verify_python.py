import json
import os
import sys
from toon_parser import encode, decode

def deep_equal(obj1, obj2, path=""):
    if type(obj1) != type(obj2):
        print(f"Type mismatch at {path}: {type(obj1)} vs {type(obj2)}")
        return False
    
    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            print(f"Dict length mismatch at {path}: {len(obj1)} keys vs {len(obj2)} keys")
            keys1 = set(obj1.keys())
            keys2 = set(obj2.keys())
            if keys1 != keys2:
                print(f"Missing keys in 1: {keys2 - keys1}")
                print(f"Missing keys in 2: {keys1 - keys2}")
            return False
        for key in obj1:
            if key not in obj2:
                print(f"Key {key} missing at {path}")
                return False
            if not deep_equal(obj1[key], obj2[key], f"{path}.{key}"):
                return False
        return True
    
    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            print(f"List length mismatch at {path}: {len(obj1)} vs {len(obj2)}")
            return False
        for i in range(len(obj1)):
            if not deep_equal(obj1[i], obj2[i], f"{path}[{i}]"):
                return False
        return True
    
    if obj1 != obj2:
        print(f"Value mismatch at {path}: {repr(obj1)} vs {repr(obj2)}")
        return False
    
    return True

def run_verification():
    base_dir = "/home/johnpaez/TOON"
    json_path = os.path.join(base_dir, "test.json")
    toon_path = os.path.join(base_dir, "test.toon")
    
    print("--- Loading Ground Truth ---")
    with open(json_path, 'r') as f:
        original_json = json.load(f)
    print(f"Loaded {json_path}")

    # 1. Decode test.toon and compare with test.json
    print("\n--- Phase 1: Decoding test.toon ---")
    if os.path.exists(toon_path):
        with open(toon_path, 'r') as f:
            toon_content = f.read()
        
        decoded_from_toon = decode(toon_content)
        if deep_equal(original_json, decoded_from_toon):
            print("✅ SUCCESS: Decoded test.toon matches test.json")
        else:
            print("❌ FAILURE: Decoded test.toon does NOT match test.json")
            # Save for inspection
            with open("python_decoded_from_toon.json", "w") as f:
                json.dump(decoded_from_toon, f, indent=2)
    else:
        print("Skipping Phase 1: test.toon not found.")

    # 2. Roundtrip test.json (Encode -> Decode)
    print("\n--- Phase 2: Roundtrip test.json (Encode -> Decode) ---")
    encoded_toon = encode(original_json)
    with open("python_encoded.toon", "w") as f:
        f.write(encoded_toon)
    
    roundtrip_json = decode(encoded_toon)
    
    if deep_equal(original_json, roundtrip_json):
        print("✅ SUCCESS: Roundtrip (Encode -> Decode) successful")
        original_file_size = os.path.getsize(json_path)
        encoded_size = len(encoded_toon)
        compact_json_size = len(json.dumps(original_json))
        
        reduction_vs_file = (original_file_size - encoded_size) / original_file_size * 100
        reduction_vs_compact = (compact_json_size - encoded_size) / compact_json_size * 100
        
        print(f"Original JSON Size (Indented): {original_file_size} bytes")
        print(f"TOON Size: {encoded_size} bytes")
        print(f"Reduction vs Indented JSON: {reduction_vs_file:.2f}%")
        print(f"Reduction vs Compact JSON: {reduction_vs_compact:.2f}%")
    else:
        print("❌ FAILURE: Roundtrip mismatch")
        with open("python_roundtrip_fail.json", "w") as f:
            json.dump(roundtrip_json, f, indent=2)

if __name__ == "__main__":
    run_verification()

"""
Release Package Verification Script.
Calculates SHA256 hashes for frontend dist assets and generates checksum manifest.
"""

import hashlib
import os

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def main():
    dist_dir = "E:/Saarthi/frontend/dist"
    print("=== SAARTHI CLOSED BETA RELEASE MANIFEST AUDIT ===")
    
    if not os.path.exists(dist_dir):
        print(f"Error: Frontend build directory '{dist_dir}' does not exist.")
        return

    manifest_entries = []
    for root, _, files in os.walk(dist_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dist_dir)
            file_hash = calculate_sha256(full_path)
            file_size = os.path.getsize(full_path)
            manifest_entries.append((rel_path, file_hash, file_size))
            print(f"- {rel_path:35s} | SHA256: {file_hash[:16]}... | Size: {file_size:7d} bytes")

    # Generate release directory
    release_dir = "E:/Saarthi/release/beta_package_v1.0.0-beta.1"
    os.makedirs(release_dir, exist_ok=True)
    
    checksum_file = os.path.join(release_dir, "SHA256SUMS.txt")
    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write("# Saarthi Closed Beta v1.0.0-beta.1 SHA256 Checksums\n")
        for rel_path, file_hash, file_size in manifest_entries:
            f.write(f"{file_hash}  {rel_path}\n")

    print(f"\nChecksum manifest written to: {checksum_file}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import os
import subprocess
import glob
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT_DIR / "output"

user_defined_mapping = {
    
}

def load_user_mapping_file():
    path = Path("user_mapping.txt")
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            content = f.read().strip()
            return eval(content) if content else {}
    except Exception as e:
        print(f"❌ Failed to read user_mapping.txt: {e}")
        return {}

def extract_cert_info(apk_path):
    try:
        output = subprocess.check_output([
            "apksigner", "verify", "--print-certs", apk_path
        ], universal_newlines=True)
        sha256 = None
        cn = None
        o = None
        for line in output.splitlines():
            if "SHA-256 digest:" in line:
                sha256 = line.split(":")[-1].strip()
            elif "certificate DN:" in line:
                dn = line.split("certificate DN:")[-1]
                parts = [x.strip() for x in dn.split(",")]
                for part in parts:
                    if part.startswith("CN="):
                        cn = part.replace("CN=", "")
                    elif part.startswith("O="):
                        o = part.replace("O=", "")
        return sha256, cn, o
    except Exception as e:
        print(f"❌ Failed to extract cert info from {apk_path}: {e}")
        return None, None, None

def extract_offset(apk_path):
    try:
        meta_dir = OUT_DIR / "meta"
        meta_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["apksigcopier", "extract", apk_path, str(meta_dir)], check=True)
        with open(meta_dir / "APKSigningBlockOffset") as f:
            return int(f.read().strip(), 10)
    except Exception as e:
        print(f"❌ Failed to get offset for {apk_path}: {e}")
        return None

def ensure_apk_sign_c():
    apk_sign = OUT_DIR / "kernel/apk_sign.c"
    if not apk_sign.exists():
        print("📄 Creating kernel/apk_sign.c")
        apk_sign.parent.mkdir(parents=True, exist_ok=True)
        with open(apk_sign, "w") as f:
            f.write("""#include <stdbool.h>

bool check_v2_signature(char *path, unsigned int offset, const char *sha256);

bool is_manager_apk(char *path)
{
    // Default check
    return check_v2_signature(path, EXPECTED_NEXT_SIZE, EXPECTED_NEXT_HASH);
}
""")
        subprocess.run(["git", "add", str(OUT_DIR / "kernel/apk_sign.c")])
        subprocess.run(["git", "commit", "-m", "Initial: add apk_sign.c"])

def update_apk_sign(results):
    apk_sign = OUT_DIR / "kernel/apk_sign.c"
    with open(apk_sign) as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    for line in lines:
        if "return check_v2_signature" in line:
            new_lines.append("    return (\n")
            new_lines.append("        check_v2_signature(path, EXPECTED_NEXT_SIZE, EXPECTED_NEXT_HASH)")
            for offset, sha256, comment in results:
                new_lines.append(f"        || check_v2_signature(path, 0x{offset:x}, \"{sha256}\") // {comment}")
            new_lines.append("    );\n")
            inserted = True
        else:
            new_lines.append(line)

    if inserted:
        with open(apk_sign, "w") as f:
            f.writelines(new_lines)
        subprocess.run(["git", "add", str(OUT_DIR / "kernel/apk_sign.c")])
        subprocess.run(["git", "commit", "-m", "apk_sign: Add more kernel manager support"])

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    assets_dir = ROOT_DIR / "assets"
    if not assets_dir.exists() or not any(assets_dir.glob("*.apk")):
        print("❌ No APK files found in assets directory")
        return
    
    ensure_apk_sign_c()
    file_mapping = load_user_mapping_file()

    # Detect which mapping source is available
    mapping_source = (
        "script (hardcoded)" if user_defined_mapping else
        "user_mapping.txt" if file_mapping else
        "automatic (certificate-based)"
    )
    print(f"🔍 Using mapping source: {mapping_source}")

    results = []
    for apk_file in Path("assets").glob("*.apk"):
        name = apk_file.name
        sha256, cn, o = extract_cert_info(str(apk_file))
        offset = extract_offset(str(apk_file))

        if sha256 and offset:
            if name in user_defined_mapping:
                label = user_defined_mapping[name]
                print(f"✅ {name} → {label} (from script)")
            elif name in file_mapping:
                label = file_mapping[name]
                print(f"✅ {name} → {label} (from user_mapping.txt)")
            elif cn and o:
                label = f"{cn}/{o}"
                print(f"✅ {name} → {label} (from CN/O)")
            elif cn:
                label = cn
                print(f"✅ {name} → {label} (from CN only)")
            elif o:
                label = o
                print(f"✅ {name} → {label} (from O only)")
            else:
                label = "unknown"
                print(f"⚠️ {name}: fallback to 'unknown'")
            results.append((offset, sha256, label))
        else:
            print(f"❌ Could not process {name}")

    if not results:
        print("❌ No valid APKs found. Nothing to patch.")
        return

    update_apk_sign(results)

    subprocess.run(["git", "format-patch", "-1", "-o", str(OUT_DIR)], check=True)

    patch_files = list(OUT_DIR.glob("*.patch"))
    if patch_files:
        patch_filename = OUT_DIR / "ksu_more_manager.patch"
        patch_files[0].rename(patch_filename)
        print(f"🎉 Patch saved as {patch_filename}!")
    else:
        print("❌ No patch file was created.")

if __name__ == "__main__":
    main()
    

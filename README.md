# 🔐 Kernel Manager Patcher

> A command-line tool that extracts **V2 signing info** from APK files and dynamically patches `kernel/apk_sign.c` with valid signature checks for various **KernelSU manager apps**.

> It simplifies patch creation for custom KernelSU builds by recognizing APKs either automatically (via their certificate info) or through user-defined mappings.

---

## ✨ Features

- ✅ <small>**Auto-detects APKs**</small> via the `assets/` folder in the project root.
- 🔗 <small>**Auto-fetches mappings**</small> from APK certificate fields `CN` and `O`.
- 🧠 <small>**User-defined mappings**</small> via `user_mapping.txt` or a Python dictionary inside the script.
- 🔍 <small>**V2 signature & offset extraction**</small> using `apksigcopier`.
- 🔑 <small>**Certificate verification**</small> with `apksigner`.
- 📝 <small>**Git patch generation**</small> with dynamic signature injection.
- 📦 <small>**Flexible APK filename support**</small> (supports spaces, symbols, etc.).
- 🪄 <small>**Fully offline operation**</small> (once dependencies are installed).
- 🤖 <small>**Supports GitHub Actions workflow**</small> Actions >> Kernel Manager Patcher >> Run.

---

## 🧩 Dependencies

Make sure the following tools are installed:

| Tool         | Purpose                              |
|--------------|--------------------------------------|
| `apksigner`  | Extract certificate details          |
| `apksigcopier` | Extract V2 signing block offset     |
| `git`        | Manage patch creation                |
| `python3`    | Run the patching script              |

---

## 🧰 Install Required Packages

### 📱 Android (Termux)
```bash
pkg update && pkg upgrade
pkg install -y git python openjdk apksigner
pip install --upgrade pip
pip install apksigcopier
```

### 🐧 Debian/Ubuntu
```bash
sudo apt update
sudo apt install -y --install-recommends git python3 python3-pip google-android-cmdline-tools-11.0-installer openjdk-21-jre-headless

pip3 install --upgrade pip
pip3 install apksigcopier

echo "export ANDROID_SDK_ROOT=\$HOME/Android/Sdk" >> ~/.bashrc
echo "export PATH=\$ANDROID_SDK_ROOT/build-tools/36.0.0:\$PATH" >> ~/.bashrc
source ~/.bashrc

mkdir -p "$ANDROID_SDK_ROOT"
sdkmanager --sdk_root=$ANDROID_SDK_ROOT --install "build-tools;36.0.0"
yes | sdkmanager --licenses || true
apksigner --version
```
***Note:***  
If using any other Linux distribution, please install equivalent packages for:  
- `git` `python3` and `pip` `OpenJDK` (Java runtime)
- Android SDK command-line tools and build-tools (for `apksigner`)

Package names and installation commands will vary by distro.

---

## ⚙️ Git Configuration
#### 👤 Set User Identity
Configure Git user information for commits:

```bash
git config --global user.name "user"
git config --global user.email "youremail@example.com"
```

#### 🔐 Safe Directory Setup
If Git throws safe directory issues, use this wildcard pattern *(requires **Git v2.36+**)*:

```bash
git config --global --add safe.directory '*'
```
*⚠️ Warning: This will make all directories on your system trusted by Git. Use with caution, especially if you work with untrusted repositories.*

---

## 🗂️ Project Directory Tree
```
Kernel_Manager_Patcher/
├── patch.py                           # Main patching script
├── user_mapping.txt                   # (Optional) User-defined APK label mappings
├── output/kernel/
│         └── apk_sign.c               # Auto-generated/modified source file
├── output/meta/
│         └── APKSigningBlock          # Auto-generated/modified bi-product file
│         └── APKSigningBlockOffset    # Auto-generated/modified bi-product file 
└── assets/*.apk                       # Place your manager APK files here (input folder)

```

---

## 📥 Getting Started (Local & GitHub Actions)
### 🤖 Automate with GitHub Actions
Automate patch generation easily:

1. **Fork** this repo to your GitHub account.
2. In your fork, create an `assets` folder at the root and **upload your APK files** there.
   - If your APK files exceed GitHub's file size limits `(100 MB per file)`, you can upload them using `Git LFS (Large File Storage)`:
   - Install Git LFS locally on your machine using git lfs install.
   - Use git lfs track "*.apk" to track .apk files.Commit and push the APKs to your repo just like regular files, and Git LFS will handle large files for you.
3. Go to the **Actions** tab in your forked repo.
4. Select the **Kernel Manager Patcher** workflow.
5. Click **Run workflow** > **Run** to start.

After the workflow completes successfully, download the generated patch (`ksu_more_manager.patch`) from the workflow artifacts.

> ***Tip:** This lets you generate patches without any local setup, fully in the cloud!*

### 🖥️ Local Setup & Usage
Clone the repository:
```bash
git clone https://github.com/UdayKumarChunduru/Kernel_Manager_Patcher.git
```

Navigate into the directory:
```bash
cd Kernel_Manager_Patcher
```

Give execution permission to patch.py file
```bash 
chmod +x patch.py
```

#### 🚀 Usage
1. ✅ Place your `.apk` manager files inside the `assets/` directory at the project root.
2. 🔄 (Optional) Add mappings directly in the `user_defined_mapping()` function inside the Python script, like:
```python
user_defined_mapping = {
  "ksun.apk": "rifsxd/KernelSU-Next",
  "sukisu.apk": "ShirkNeko/SukiSU-Ultra"
}
```
3. 🔄 (Optional) Create or edit user_mapping.txt to define custom mappings:

```json
{
  "ksun.apk": "rifsxd/KernelSU-Next",
  "sukisu.apk": "ShirkNeko/SukiSU-Ultra"
}
```
> **Note:** If both `user_mapping.txt` and the Python dictionary inside the script (`user_defined_mapping()`) are present, mappings in `user_mapping.txt` take precedence.

#### ▶ Run the script:

```python
python3 patch.py
```

#### 📦 Output:
Updated kernel/apk_sign.c with new signature verification entries

A patch file `ksu_more_manager.patch` will be generated

---

## 📫 Support
Feel free to reach out with questions, issues, or suggestions:

[![Telegram](https://img.shields.io/badge/Telegram-000?style=for-the-badge&logo=telegram&logoColor=26A5E4)](https://t.me/fortecipher)

---

## 📄 License
<small>Licensed under GNU General Public License v2.0 (GPL-2.0), in accordance with the Linux kernel.</small>

---

## ⭐️ Star the Project!
<small>If this tool simplifies your workflow or saves you time, consider starring ⭐️ the repository. Your support is appreciated!</small>

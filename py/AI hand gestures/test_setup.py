
import sys
import importlib
import importlib.metadata
import os

# ==========================================
# CONFIGURATION
# ==========================================

REQUIRED_PACKAGES = {
    "cv2": "opencv-python",
    "mediapipe": "mediapipe"
}

MODEL_PATH = "models/gesture_recognizer.task"

# ==========================================
# SETUP CHECK
# ==========================================

print("=" * 45)
print("       GESTURE CONTROLLER SETUP CHECK")
print("=" * 45)

print(f"\nPython version: {sys.version.split()[0]}")
print(f"Python location: {sys.executable}")

missing_packages = []
failed_packages = []

# ==========================================
# CHECK PACKAGES
# ==========================================

print("\nChecking dependencies...\n")

for module_name, package_name in REQUIRED_PACKAGES.items():

    try:
        module = importlib.import_module(module_name)

        try:
            version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            version = "Unknown"

        print(f"[OK] {package_name} ({version})")

        # Check MediaPipe Tasks API
        if module_name == "mediapipe":

            if hasattr(module, "tasks"):
                print("[OK] MediaPipe Tasks API available")
            else:
                print("[ERROR] MediaPipe Tasks API unavailable")
                failed_packages.append(package_name)

    except ImportError as error:

        print(f"[MISSING] {package_name}")
        print(f"         {error}")

        missing_packages.append(package_name)

    except Exception as error:

        print(f"[ERROR] {package_name}")
        print(f"        {error}")

        failed_packages.append(package_name)


# ==========================================
# CHECK MODEL
# ==========================================

print("\nChecking model...\n")

if os.path.isfile(MODEL_PATH):
    print(f"[OK] Model found: {MODEL_PATH}")
else:
    print(f"[WARNING] Model not found: {MODEL_PATH}")
    print("          Check your models folder.")


# ==========================================
# RESULTS
# ==========================================

print("\n" + "=" * 45)
print("                RESULTS")
print("=" * 45)

if not missing_packages and not failed_packages:

    print("\n[SUCCESS] All dependencies are working!")

else:

    print("\n[ERROR] Some dependencies need attention.")

    if missing_packages:

        print("\nMissing packages:")

        for package in missing_packages:
            print(f"- {package}")

        print("\nInstall them using:")

        import subprocess

        command = subprocess.list2cmdline([
            sys.executable,
            "-m",
            "pip",
            "install",
            *missing_packages
        ])

        print(command)

    if failed_packages:

        print("\nPackages with errors:")

        for package in failed_packages:
            print(f"- {package}")

        print("\nTry reinstalling the affected packages:")
        print(f'"{sys.executable}" -m pip install --upgrade --force-reinstall '
              + " ".join(failed_packages))

print("\nSetup check completed.")
print("=" * 45)

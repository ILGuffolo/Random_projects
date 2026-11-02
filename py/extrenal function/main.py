
import subprocess
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
PROGRAMS = ROOT / "programs"
BUILD = ROOT / "build"

BUILD.mkdir(exist_ok=True)


# --------------------------------
# PHASE 1: COMPILE ALL C PROGRAMS
# --------------------------------

def compile_all():

    print("\n=== COMPILING C PROGRAMS ===")

    compiled = {}

    for source in PROGRAMS.glob("*.c"):

        name = source.stem
        executable = BUILD / name

        print(f"Compiling {name}.c...")

        result = subprocess.run(
            ["gcc", str(source), "-o", str(executable)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"ERROR compiling {name}:")
            print(result.stderr)
            continue

        compiled[name] = executable
        print(f"[OK] {name} compiled!")

    print(f"\nCompiled {len(compiled)} programs.\n")

    return compiled


# --------------------------------
# PHASE 2: RUN A COMPILED PROGRAM
# --------------------------------

def run_program(programs, name, *args):

    if name not in programs:
        print(f"Program '{name}' is not available.")
        return None

    result = subprocess.run(
        [str(programs[name]), *map(str, args)],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        print("Program error:")
        print(result.stderr)
        return None

    return result.stdout.strip()


# --------------------------------
# PHASE 3: MAIN APPLICATION
# --------------------------------

def main():

    # Compile everything first
    programs = compile_all()

    # Run hello.c
    print("=== HELLO PROGRAM ===")

    hello_output = run_program(programs, "hello")

    if hello_output is not None:
        print(hello_output)

    # Interactive calculator loop
    print("\n=== CALCULATOR ===")
    print("Enter two numbers to calculate their sum.")
    print("Type 'q' to quit.\n")

    while True:

        first = input("First number: ")

        if first.lower() == "q":
            break

        second = input("Second number: ")

        if second.lower() == "q":
            break

        try:
            a = int(first)
            b = int(second)
        except ValueError:
            print("Please enter valid integers.\n")
            continue

        # Execute the already-compiled C program
        output = run_program(programs, "calculator", a, b)

        if output is not None:
            print(f"Result: {output}\n")

    print("Exiting Python C Runner.")


if __name__ == "__main__":
    main()

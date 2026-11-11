
import cv2
import os
import re
import zipfile
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

DATASET_FOLDER = "dataset"
ZIP_NAME = "dataset.zip"

os.makedirs(DATASET_FOLDER, exist_ok=True)


# ==========================================
# GESTURE SELECTION
# ==========================================

def select_gesture():

    while True:

        name = input(
            "\nGesture name (or Q to finish): "
        ).strip()

        if name.lower() == "q":
            return None

        name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)

        if not name:
            print("Invalid name.")
            continue

        folder = os.path.join(DATASET_FOLDER, name)

        os.makedirs(folder, exist_ok=True)

        existing = len([
            f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        print(f"\nSelected: {name}")
        print(f"Existing samples: {existing}")

        return name


# ==========================================
# DATASET EXPORT
# ==========================================

def export_dataset():

    print("\nCreating dataset ZIP...")

    with zipfile.ZipFile(
        ZIP_NAME,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:

        for root, dirs, files in os.walk(DATASET_FOLDER):

            for filename in files:

                if filename.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                ):

                    filepath = os.path.join(root, filename)

                    archive_name = os.path.relpath(
                        filepath,
                        DATASET_FOLDER
                    )

                    archive.write(filepath, archive_name)

    print(f"Dataset exported: {ZIP_NAME}")


# ==========================================
# CAMERA INITIALIZATION
# ==========================================

camera = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

if not camera.isOpened():

    print("ERROR: Could not open webcam.")
    raise SystemExit


# ==========================================
# MAIN LOOP
# ==========================================

try:

    while True:

        gesture_name = select_gesture()

        if gesture_name is None:
            break

        gesture_folder = os.path.join(
            DATASET_FOLDER,
            gesture_name
        )

        sample_count = len([
            f for f in os.listdir(gesture_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        print("\nCONTROLS:")
        print("SPACE = Capture image")
        print("N     = Select another gesture")
        print("Q     = Finish and export dataset")

        while True:

            success, frame = camera.read()

            if not success:
                print("ERROR: Camera unavailable.")
                break

            frame = cv2.flip(frame, 1)

            # Save clean frame, not the interface overlay
            display = frame.copy()

            cv2.putText(
                display,
                f"Gesture: {gesture_name}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                display,
                f"Samples: {sample_count}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                display,
                "SPACE: Capture | N: Next | Q: Finish",
                (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

            cv2.imshow("Gesture Dataset Collector", display)

            key = cv2.waitKey(1) & 0xFF

            # Capture image
            if key == ord(' '):

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                filename = f"{timestamp}.jpg"

                filepath = os.path.join(
                    gesture_folder,
                    filename
                )

                cv2.imwrite(filepath, frame)

                sample_count += 1

                print(
                    f"[{gesture_name}] "
                    f"Captured: {sample_count}"
                )

            # Next gesture
            elif key == ord('n'):
                break

            # Finish
            elif key == ord('q'):
                raise SystemExit

finally:

    camera.release()
    cv2.destroyAllWindows()

    export_dataset()

    print("\nDataset collection finished!")

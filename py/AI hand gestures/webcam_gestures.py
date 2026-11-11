
import cv2
import mediapipe as mp
import time
import os
from datetime import datetime

# Import custom actions
from actions.open_palm import run as open_palm_action
from actions.fist import run as fist_action
from actions.thumbs_up import run as thumbs_up_action
from actions.victory import run as victory_action
from actions.quit import run as quit_action
from actions.thumbs_down import run as thumbs_down_action
from actions.pointing_up import run as pointing_up_action


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_PATH = "models/gesture_recognizer.task"

CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

NUM_HANDS = 2

STABILITY_TIME = 0.3
MIN_CONFIDENCE = 0.60

SCREENSHOT_FOLDER = "screenshots"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


# ==========================================
# CUSTOM ACTIONS
# ==========================================

ACTIONS = {
    "Open_Palm": open_palm_action,
    "Closed_Fist": fist_action,
    "Thumb_Up": thumbs_up_action,
    "Victory": victory_action,
    "ILoveYou": quit_action,
    "Thumb_Down": thumbs_down_action,
    "Pointing_Up": pointing_up_action
}


# ==========================================
# GESTURE STATE
# ==========================================

hand_state = None
stability_start = None


def run_gesture(gesture):

    action = ACTIONS.get(gesture)

    if action:
        print(f"Executing: {gesture}")

        # True means the application should quit
        return action() is True

    return False


def update_gesture(detected_gesture):

    global hand_state
    global stability_start

    # Gesture matches current state
    if detected_gesture == hand_state:
        stability_start = None
        return False

    # Start timer when a change is detected
    if stability_start is None:
        stability_start = time.perf_counter()
        return False

    # Check stability
    elapsed = time.perf_counter() - stability_start

    if elapsed >= STABILITY_TIME:

        hand_state = detected_gesture

        print(f"Hand state changed: {hand_state}")

        should_quit = run_gesture(hand_state)

        stability_start = None

        return should_quit

    return False


# ==========================================
# MEDIAPIPE INITIALIZATION
# ==========================================

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=NUM_HANDS
)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


# ==========================================
# WEBCAM INITIALIZATION
# ==========================================

camera = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
    raise SystemExit

print("Webcam connected!")
print("Starting gesture controller...")
print(f"Stability time: {STABILITY_TIME}s")
print(f"Minimum confidence: {MIN_CONFIDENCE:.0%}")
print("Press Q to quit | S to save screenshot")


# ==========================================
# MAIN LOOP
# ==========================================

try:

    with GestureRecognizer.create_from_options(options) as recognizer:

        frame_count = 0
        fps = 0

        fps_timer = time.perf_counter()
        last_timestamp = 0

        while True:

            # 1. Receive webcam frame
            success, frame = camera.read()

            if not success:
                print("ERROR: Could not receive webcam frame.")
                break

            # 2. Mirror image
            frame = cv2.flip(frame, 1)

            # 3. Convert BGR to RGB
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # 4. Create MediaPipe image
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # 5. Generate increasing timestamp
            timestamp_ms = time.monotonic_ns() // 1_000_000

            timestamp_ms = max(
                timestamp_ms,
                last_timestamp + 1
            )

            last_timestamp = timestamp_ms

            # 6. Recognize gestures
            result = recognizer.recognize_for_video(
                mp_image,
                timestamp_ms
            )

            # Default: no reliable gesture
            detected_gesture = None

            # 7. Process detected hands
            if result.hand_landmarks:

                for hand_index, landmarks in enumerate(
                    result.hand_landmarks
                ):

                    height, width, _ = frame.shape

                    points = []

                    for landmark in landmarks:
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        points.append((x, y))

                    # Draw hand connections
                    for start, end in HAND_CONNECTIONS:
                        cv2.line(
                            frame,
                            points[start],
                            points[end],
                            (0, 255, 0),
                            2
                        )

                    # Draw landmarks
                    for x, y in points:
                        cv2.circle(
                            frame,
                            (x, y),
                            4,
                            (0, 0, 255),
                            -1
                        )

                    # Get gesture classification
                    if (
                        result.gestures
                        and result.gestures[hand_index]
                    ):

                        category = result.gestures[hand_index][0]

                        gesture = category.category_name
                        confidence = category.score

                        # Accept sufficiently confident predictions
                        if (
                            confidence >= MIN_CONFIDENCE
                            and detected_gesture is None
                        ):
                            detected_gesture = gesture

                        # Display raw recognition
                        cv2.putText(
                            frame,
                            f"{gesture} ({confidence:.0%})",
                            (
                                points[0][0] - 20,
                                points[0][1] - 20
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 0),
                            2
                        )

            # 8. Update gesture state
            should_quit = update_gesture(detected_gesture)

            # 9. Display current state
            status = f"Hand state: {hand_state or 'None'}"

            cv2.putText(
                frame,
                status,
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            # 10. Calculate FPS
            frame_count += 1

            elapsed = time.perf_counter() - fps_timer

            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                fps_timer = time.perf_counter()

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # 11. Display webcam
            cv2.imshow("AI Gesture Controller", frame)

            # 12. Keyboard controls
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or should_quit:
                break

            elif key == ord('s'):

                filename = datetime.now().strftime(
                    "screenshot_%Y%m%d_%H%M%S.jpg"
                )

                filepath = os.path.join(
                    SCREENSHOT_FOLDER,
                    filename
                )

                cv2.imwrite(filepath, frame)

                print(f"Screenshot saved: {filepath}")

finally:

    camera.release()
    cv2.destroyAllWindows()

    print("Webcam disconnected.")


import mediapipe as mp
import cv2

# ----------------------------------
# 1. Configuration
# ----------------------------------

MODEL_PATH = "models/gesture_recognizer.task"
IMAGE_PATH = "images/test.jpg"

# ----------------------------------
# 2. Initialize MediaPipe
# ----------------------------------

print("Loading MediaPipe...")

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.IMAGE,
    num_hands=2
)

# ----------------------------------
# 3. Load image
# ----------------------------------

print("Loading image...")

image = mp.Image.create_from_file(IMAGE_PATH)

# ----------------------------------
# 4. Recognize gestures
# ----------------------------------

print("Analyzing hand gestures...")

with GestureRecognizer.create_from_options(options) as recognizer:

    result = recognizer.recognize(image)

    if not result.gestures:
        print("\nNo hands detected.")

    else:
        for i, hand_gestures in enumerate(result.gestures):

            gesture = hand_gestures[0]

            print(f"\nHand {i + 1}")
            print("Gesture:", gesture.category_name)
            print("Confidence:", f"{gesture.score:.2%}")

            # Number of detected landmarks
            landmarks = result.hand_landmarks[i]
            print("Landmarks detected:", len(landmarks))

# ----------------------------------
# 5. Display image
# ----------------------------------

# Convert MediaPipe image to OpenCV format
image_bgr = cv2.cvtColor(
    image.numpy_view(),
    cv2.COLOR_RGB2BGR
)

cv2.namedWindow("MediaPipe Gesture Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("MediaPipe Gesture Test", 1200, 850)
cv2.imshow("MediaPipe Gesture Test", image_bgr)

print("\nPress any key to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()

print("Test completed!")

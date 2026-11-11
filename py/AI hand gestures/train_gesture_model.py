
import os
from mediapipe_model_maker import gesture_recognizer

# ==========================================
# CONFIGURATION
# ==========================================

DATASET_FOLDER = "dataset"
EXPORT_FOLDER = "exported_model"

EPOCHS = 15
BATCH_SIZE = 8

# ==========================================
# LOAD DATASET
# ==========================================

print("Loading gesture dataset...")

data = gesture_recognizer.Dataset.from_folder(
    dirname=DATASET_FOLDER
)

print(f"Dataset loaded: {data.size} samples")
print(f"Gestures: {data.label_names}")

# ==========================================
# SPLIT DATASET
# ==========================================

train_data, remaining_data = data.split(0.8)

validation_data, test_data = remaining_data.split(0.5)

print(f"Training samples: {train_data.size}")
print(f"Validation samples: {validation_data.size}")
print(f"Testing samples: {test_data.size}")

# ==========================================
# TRAIN MODEL
# ==========================================

print("\nTraining model...")

hparams = gesture_recognizer.HParams(
    export_dir=EXPORT_FOLDER,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    shuffle=True
)

options = gesture_recognizer.GestureRecognizerOptions(
    hparams=hparams
)

model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)

# ==========================================
# EVALUATE MODEL
# ==========================================

print("\nEvaluating model...")

loss, accuracy = model.evaluate(test_data)

print(f"Test loss: {loss:.4f}")
print(f"Test accuracy: {accuracy:.2%}")

# ==========================================
# EXPORT MODEL
# ==========================================

print("\nExporting model...")

model.export_model(
    model_name="gesture_recognizer.task"
)

print("\nTraining finished!")
print(f"Model saved in: {EXPORT_FOLDER}")

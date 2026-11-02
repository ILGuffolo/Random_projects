import copy
import time

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.utils.prune as prune

import matplotlib.pyplot as plt

from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import make_moons, make_circles
from sklearn.model_selection import train_test_split


# ==========================================
# CONFIGURATION
# ==========================================

# Choose: "easy", "medium", "hard"
DATASET = "hard"

SAMPLES = 1200
NOISE = 0.15

HIDDEN_SIZE = 128
HIDDEN_LAYERS = 3

INITIAL_EPOCHS = 200
RETRAIN_EPOCHS = 40

BATCH_SIZE = 64
LEARNING_RATE = 0.001

PRUNE_AMOUNT = 0.20
PRUNE_ITERATIONS = 10

# Stop if validation accuracy drops more than 2 percentage points
MAX_ACCURACY_DROP = 0.02

SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)

# Keep CPU usage predictable on low-end PCs
torch.set_num_threads(1)

device = torch.device("cpu")


# ==========================================
# DATASET GENERATION
# ==========================================

def generate_spirals(samples, noise):

    n = samples // 2

    t = np.linspace(0, 4 * np.pi, n)

    radius = t / (4 * np.pi)

    x1 = radius * np.cos(t)
    y1 = radius * np.sin(t)

    x2 = -radius * np.cos(t)
    y2 = -radius * np.sin(t)

    class1 = np.column_stack((x1, y1))
    class2 = np.column_stack((x2, y2))

    X = np.vstack((class1, class2))
    y = np.concatenate((np.zeros(n), np.ones(n)))

    X += np.random.normal(0, noise, X.shape)

    return X, y


def generate_dataset():

    if DATASET == "easy":

        return make_moons(
            n_samples=SAMPLES,
            noise=NOISE,
            random_state=SEED
        )

    elif DATASET == "medium":

        return make_circles(
            n_samples=SAMPLES,
            noise=NOISE,
            factor=0.5,
            random_state=SEED
        )

    elif DATASET == "hard":

        return generate_spirals(
            SAMPLES,
            noise=0.04
        )

    else:
        raise ValueError(
            "DATASET must be easy, medium or hard"
        )


X, y = generate_dataset()

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=SEED,
    stratify=y
)


# Convert to tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)

X_val = torch.tensor(X_val, dtype=torch.float32)
y_val = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)


# DataLoader for mini-batch training
train_loader = DataLoader(
    TensorDataset(X_train, y_train),
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)


# ==========================================
# NEURAL NETWORK
# ==========================================

class NeuralNetwork(nn.Module):

    def __init__(self):

        super().__init__()

        layers = []
        input_size = 2

        for _ in range(HIDDEN_LAYERS):

            layers.append(
                nn.Linear(input_size, HIDDEN_SIZE)
            )

            layers.append(nn.ReLU())

            input_size = HIDDEN_SIZE

        layers.append(nn.Linear(input_size, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


model = NeuralNetwork().to(device)


# ==========================================
# LOSS AND OPTIMIZER
# ==========================================

criterion = nn.BCEWithLogitsLoss()


def create_optimizer():

    return optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )


optimizer = create_optimizer()


# ==========================================
# EVALUATION
# ==========================================

def evaluate_model():

    model.eval()

    with torch.inference_mode():

        train_predictions = model(X_train)
        val_predictions = model(X_val)

        train_accuracy = (
            (train_predictions >= 0) == (y_train >= 0.5)
        ).float().mean().item()

        val_accuracy = (
            (val_predictions >= 0) == (y_val >= 0.5)
        ).float().mean().item()

        val_loss = criterion(
            val_predictions,
            y_val
        ).item()

    return train_accuracy, val_accuracy, val_loss


# ==========================================
# TRAINING
# ==========================================

def train_model(epochs):

    for epoch in range(epochs):

        model.train()

        for X_batch, y_batch in train_loader:

            predictions = model(X_batch)

            loss = criterion(predictions, y_batch)

            optimizer.zero_grad(set_to_none=True)

            loss.backward()

            optimizer.step()

    return evaluate_model()


# ==========================================
# PRUNING
# ==========================================

def apply_pruning(amount):

    for module in model.modules():

        if isinstance(module, nn.Linear):

            prune.l1_unstructured(
                module,
                name="weight",
                amount=amount
            )


def make_pruning_permanent():

    for module in model.modules():

        if isinstance(module, nn.Linear):

            if hasattr(module, "weight_orig"):

                prune.remove(module, "weight")


def calculate_sparsity():

    total = 0
    zeros = 0

    for module in model.modules():

        if isinstance(module, nn.Linear):

            total += module.weight.numel()

            zeros += (
                module.weight == 0
            ).sum().item()

    return zeros / total


# ==========================================
# INITIAL TRAINING
# ==========================================

print(f"\nDataset: {DATASET.upper()}")
print("Training initial network...")

start_time = time.time()

train_acc, val_acc, val_loss = train_model(
    INITIAL_EPOCHS
)

initial_accuracy = val_acc

# Save original network for comparison
baseline_model = copy.deepcopy(model)
baseline_model.eval()

# Keep best network in case pruning becomes harmful
best_model = copy.deepcopy(model)

print(
    f"Initial accuracy: {val_acc * 100:.2f}%"
)


# ==========================================
# ITERATIVE PRUNING
# ==========================================

accuracies = [val_acc]
train_accuracies = [train_acc]
sparsities = [0.0]

print("\nStarting iterative pruning...")

for iteration in range(PRUNE_ITERATIONS):

    # Save current best model
    previous_model = copy.deepcopy(model)

    # Remove least important connections
    apply_pruning(PRUNE_AMOUNT)

    # Recreate optimizer to clear old Adam momentum
    optimizer = create_optimizer()

    # Retrain remaining connections
    train_acc, val_acc, val_loss = train_model(
        RETRAIN_EPOCHS
    )

    accuracy_drop = initial_accuracy - val_acc

    # Stop if accuracy loss is too large
    if accuracy_drop > MAX_ACCURACY_DROP:

        model = previous_model

        print(
            f"Iteration {iteration + 1}: "
            f"Accuracy limit reached. Stopping."
        )

        break

    # Accept new model
    best_model = copy.deepcopy(model)

    sparsity = calculate_sparsity()

    accuracies.append(val_acc)
    train_accuracies.append(train_acc)
    sparsities.append(sparsity)

    print(
        f"Iteration {iteration + 1:02d} | "
        f"Accuracy: {val_acc * 100:.2f}% | "
        f"Sparsity: {sparsity * 100:.1f}%"
    )


# ==========================================
# FINALIZE MODEL
# ==========================================

model = best_model

make_pruning_permanent()

final_train_acc, final_val_acc, final_loss = evaluate_model()

total_time = time.time() - start_time

torch.save(
    model.state_dict(),
    f"pruned_{DATASET}.pth"
)

print("\n================================")
print("FINAL RESULTS")
print("================================")

print(f"Dataset:       {DATASET}")
print(f"Accuracy:      {initial_accuracy * 100:.2f}% -> {final_val_acc * 100:.2f}%")
print(f"Sparsity:      {calculate_sparsity() * 100:.2f}%")
print(f"Training time: {total_time:.2f} seconds")

print(f"Saved: pruned_{DATASET}.pth")


# ==========================================
# VISUALIZATION
# ==========================================

model.eval()

# Generate decision boundary grid
x_min, x_max = X[:, 0].min() - 0.2, X[:, 0].max() + 0.2
y_min, y_max = X[:, 1].min() - 0.2, X[:, 1].max() + 0.2

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 200),
    np.linspace(y_min, y_max, 200)
)

grid = torch.tensor(
    np.c_[xx.ravel(), yy.ravel()],
    dtype=torch.float32
)

with torch.inference_mode():

    Z_before = torch.sigmoid(
        baseline_model(grid)
    ).numpy()

    Z_after = torch.sigmoid(
        model(grid)
    ).numpy()

Z_before = Z_before.reshape(xx.shape)
Z_after = Z_after.reshape(xx.shape)


# Create figure
fig, axes = plt.subplots(2, 2, figsize=(13, 9))


# ------------------------------------------
# BEFORE PRUNING
# ------------------------------------------

axes[0, 0].contourf(
    xx, yy, Z_before >= 0.5,
    alpha=0.3,
    cmap="coolwarm"
)

axes[0, 0].scatter(
    X[:, 0], X[:, 1],
    c=y,
    cmap="coolwarm",
    edgecolors="black",
    s=18
)

axes[0, 0].set_title(
    f"Before pruning ({initial_accuracy * 100:.2f}%)"
)


# ------------------------------------------
# AFTER PRUNING
# ------------------------------------------

axes[0, 1].contourf(
    xx, yy, Z_after >= 0.5,
    alpha=0.3,
    cmap="coolwarm"
)

axes[0, 1].scatter(
    X[:, 0], X[:, 1],
    c=y,
    cmap="coolwarm",
    edgecolors="black",
    s=18
)

axes[0, 1].set_title(
    f"After pruning ({final_val_acc * 100:.2f}%)"
)


# ------------------------------------------
# ACCURACY
# ------------------------------------------

iterations = range(len(accuracies))

axes[1, 0].plot(
    iterations,
    np.array(train_accuracies) * 100,
    marker="o",
    label="Training"
)

axes[1, 0].plot(
    iterations,
    np.array(accuracies) * 100,
    marker="o",
    label="Validation"
)

axes[1, 0].axhline(
    initial_accuracy * 100,
    color="red",
    linestyle="--",
    label="Original validation"
)

axes[1, 0].set_title("Accuracy during pruning")
axes[1, 0].set_xlabel("Pruning iteration")
axes[1, 0].set_ylabel("Accuracy (%)")
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)


# ------------------------------------------
# NETWORK DENSITY
# ------------------------------------------

axes[1, 1].plot(
    range(len(sparsities)),
    np.array(sparsities) * 100,
    marker="o",
    color="orange",
    label="Sparsity"
)

axes[1, 1].plot(
    range(len(sparsities)),
    (1 - np.array(sparsities)) * 100,
    marker="o",
    color="green",
    label="Remaining weights"
)

axes[1, 1].set_title("Network density")
axes[1, 1].set_xlabel("Pruning iteration")
axes[1, 1].set_ylabel("Weights (%)")
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)


# ------------------------------------------
# FINAL FIGURE
# ------------------------------------------

fig.suptitle(
    f"{DATASET.upper()} DATASET | "
    f"Pruning experiment | "
    f"Accuracy drop: "
    f"{(initial_accuracy - final_val_acc) * 100:.2f} pp",
    fontsize=13
)

plt.tight_layout()

plt.savefig(
    f"results_{DATASET}.png",
    dpi=150
)

plt.show()
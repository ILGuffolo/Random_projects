import copy
import os
import time
import queue
import threading
import traceback

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.utils.prune as prune

import tkinter as tk
from tkinter import ttk, messagebox

from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import make_moons, make_circles
from sklearn.model_selection import train_test_split

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "Neural Network Experiment Studio"

DEVICE = torch.device("cpu")

torch.set_num_threads(1)


# ============================================================
# DATASET REGISTRY
#
# Add new datasets here.
#
# Every dataset function must accept:
#     samples, noise, seed
#
# And return:
#     X, y
# ============================================================

def generate_moons(samples, noise, seed):

    return make_moons(
        n_samples=samples,
        noise=noise,
        random_state=seed
    )


def generate_circles(samples, noise, seed):

    return make_circles(
        n_samples=samples,
        noise=noise,
        factor=0.5,
        random_state=seed
    )


def generate_spirals(samples, noise, seed):

    n = samples // 2

    rng = np.random.default_rng(seed)

    t = np.linspace(0, 4 * np.pi, n)

    radius = t / (4 * np.pi)

    x1 = radius * np.cos(t)
    y1 = radius * np.sin(t)

    x2 = -radius * np.cos(t)
    y2 = -radius * np.sin(t)

    class1 = np.column_stack((x1, y1))
    class2 = np.column_stack((x2, y2))

    X = np.vstack((class1, class2))

    y = np.concatenate((
        np.zeros(n),
        np.ones(n)
    ))

    X += rng.normal(0, noise, X.shape)

    return X, y


DATASET_REGISTRY = {
    "Easy - Moons": generate_moons,
    "Medium - Circles": generate_circles,
    "Hard - Spirals": generate_spirals,
}


# ============================================================
# NETWORK ARCHITECTURE REGISTRY
#
# New architectures can be added here in the future.
# ============================================================

class NeuralNetwork(nn.Module):

    def __init__(
        self,
        input_size=2,
        hidden_size=128,
        hidden_layers=3,
        output_size=1
        ):


        super().__init__()

        layers = []

        current_size = input_size

        for _ in range(hidden_layers):

            layers.append(
                nn.Linear(current_size, hidden_size)
            )

            layers.append(nn.ReLU())

            current_size = hidden_size

        layers.append(
            nn.Linear(current_size, output_size)
        )

        self.network = nn.Sequential(*layers)

    def forward(self, x):

        return self.network(x)


ARCHITECTURE_REGISTRY = {
    "Fully Connected": NeuralNetwork,
}


# ============================================================
# PRUNING STRATEGY REGISTRY
#
# To add another pruning method, register its function here.
# ============================================================

def l1_pruning(module, amount):

    prune.l1_unstructured(
        module,
        name="weight",
        amount=amount
    )


PRUNING_REGISTRY = {
    "L1 Unstructured": l1_pruning,
}


# ============================================================
# EXPERIMENT ENGINE
#
# No GUI code belongs in this class.
# ============================================================

class ExperimentEngine:

    def __init__(
        self,
        config,
        progress_callback=None,
        cancel_event=None
    ):

        self.config = config

        self.progress_callback = progress_callback

        self.cancel_event = cancel_event

        self.device = DEVICE

        self.model = None
        self.optimizer = None

        self.criterion = nn.BCEWithLogitsLoss()

        self.X_train = None
        self.X_val = None

        self.y_train = None
        self.y_val = None

        self.train_loader = None

        self.total_epochs = 0
        self.completed_epochs = 0

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    def prepare_dataset(self):

        dataset_function = DATASET_REGISTRY[
            self.config["dataset"]
        ]

        X, y = dataset_function(
            self.config["samples"],
            self.config["noise"],
            self.config["seed"]
        )

        X_train, X_val, y_train, y_val = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=self.config["seed"],
            stratify=y
        )

        self.X_train = torch.tensor(
            X_train,
            dtype=torch.float32
        )

        self.X_val = torch.tensor(
            X_val,
            dtype=torch.float32
        )

        self.y_train = torch.tensor(
            y_train,
            dtype=torch.float32
        ).view(-1, 1)

        self.y_val = torch.tensor(
            y_val,
            dtype=torch.float32
        ).view(-1, 1)

        self.train_loader = DataLoader(
            TensorDataset(
                self.X_train,
                self.y_train
            ),
            batch_size=self.config["batch_size"],
            shuffle=True,
            num_workers=0
        )

        return X, y

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    def create_model(self):

        architecture = ARCHITECTURE_REGISTRY[
            self.config["architecture"]
        ]

        self.model = architecture(
            hidden_size=self.config["hidden_size"],
            hidden_layers=self.config["hidden_layers"]
        ).to(self.device)

        self.create_optimizer()

    def create_optimizer(self):

        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config["learning_rate"]
        )

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    def evaluate(self):

        self.model.eval()

        with torch.inference_mode():

            train_predictions = self.model(self.X_train)

            val_predictions = self.model(self.X_val)

            train_accuracy = (
                (train_predictions >= 0)
                == (self.y_train >= 0.5)
            ).float().mean().item()

            val_accuracy = (
                (val_predictions >= 0)
                == (self.y_val >= 0.5)
            ).float().mean().item()

            val_loss = self.criterion(
                val_predictions,
                self.y_val
            ).item()

        return train_accuracy, val_accuracy, val_loss

    # --------------------------------------------------------
    # TRAINING
    # --------------------------------------------------------

    def train(self, epochs, phase):

        for epoch in range(epochs):

            self.check_cancelled()

            self.model.train()

            for X_batch, y_batch in self.train_loader:

                self.check_cancelled()

                predictions = self.model(X_batch)

                loss = self.criterion(
                    predictions,
                    y_batch
                )

                self.optimizer.zero_grad(
                    set_to_none=True
                )

                loss.backward()

                self.optimizer.step()

            self.completed_epochs += 1

            if self.progress_callback:

                self.progress_callback(
                    self.completed_epochs,
                    self.total_epochs,
                    phase,
                    epoch + 1,
                    epochs
                )

        return self.evaluate()

    # --------------------------------------------------------
    # PRUNING
    # --------------------------------------------------------

    def apply_pruning(self):

        strategy = PRUNING_REGISTRY[
            self.config["pruning_strategy"]
        ]

        for module in self.model.modules():

            if isinstance(module, nn.Linear):

                strategy(
                    module,
                    self.config["prune_amount"]
                )

    def make_pruning_permanent(self):

        for module in self.model.modules():

            if isinstance(module, nn.Linear):

                if hasattr(module, "weight_orig"):

                    prune.remove(
                        module,
                        "weight"
                    )

    def calculate_sparsity(self):

        total = 0
        zeros = 0

        for module in self.model.modules():

            if isinstance(module, nn.Linear):

                total += module.weight.numel()

                zeros += (
                    module.weight == 0
                ).sum().item()

        if total == 0:
            return 0.0

        return zeros / total

    def check_cancelled(self):

        if (
            self.cancel_event is not None
            and self.cancel_event.is_set()
        ):
            raise InterruptedError(
                "Training cancelled by user."
            )

    # --------------------------------------------------------
    # DECISION BOUNDARY
    # --------------------------------------------------------

    def calculate_boundary(self, model, X):

        x_min = X[:, 0].min() - 0.2
        x_max = X[:, 0].max() + 0.2

        y_min = X[:, 1].min() - 0.2
        y_max = X[:, 1].max() + 0.2

        xx, yy = np.meshgrid(
            np.linspace(x_min, x_max, 200),
            np.linspace(y_min, y_max, 200)
        )

        grid = torch.tensor(
            np.c_[xx.ravel(), yy.ravel()],
            dtype=torch.float32
        )

        model.eval()

        with torch.inference_mode():

            Z = torch.sigmoid(
                model(grid)
            ).numpy()

        return xx, yy, Z.reshape(xx.shape)

    # --------------------------------------------------------
    # COMPLETE EXPERIMENT
    # --------------------------------------------------------

    def run(self):

        self.check_cancelled()

        start_time = time.time()

        # Dataset

        X, y = self.prepare_dataset()
        self.check_cancelled()

        # Model

        self.create_model()

        initial_epochs = self.config["initial_epochs"]

        retrain_epochs = self.config["retrain_epochs"]

        iterations = (
            self.config["prune_iterations"]
            if self.config["use_pruning"]
            else 0
        )

        self.total_epochs = (
            initial_epochs
            + iterations * retrain_epochs
        )

        self.completed_epochs = 0

        # Initial training

        train_acc, val_acc, val_loss = self.train(
            initial_epochs,
            "Initial training"
        )

        initial_accuracy = val_acc

        baseline_model = copy.deepcopy(self.model)

        best_model = copy.deepcopy(self.model)

        best_accuracy = val_acc

        # History

        accuracies = [val_acc]

        train_accuracies = [train_acc]

        sparsities = [0.0]

        # Iterative pruning

        if self.config["use_pruning"]:

            for iteration in range(iterations):

                self.check_cancelled()

                previous_model = copy.deepcopy(
                    self.model
                )

                # Remove less important weights

                self.apply_pruning()

                # Reset optimizer

                self.create_optimizer()

                # Retrain

                train_acc, val_acc, val_loss = self.train(
                    retrain_epochs,
                    f"Pruning iteration {iteration + 1}"
                )

                accuracy_drop = (
                    initial_accuracy - val_acc
                )

                # Reject harmful pruning

                if accuracy_drop > self.config["max_accuracy_drop"]:

                    self.model = previous_model

                    print(
                        "Pruning stopped: accuracy limit reached."
                    )

                    break

                # Accept pruning

                best_model = copy.deepcopy(self.model)

                best_accuracy = val_acc

                accuracies.append(val_acc)

                train_accuracies.append(train_acc)

                sparsities.append(
                    self.calculate_sparsity()
                )

        # Final model

        self.model = best_model

        self.make_pruning_permanent()

        final_train_acc, final_val_acc, final_loss = (
            self.evaluate()
        )

        total_time = time.time() - start_time

        # Decision boundaries

        X_numpy = X

        xx, yy, Z_before = self.calculate_boundary(
            baseline_model,
            X_numpy
        )

        _, _, Z_after = self.calculate_boundary(
            self.model,
            X_numpy
        )

        # Save model

        os.makedirs("experiments", exist_ok=True)

        dataset_name = (
            self.config["dataset"]
            .split(" - ")[1]
            .lower()
        )

        model_path = (
            f"experiments/model_{dataset_name}.pth"
        )

        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "config": self.config,
                "initial_accuracy": initial_accuracy,
                "final_accuracy": final_val_acc,
                "sparsity": self.calculate_sparsity()
            },
            model_path
        )

        # Return everything required by the GUI

        return {

            "X": X,
            "y": y,

            "xx": xx,
            "yy": yy,

            "Z_before": Z_before,
            "Z_after": Z_after,

            "initial_accuracy": initial_accuracy,
            "final_accuracy": final_val_acc,

            "train_accuracy": final_train_acc,

            "final_loss": final_loss,

            "accuracies": accuracies,
            "train_accuracies": train_accuracies,
            "sparsities": sparsities,

            "training_time": total_time,

            "parameters": sum(
                p.numel()
                for p in self.model.parameters()
            ),

            "sparsity": self.calculate_sparsity(),

            "model_path": model_path
        }

# ============================================================
# SCROLLABLE FRAME
# ============================================================

class ScrollableFrame(ttk.Frame):

    def __init__(self, parent):

        super().__init__(parent)

        self.canvas = tk.Canvas(
            self,
            bg="#20242c",
            highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )

        self.inner = ttk.Frame(self.canvas)

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.inner.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content
        )

        # Mouse wheel support

        self.canvas.bind(
            "<Enter>",
            self.enable_mousewheel
        )

        self.canvas.bind(
            "<Leave>",
            self.disable_mousewheel
        )

    def update_scroll_region(self, event=None):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def resize_content(self, event):

        self.canvas.itemconfigure(
            self.window_id,
            width=event.width
        )

    def enable_mousewheel(self, event=None):

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        # Linux mouse wheel support

        self.canvas.bind_all(
            "<Button-4>",
            lambda e: self.canvas.yview_scroll(-1, "units")
        )

        self.canvas.bind_all(
            "<Button-5>",
            lambda e: self.canvas.yview_scroll(1, "units")
        )

    def disable_mousewheel(self, event=None):

        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def on_mousewheel(self, event):

        self.canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )



# ============================================================
# GUI
# ============================================================

class NeuralNetworkStudio:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_NAME)

        self.root.geometry("1250x850")

        self.root.minsize(950, 700)

        self.root.configure(
            bg="#20242c"
        )

        self.events = queue.Queue()

        self.cancel_event = threading.Event()

        self.training_thread = None

        self.results = None

        self.setup_style()

        self.create_interface()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

        self.root.after(
            100,
            self.process_events
        )

    # --------------------------------------------------------
    # STYLE
    # --------------------------------------------------------

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            ".",
            font=("Segoe UI", 10)
        )

        style.configure(
            "TFrame",
            background="#20242c"
        )

        style.configure(
            "TLabel",
            background="#20242c",
            foreground="#eeeeee"
        )

        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 20, "bold"),
            foreground="#61a5fa"
        )

        style.configure(
            "Sub.TLabel",
            foreground="#aaaaaa"
        )

        style.configure(
            "TLabelframe",
            background="#20242c",
            foreground="#61a5fa"
        )

        style.configure(
            "TLabelframe.Label",
            background="#20242c",
            foreground="#61a5fa",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "TButton",
            padding=8
        )

        style.configure(
            "Start.TButton",
            background="#2563eb",
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Start.TButton",
            background=[
                ("active", "#1d4ed8"),
                ("disabled", "#555555")
            ]
        )

        style.configure(
            "Horizontal.TProgressbar",
            background="#3b82f6",
            troughcolor="#383e49",
            thickness=15
        )

        style.configure(
            "TCheckbutton",
            background="#20242c",
            foreground="#eeeeee"
        )

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------

    def show_error_dialog(self, error):

        window = tk.Toplevel(self.root)

        window.title("Training Error")

        window.geometry("750x500")

        window.minsize(450, 300)

        window.configure(
            bg="#20242c"
        )

        window.transient(self.root)

        window.grab_set()

        # Header

        ttk.Label(
            window,
            text="Something went wrong",
            font=("Segoe UI", 16, "bold"),
            foreground="#f87171"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        ttk.Label(
            window,
            text="You can select, copy and inspect the full error below.",
            style="Sub.TLabel"
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # Error text area

        text_frame = ttk.Frame(window)

        text_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical"
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        error_text = tk.Text(
            text_frame,
            wrap="none",
            font=("Consolas", 10),
            bg="#15191f",
            fg="#fca5a5",
            insertbackground="white",
            selectbackground="#2563eb",
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )

        error_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.configure(
            command=error_text.yview
        )

        error_text.insert(
            "1.0",
            error
        )

        # Keep editable/selectable so Ctrl+C works

        error_text.focus_set()

        error_text.bind(
            "<Control-a>",
            lambda e: (
                error_text.tag_add("sel", "1.0", "end"),
                "break"
            )
        )

        # Buttons

        button_frame = ttk.Frame(window)

        button_frame.pack(
            fill="x",
            padx=15,
            pady=15
        )

        def copy_error():

            window.clipboard_clear()

            window.clipboard_append(error)

            window.update()

            copy_button.configure(
                text="✓ Copied!"
            )

            window.after(
                1500,
                lambda: copy_button.configure(
                    text="Copy full error"
                )
            )

        copy_button = ttk.Button(
            button_frame,
            text="Copy full error",
            command=copy_error
        )

        copy_button.pack(
            side="left"
        )

        ttk.Button(
            button_frame,
            text="Close",
            command=window.destroy
        ).pack(
            side="right"
        )

        window.bind(
            "<Escape>",
            lambda e: window.destroy()
        )


    def create_interface(self):

        main = ttk.Frame(
            self.root,
            padding=15
        )

        main.pack(
            fill="both",
            expand=True
        )

        # Header

        ttk.Label(
            main,
            text="Neural Network Studio",
            style="Header.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            main,
            text="Train, prune, experiment and visualize neural networks.",
            style="Sub.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        # Notebook

        self.notebook = ttk.Notebook(main)

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.setup_tab = ttk.Frame(
            self.notebook,
            padding=15
        )

        self.results_tab = ttk.Frame(
            self.notebook,
            padding=10
        )

        self.notebook.add(
            self.setup_tab,
            text="  Experiment Setup  "
        )

        self.notebook.add(
            self.results_tab,
            text="  Results  "
        )

        self.create_setup_tab()

        self.create_results_tab()

    # --------------------------------------------------------
    # SETUP TAB
    # --------------------------------------------------------

    def create_setup_tab(self):

        tab = self.setup_tab

        # Scrollable container

        self.setup_scroll = ScrollableFrame(tab)

        self.setup_scroll.pack(
            fill="both",
            expand=True
        )

        left = self.setup_scroll.inner

        # Dataset

        dataset_frame = ttk.LabelFrame(
            left,
            text="Dataset",
            padding=12
        )

        dataset_frame.pack(
            fill="x",
            pady=5
        )

        self.dataset_var = tk.StringVar(
            value="Hard - Spirals"
        )

        self.add_combo(
            dataset_frame,
            "Dataset",
            self.dataset_var,
            list(DATASET_REGISTRY.keys())
        )

        self.samples_var = tk.IntVar(value=1200)
        self.noise_var = tk.DoubleVar(value=0.04)

        self.add_spin(
            dataset_frame, "Samples",
            self.samples_var, 100, 10000, 100
        )

        self.add_spin(
            dataset_frame, "Noise",
            self.noise_var, 0, 1, 0.01
        )

        # Neural Network

        network_frame = ttk.LabelFrame(
            left,
            text="Neural Network",
            padding=12
        )

        network_frame.pack(
            fill="x",
            pady=5
        )

        self.architecture_var = tk.StringVar(
            value="Fully Connected"
        )

        self.add_combo(
            network_frame,
            "Architecture",
            self.architecture_var,
            list(ARCHITECTURE_REGISTRY.keys())
        )

        self.hidden_size_var = tk.IntVar(value=128)
        self.hidden_layers_var = tk.IntVar(value=3)

        self.add_spin(
            network_frame, "Neurons per hidden layer",
            self.hidden_size_var, 4, 1024, 16
        )

        self.add_spin(
            network_frame, "Hidden layers",
            self.hidden_layers_var, 1, 10, 1
        )

        # Training

        training_frame = ttk.LabelFrame(
            left,
            text="Training Parameters",
            padding=12
        )

        training_frame.pack(
            fill="x",
            pady=5
        )

        self.epochs_var = tk.IntVar(value=200)
        self.retrain_var = tk.IntVar(value=40)
        self.batch_var = tk.IntVar(value=64)
        self.lr_var = tk.DoubleVar(value=0.001)
        self.seed_var = tk.IntVar(value=42)

        self.add_spin(
            training_frame, "Initial epochs",
            self.epochs_var, 1, 5000, 10
        )

        self.add_spin(
            training_frame, "Retraining epochs",
            self.retrain_var, 1, 1000, 5
        )

        self.add_spin(
            training_frame, "Batch size",
            self.batch_var, 8, 1024, 8
        )

        self.add_spin(
            training_frame, "Learning rate",
            self.lr_var, 0.00001, 0.1, 0.0001
        )

        self.add_spin(
            training_frame, "Random seed",
            self.seed_var, 0, 999999, 1
        )

        # Pruning

        pruning_frame = ttk.LabelFrame(
            left,
            text="Network Pruning",
            padding=12
        )

        pruning_frame.pack(
            fill="x",
            pady=5
        )

        self.pruning_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            pruning_frame,
            text="Enable iterative pruning",
            variable=self.pruning_var,
            command=self.toggle_pruning
        ).pack(
            anchor="w",
            pady=5
        )

        self.pruning_options = ttk.Frame(
            pruning_frame
        )

        self.pruning_options.pack(
            fill="x"
        )

        self.strategy_var = tk.StringVar(
            value="L1 Unstructured"
        )

        self.add_combo(
            self.pruning_options,
            "Pruning strategy",
            self.strategy_var,
            list(PRUNING_REGISTRY.keys())
        )

        self.prune_amount_var = tk.DoubleVar(value=0.20)
        self.iterations_var = tk.IntVar(value=10)
        self.max_drop_var = tk.DoubleVar(value=0.02)

        self.add_spin(
            self.pruning_options,
            "Pruning amount per iteration",
            self.prune_amount_var,
            0.01, 0.90, 0.05
        )

        self.add_spin(
            self.pruning_options,
            "Maximum iterations",
            self.iterations_var,
            1, 50, 1
        )

        self.add_spin(
            self.pruning_options,
            "Maximum accuracy drop",
            self.max_drop_var,
            0, 0.50, 0.01
        )

        self.toggle_pruning()

        # Progress

        progress_frame = ttk.LabelFrame(
            left,
            text="Training Progress",
            padding=12
        )

        progress_frame.pack(
            fill="x",
            pady=10
        )

        self.progress_var = tk.DoubleVar(value=0)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )

        self.progress_bar.pack(
            fill="x",
            pady=5
        )

        self.status_var = tk.StringVar(
            value="Ready to start."
        )

        ttk.Label(
            progress_frame,
            textvariable=self.status_var
        ).pack(
            anchor="w"
        )

        # Start button

        self.start_button = ttk.Button(
            left,
            text="▶  START TRAINING",
            style="Start.TButton",
            command=self.start_training
        )

        self.start_button.pack(
            fill="x",
            pady=10
        )


    # --------------------------------------------------------
    # INPUT HELPERS
    # --------------------------------------------------------

    def close_application(self):

        # Request cancellation of active training

        self.cancel_event.set()

        # Destroy GUI immediately.
        # Training thread is daemonized.

        self.root.destroy()

    def add_combo(self, parent, label, variable, values):

        row = ttk.Frame(parent)

        row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            row,
            text=label,
            width=30
        ).pack(
            side="left"
        )

        ttk.Combobox(
            row,
            textvariable=variable,
            values=values,
            state="readonly",
            width=27
        ).pack(
            side="right"
        )

    def add_spin(
        self,
        parent,
        label,
        variable,
        minimum,
        maximum,
        step
    ):

        row = ttk.Frame(parent)

        row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            row,
            text=label,
            width=30
        ).pack(
            side="left"
        )

        ttk.Spinbox(
            row,
            textvariable=variable,
            from_=minimum,
            to=maximum,
            increment=step,
            width=25
        ).pack(
            side="right"
        )

    # --------------------------------------------------------
    # PRUNING ENABLE / DISABLE
    # --------------------------------------------------------

    def toggle_pruning(self):

        state = (
            "normal"
            if self.pruning_var.get()
            else "disabled"
        )

        for child in self.pruning_options.winfo_children():

            try:

                child.configure(state=state)

                for subchild in child.winfo_children():

                    try:
                        subchild.configure(state=state)
                    except tk.TclError:
                        pass

            except tk.TclError:
                pass

    # --------------------------------------------------------
    # COLLECT CONFIGURATION
    # --------------------------------------------------------

    def get_config(self):

        config = {

            "dataset": self.dataset_var.get(),

            "samples": self.samples_var.get(),

            "noise": self.noise_var.get(),

            "architecture": self.architecture_var.get(),

            "hidden_size": self.hidden_size_var.get(),

            "hidden_layers": self.hidden_layers_var.get(),

            "initial_epochs": self.epochs_var.get(),

            "retrain_epochs": self.retrain_var.get(),

            "batch_size": self.batch_var.get(),

            "learning_rate": self.lr_var.get(),

            "seed": self.seed_var.get(),

            "use_pruning": self.pruning_var.get(),

            "pruning_strategy": self.strategy_var.get(),

            "prune_amount": self.prune_amount_var.get(),

            "prune_iterations": self.iterations_var.get(),

            "max_accuracy_drop": self.max_drop_var.get()
        }

        if config["samples"] < 100:
            raise ValueError("Use at least 100 samples.")

        if config["samples"] % 2 != 0:
            raise ValueError("Samples must be an even number.")

        if config["hidden_size"] < 1:
            raise ValueError("Hidden size must be positive.")

        if config["hidden_layers"] < 1:
            raise ValueError("Use at least one hidden layer.")

        if not 0 < config["learning_rate"] <= 0.1:
            raise ValueError("Invalid learning rate.")

        if not 0 <= config["noise"] <= 1:
            raise ValueError("Invalid noise value.")

        if config["use_pruning"]:

            if not 0 < config["prune_amount"] < 1:
                raise ValueError("Pruning amount must be between 0 and 1.")

            if not 0 <= config["max_accuracy_drop"] <= 1:
                raise ValueError("Invalid accuracy drop limit.")

        return config

    # --------------------------------------------------------
    # START TRAINING
    # --------------------------------------------------------

    def start_training(self):

        if self.training_thread and self.training_thread.is_alive():
            return

        self.cancel_event.clear()

        try:

            config = self.get_config()

        except (ValueError, tk.TclError) as error:

            messagebox.showerror(
                "Invalid configuration",
                str(error)
            )

            return

        self.progress_var.set(0)

        self.status_var.set(
            "Initializing experiment..."
        )

        self.start_button.configure(
            state="disabled"
        )

        self.notebook.select(
            self.setup_tab
        )

        self.training_thread = threading.Thread(
            target=self.training_worker,
            args=(config,),
            daemon=True
        )

        self.training_thread.start()

    # --------------------------------------------------------
    # BACKGROUND WORKER
    # --------------------------------------------------------

    def training_worker(self, config):

        try:

            engine = ExperimentEngine(
                config,
                self.progress_callback,
                self.cancel_event
            )

            results = engine.run()

            self.events.put((
                "finished",
                results
            ))

        except InterruptedError:

            self.events.put((
                "cancelled",
                None
            ))

        except Exception:

            self.events.put((
                "error",
                traceback.format_exc()
            ))

    # --------------------------------------------------------
    # PROGRESS CALLBACK
    # --------------------------------------------------------

    def progress_callback(
        self,
        completed,
        total,
        phase,
        epoch,
        phase_epochs
    ):

        self.events.put((
            "progress",
            completed,
            total,
            phase,
            epoch,
            phase_epochs
        ))

    # --------------------------------------------------------
    # EVENT QUEUE
    # --------------------------------------------------------

    def process_events(self):

        try:

            while True:

                event = self.events.get_nowait()

                event_type = event[0]

                if event_type == "progress":

                    _, completed, total, phase, epoch, phase_epochs = event

                    percentage = (
                        completed / total * 100
                        if total > 0
                        else 0
                    )

                    self.progress_var.set(
                        percentage
                    )

                    self.status_var.set(
                        f"{phase} | "
                        f"Epoch {epoch}/{phase_epochs} | "
                        f"Overall {percentage:.1f}%"
                    )

                elif event_type == "finished":

                    results = event[1]

                    self.results = results

                    self.start_button.configure(
                        state="normal"
                    )

                    self.progress_var.set(100)

                    self.status_var.set(
                        "Training completed successfully."
                    )

                    self.display_results(results)

                    self.notebook.select(
                        self.results_tab
                    )

                    messagebox.showinfo(
                        "Experiment completed",
                        "Training completed successfully!\n\n"
                        f"Final accuracy: "
                        f"{results['final_accuracy'] * 100:.2f}%\n"
                        f"Sparsity: "
                        f"{results['sparsity'] * 100:.2f}%"
                    )

                elif event_type == "error":

                    error = event[1]

                    self.start_button.configure(
                        state="normal"
                    )

                    self.status_var.set(
                        "Experiment failed."
                    )

                    self.show_error_dialog(error)

                elif event_type == "cancelled":

                    self.status_var.set(
                        "Training cancelled."
                    )

                    self.start_button.configure(
                        state="normal"
                    )

        except queue.Empty:
            pass

        except Exception:

            error = traceback.format_exc()

            self.start_button.configure(
                state="normal"
            )

            self.status_var.set(
                "Error while displaying results."
            )

            self.show_error_dialog(error)

        finally:

            if self.root.winfo_exists():

                self.root.after(
                    100,
                    self.process_events
                )

    # --------------------------------------------------------
    # RESULTS TAB
    # --------------------------------------------------------

    def create_results_tab(self):

        tab = self.results_tab

        self.metrics_frame = ttk.Frame(tab)

        self.metrics_frame.pack(
            fill="x",
            pady=5
        )

        # Matplotlib figure

        self.figure, self.axes = plt.subplots(
            2,
            2,
            figsize=(11, 7)
        )

        self.figure.patch.set_facecolor(
            "#20242c"
        )

        self.figure.tight_layout(
            pad=3
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=tab
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self.result_status = ttk.Label(
            tab,
            text="Run an experiment to see results here.",
            style="Sub.TLabel"
        )

        self.result_status.pack(
            anchor="w",
            pady=5
        )

    # --------------------------------------------------------
    # RESULTS VISUALIZATION
    # --------------------------------------------------------

    def display_results(self, results):

        # Clear previous metrics

        for widget in self.metrics_frame.winfo_children():

            widget.destroy()

        # Metric cards

        metrics = [

            (
                "Initial accuracy",
                f"{results['initial_accuracy'] * 100:.2f}%"
            ),

            (
                "Final accuracy",
                f"{results['final_accuracy'] * 100:.2f}%"
            ),

            (
                "Network sparsity",
                f"{results['sparsity'] * 100:.2f}%"
            ),

            (
                "Training time",
                f"{results['training_time']:.2f}s"
            ),

            (
                "Parameters",
                f"{results['parameters']:,}"
            ),

            (
                "Validation loss",
                f"{results['final_loss']:.4f}"
            )
        ]

        for i, (label, value) in enumerate(metrics):

            card = tk.Frame(
                self.metrics_frame,
                bg="#303744",
                padx=12,
                pady=10
            )

            card.grid(
                row=0,
                column=i,
                padx=4,
                sticky="nsew"
            )

            tk.Label(
                card,
                text=label,
                bg="#303744",
                fg="#aaaaaa",
                font=("Segoe UI", 9)
            ).pack()

            tk.Label(
                card,
                text=value,
                bg="#303744",
                fg="#61a5fa",
                font=("Segoe UI", 14, "bold")
            ).pack()

            self.metrics_frame.columnconfigure(
                i,
                weight=1
            )

        # Reset plots

        for ax in self.axes.flat:

            ax.clear()

            ax.set_facecolor("#303744")

            ax.tick_params(
                colors="#dddddd"
            )

            for spine in ax.spines.values():

                spine.set_color("#555555")

        X = results["X"]
        y = results["y"]

        xx = results["xx"]
        yy = results["yy"]

        # BEFORE PRUNING

        ax = self.axes[0, 0]

        ax.contourf(
            xx,
            yy,
            results["Z_before"] >= 0.5,
            alpha=0.35,
            cmap="coolwarm"
        )

        ax.scatter(
            X[:, 0],
            X[:, 1],
            c=y,
            cmap="coolwarm",
            edgecolors="black",
            s=15
        )

        ax.set_title(
            f"Before pruning "
            f"({results['initial_accuracy'] * 100:.2f}%)",
            color="white"
        )

        # AFTER PRUNING

        ax = self.axes[0, 1]

        ax.contourf(
            xx,
            yy,
            results["Z_after"] >= 0.5,
            alpha=0.35,
            cmap="coolwarm"
        )

        ax.scatter(
            X[:, 0],
            X[:, 1],
            c=y,
            cmap="coolwarm",
            edgecolors="black",
            s=15
        )

        ax.set_title(
            f"After pruning "
            f"({results['final_accuracy'] * 100:.2f}%)",
            color="white"
        )

        # ACCURACY

        ax = self.axes[1, 0]

        iterations = range(
            len(results["accuracies"])
        )

        ax.plot(
            iterations,
            np.array(results["train_accuracies"]) * 100,
            marker="o",
            color="#60a5fa",
            label="Training"
        )

        ax.plot(
            iterations,
            np.array(results["accuracies"]) * 100,
            marker="o",
            color="#4ade80",
            label="Validation"
        )

        ax.axhline(
            results["initial_accuracy"] * 100,
            color="#f87171",
            linestyle="--",
            label="Original validation"
        )

        ax.set_title(
            "Accuracy during pruning",
            color="white"
        )

        ax.set_xlabel(
            "Pruning iteration",
            color="white"
        )

        ax.set_ylabel(
            "Accuracy (%)",
            color="white"
        )

        ax.legend(
            facecolor="#303744",
            labelcolor="white"
        )

        ax.grid(
            alpha=0.2
        )

        # NETWORK SPARSITY

        ax = self.axes[1, 1]

        ax.plot(
            range(len(results["sparsities"])),
            np.array(results["sparsities"]) * 100,
            marker="o",
            color="#fb923c",
            label="Zero weights"
        )

        ax.plot(
            range(len(results["sparsities"])),
            (1 - np.array(results["sparsities"])) * 100,
            marker="o",
            color="#4ade80",
            label="Remaining weights"
        )

        ax.set_title(
            "Network density",
            color="white"
        )

        ax.set_xlabel(
            "Pruning iteration",
            color="white"
        )

        ax.set_ylabel(
            "Weights (%)",
            color="white"
        )

        ax.legend(
            facecolor="#303744",
            labelcolor="white"
        )

        ax.grid(
            alpha=0.2
        )

        self.figure.tight_layout(
            pad=3
        )

        self.canvas.draw()

        self.result_status.configure(
            text=(
                f"Model saved to: {results['model_path']} | "
                f"Accuracy change: "
                f"{(results['final_accuracy'] - results['initial_accuracy']) * 100:+.2f} "
                f"percentage points"
            )
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():

    root = tk.Tk()

    app = NeuralNetworkStudio(root)

    root.mainloop()


if __name__ == "__main__":

    main()

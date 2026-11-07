
import torch
import torch.nn as nn
import random

from dataset import load_dataset
from model import ChatbotModel

def evaluate(model, data, tokenizer, criterion, device):

    model.eval()
    total_loss = 0

    with torch.no_grad():

        for question, answer in data:

            input_ids = torch.tensor(
                [tokenizer.encode(question)],
                dtype=torch.long,
                device=device
            )

            target_ids = torch.tensor(
                [tokenizer.encode(answer)],
                dtype=torch.long,
                device=device
            )

            predictions = model(input_ids, target_ids)

            expected = target_ids[:, 1:]

            loss = criterion(
                predictions.reshape(-1, predictions.size(-1)),
                expected.reshape(-1)
            )

            total_loss += loss.item()

    model.train()

    return total_loss / max(len(data), 1)


def train():

    # Configuration
    EPOCHS = 500
    LEARNING_RATE = 0.001

    torch.manual_seed(42)
    random.seed(42)

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)

    # Load data
    conversations, tokenizer = load_dataset()
    
    # Split dataset
    random.shuffle(conversations)

    split = int(len(conversations) * 0.9)

    train_data = conversations[:split]
    val_data = conversations[split:]

    model = ChatbotModel(
        vocab_size=len(tokenizer.word_to_id)
    ).to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    criterion = nn.CrossEntropyLoss(
        ignore_index=0
    )

    print("Vocabulary size:", len(tokenizer.word_to_id))
    print("Training started...")

    model.train()

    for epoch in range(EPOCHS):

        total_loss = 0

        random.shuffle(train_data)

        for question, answer in train_data:

            input_ids = torch.tensor(
                [tokenizer.encode(question)],
                dtype=torch.long,
                device=device
            )

            target_ids = torch.tensor(
                [tokenizer.encode(answer)],
                dtype=torch.long,
                device=device
            )

            optimizer.zero_grad()

            predictions = model(
                input_ids,
                target_ids
            )

            expected = target_ids[:, 1:]

            loss = criterion(
                predictions.reshape(-1, predictions.size(-1)),
                expected.reshape(-1)
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0
            )

            optimizer.step()

            total_loss += loss.item()

        if (epoch + 1) % 25 == 0:

            train_loss = total_loss / len(train_data)

            val_loss = evaluate(
                model, val_data, tokenizer, criterion, device
            )

            print(
                f"Epoch {epoch+1}/{EPOCHS} "
                f"| Train: {train_loss:.4f} "
                f"| Validation: {val_loss:.4f}"
            )

    # Save model and vocabulary together
    torch.save(
        {
            "model_state": model.state_dict(),
            "word_to_id": tokenizer.word_to_id,
            "id_to_word": tokenizer.id_to_word
        },
        "models/chatbot.pth"
    )

    print("\nTraining complete!")
    print("Model saved to models/chatbot.pth")


if __name__ == "__main__":
    train()

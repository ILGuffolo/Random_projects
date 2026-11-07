
import torch

from model import ChatbotModel
from tokenizer import Tokenizer


class Chatbot:

    def __init__(self, path="models/chatbot.pth"):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        checkpoint = torch.load(
            path,
            map_location=self.device,
            weights_only=True
        )

        # Restore vocabulary
        self.tokenizer = Tokenizer()
        self.tokenizer.word_to_id = checkpoint["word_to_id"]
        self.tokenizer.id_to_word = {
            int(k): v
            for k, v in checkpoint["id_to_word"].items()
        }

        # Restore model
        self.model = ChatbotModel(
            vocab_size=len(self.tokenizer.word_to_id)
        ).to(self.device)

        self.model.load_state_dict(
            checkpoint["model_state"]
        )

        self.model.eval()

    
    def generate(
        self,
        message,
        max_length=30,
        temperature=0.8,
        top_k=5
    ):

        input_ids = torch.tensor(
            [self.tokenizer.encode(message)],
            dtype=torch.long,
            device=self.device
        )

        with torch.no_grad():

            hidden = self.model.encode(input_ids)

            token = torch.tensor(
                [[2]],
                dtype=torch.long,
                device=self.device
            )

            response = []

            for _ in range(max_length):

                logits, hidden = self.model.decode_step(
                    token, hidden
                )

                logits = logits[:, -1, :] / temperature

                # Never generate PAD, UNK or SOS
                logits[:, :3] = float("-inf")

                # Keep only the top-k candidates
                if top_k > 0:
                    values, _ = torch.topk(
                        logits, min(top_k, logits.size(-1))
                    )

                    threshold = values[:, -1].unsqueeze(1)

                    logits[logits < threshold] = float("-inf")

                # Convert scores into probabilities
                probabilities = torch.softmax(logits, dim=-1)

                # Randomly sample the next token
                next_token = torch.multinomial(
                    probabilities, num_samples=1
                )

                token_id = next_token.item()

                if token_id == 3:
                    break

                response.append(token_id)
                token = next_token

        return self.tokenizer.decode(response)



import torch
import torch.nn as nn


class ChatbotModel(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_size=128,
        hidden_size=256
    ):
        super().__init__()

        self.embedding = nn.Embedding(
            vocab_size,
            embedding_size,
            padding_idx=0
        )

        self.encoder = nn.GRU(
            embedding_size,
            hidden_size,
            batch_first=True
        )

        self.decoder = nn.GRU(
            embedding_size,
            hidden_size,
            batch_first=True
        )

        self.output_layer = nn.Linear(
            hidden_size,
            vocab_size
        )

    def encode(self, input_ids):
        embedded = self.embedding(input_ids)

        _, hidden = self.encoder(embedded)

        return hidden

    def decode_step(self, token, hidden):
        embedded = self.embedding(token)

        output, hidden = self.decoder(
            embedded,
            hidden
        )

        logits = self.output_layer(output)

        return logits, hidden

    def forward(self, input_ids, target_ids):
        hidden = self.encode(input_ids)

        decoder_input = target_ids[:, 0:1]

        outputs = []

        # Predict each target token
        for t in range(1, target_ids.size(1)):
            logits, hidden = self.decode_step(
                decoder_input, hidden
            )

            outputs.append(logits)

            # Teacher forcing
            decoder_input = target_ids[:, t:t+1]

        return torch.cat(outputs, dim=1)

from typing import Tuple

import torch
import torch.nn.functional as F
from torch import nn

from pipegoose.distributed.parallel_context import ParallelContext
from pipegoose.distributed.parallel_mode import ParallelMode
from pipegoose.nn.tensor_parallel._operations import reduce


class ParallelEmbedding(nn.Module):
    def __init__(self, num_embeddings: int, embedding_dim: int, parallel_context: ParallelContext):
        super().__init__()
        world_size = parallel_context.get_world_size(ParallelMode.TENSOR)

        assert num_embeddings % world_size == 0, "num_embeddings must be divisible by world_size"

        num_embeddings_per_partition = num_embeddings // world_size

        self.parallel_context = parallel_context
        self.weight = nn.Parameter(torch.randn(num_embeddings_per_partition, embedding_dim))
        self.vocab_start_idx, self.vocab_end_idx = self._get_vocab_range_idx(
            num_embeddings, parallel_context.get_local_rank(ParallelMode.TENSOR), world_size
        )

    def _get_vocab_range_idx(self, num_embeddings: int, rank: int, world_size: int) -> Tuple[int, int]:
        num_embeddings_per_partition = num_embeddings // world_size
        start_idx = rank * num_embeddings_per_partition
        end_idx = start_idx + num_embeddings_per_partition
        return start_idx, end_idx

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        input_mask = (input < self.vocab_start_idx) | (input >= self.vocab_end_idx)
        # align global embedding indices to local embedding indices
        masked_input = input.clone() - self.vocab_start_idx
        masked_input[input_mask] = 0

        parallel_output = F.embedding(masked_input, self.weight)
        parallel_output[input_mask, :] = 0.0
        out = parallel_output.clone()

        torch.distributed.barrier()
        output = reduce(parallel_output, parallel_context=self.parallel_context)
        torch.distributed.barrier()

        return output, out

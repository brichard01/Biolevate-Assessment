import json
import urllib.error
import urllib.request

from config import EMBEDDINGS_URL

BATCH_SIZE = 32
TIMEOUT_SECONDS = 10


class EmbeddingsUnavailable(Exception):
    pass


def embed(texts):
    # Returns one vector (list of 384 floats) per text, in the same order.
    vectors = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        request = urllib.request.Request(
            f"{EMBEDDINGS_URL}/embed",
            data=json.dumps({"inputs": batch, "truncate": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                vectors.extend(json.loads(response.read()))
        except (urllib.error.URLError, TimeoutError) as error:
            raise EmbeddingsUnavailable(f"Embeddings service at {EMBEDDINGS_URL} failed: {error}")

    return vectors


def to_pgvector(vector):
    return "[" + ",".join(str(value) for value in vector) + "]"

import json
import os
import urllib.request

EMBEDDINGS_URL = os.environ.get("EMBEDDINGS_URL", "http://localhost:8080")

BATCH_SIZE = 32


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
        with urllib.request.urlopen(request) as response:
            vectors.extend(json.loads(response.read()))

    return vectors


def to_pgvector(vector):
    return "[" + ",".join(str(value) for value in vector) + "]"

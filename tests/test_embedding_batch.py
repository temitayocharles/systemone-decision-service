from rag.app.embeddings import EmbeddingClient


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_embed_many_batches_ollama_inputs(monkeypatch):
    client = object.__new__(EmbeddingClient)
    client.provider = "ollama"
    client.model = "nomic-embed-text"
    client.ollama_host = "http://ollama"
    client.batch_size = 2

    calls = []

    def fake_post(url, json, timeout):
        calls.append(list(json["input"]))
        return Response({"embeddings": [[float(len(x))] for x in json["input"]]})

    monkeypatch.setattr("rag.app.embeddings.requests.post", fake_post)

    result = client.embed_many(["a", "bb", "ccc"])

    assert result == [[1.0], [2.0], [3.0]]
    assert calls == [["a", "bb"], ["ccc"]]


def test_embed_delegates_to_batch_path(monkeypatch):
    client = object.__new__(EmbeddingClient)
    monkeypatch.setattr(client, "embed_many", lambda texts: [[0.25]])
    assert client.embed("one") == [0.25]

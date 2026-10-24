"""Shared fixtures. Unit tests are fast and offline: no API key is read and no network is used."""
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE))
DATASET = CODE.parent / "dataset"


@pytest.fixture(autouse=True)
def no_llm_keys(monkeypatch):
    """Tests never see real provider keys, so nothing can reach the network."""
    for k in ("GEMINI_API_KEY", "MISTRAL_API_KEY", "GROQ_API_KEY", "NVIDIA_API_KEY"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture(scope="session")
def engine():
    """The real engine over the shipped dataset (skipped when the dataset is not next to code/)."""
    if not (DATASET / "deletion_requests.csv").exists():
        pytest.skip("dataset/ not present")
    from audit.engine import AuditEngine, IdentityResolver
    from audit.evidence import EvidenceStore
    from audit.media import MediaExtractor
    store = EvidenceStore(DATASET, MediaExtractor(prefer="auto"))
    return AuditEngine(DATASET, store, IdentityResolver(DATASET))

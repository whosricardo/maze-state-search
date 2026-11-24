# [IA] Codex – suporte de sintaxe para download e validação do cabeçalho TSV
import csv
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "data" / "dataset_parte2" / "soc-redditHyperlinks-body.tsv"
URL = "https://snap.stanford.edu/data/soc-redditHyperlinks-body.tsv"


def download():
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists():
        print(f"Dataset já presente em {DESTINATION}")
        return
    temporary = None
    try:
        with NamedTemporaryFile(dir=DESTINATION.parent, suffix=".tmp", delete=False) as target:
            temporary = Path(target.name)
            with urlopen(URL, timeout=60) as response:
                shutil.copyfileobj(response, target)
        with temporary.open(encoding="utf-8-sig", newline="") as source:
            fields = set(next(csv.reader(source, delimiter="\t"), ()))
            if not {"SOURCE_SUBREDDIT", "TARGET_SUBREDDIT", "TIMESTAMP"} <= fields or not (
                {"LINK_SENTIMENT", "POST_LABEL"} & fields
            ):
                raise ValueError("O arquivo baixado não possui o cabeçalho esperado.")
        temporary.replace(DESTINATION)
        print(f"Dataset salvo em {DESTINATION}")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    download()

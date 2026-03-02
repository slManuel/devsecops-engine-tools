import json
import base64
import os

def read_sbom_file_as_base64(sbom_filename: str) -> str:
    file_path = os.path.join(os.getcwd(), sbom_filename)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"SBOM file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    json.loads(content)

    return base64.b64encode(content.encode("utf-8")).decode("utf-8")

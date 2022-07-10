import json
import requests
from pathlib import Path


def upload_nft(image_path, metadata):
    if "image" not in metadata:
        with Path(image_path).open("rb") as fp:
            image_binary = fp.read()

        response = requests.post(
            "https://ipfs.infura.io:5001/api/v0/add", files={"file": image_binary}, timeout=1800
        )
        ipfs_hash = response.json()["Hash"]
        metadata["image"] = f"ipfs://{ipfs_hash}"

    metadata_str = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    response = requests.post("https://ipfs.infura.io:5001/api/v0/add", files={"file": metadata_str})
    ipfs_hash = response.json()["Hash"]
    print(f"{image_path} - {metadata['image']} - {ipfs_hash}")

    return ipfs_hash

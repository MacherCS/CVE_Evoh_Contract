#!/usr/bin/python3
import brownie
import pytest


def test_metadata_support(nft):
    metadata_interface_id = "0x5b5e139f"
    assert nft.supportsInterface(metadata_interface_id) is True


def test_name_symbol(nft):
    assert nft.name() == "Test NFT"
    assert nft.symbol() == "TEST"


@pytest.mark.parametrize("idx,uri", [(0, "a"), (1, "b"), (2, "c"), (3, "d"), (4, "e")])
def test_token_uri(nft, idx, uri):
    assert nft.tokenURI(idx) == uri


def test_token_uri_nonexisting(nft):
    with brownie.reverts("Query for nonexistent tokenId"):
        nft.tokenURI(1337)

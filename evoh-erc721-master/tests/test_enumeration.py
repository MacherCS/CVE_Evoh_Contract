#!/usr/bin/python3

import brownie


def test_enumeration_support(nft):
    enumeration_interface_id = "0x780e9d63"
    assert nft.supportsInterface(enumeration_interface_id) is True


def test_token_by_index_reverts(nft, accounts):
    with brownie.reverts():
        nft.tokenByIndex(6)


def test_token_of_owner_by_index(nft, accounts):
    nft.transferFrom(accounts[2], accounts[3], 4, {"from": accounts[2]})
    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[2]})
    nft.transferFrom(accounts[2], accounts[1], 2, {"from": accounts[2]})

    assert nft.tokenOfOwnerByIndex(accounts[1], 0) == 2
    with brownie.reverts():
        nft.tokenOfOwnerByIndex(accounts[1], 1)

    assert nft.tokenOfOwnerByIndex(accounts[2], 0) == 0
    assert nft.tokenOfOwnerByIndex(accounts[2], 1) == 3
    with brownie.reverts():
        nft.tokenOfOwnerByIndex(accounts[2], 2)

    assert nft.tokenOfOwnerByIndex(accounts[3], 0) == 1
    assert nft.tokenOfOwnerByIndex(accounts[3], 1) == 4
    with brownie.reverts():
        nft.tokenOfOwnerByIndex(accounts[3], 2)

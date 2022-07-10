#!/usr/bin/python3
import brownie
from brownie import ZERO_ADDRESS


def test_sender_balance_decreases(nft, accounts):
    balance = nft.balanceOf(accounts[2])

    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[2]})

    assert nft.balanceOf(accounts[2]) == balance - 1


def test_receiver_balance_increases(nft, accounts):
    balance = nft.balanceOf(accounts[3])

    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[2]})

    assert nft.balanceOf(accounts[3]) == balance + 1


def test_caller_balance_unaffected(nft, accounts):
    balance = nft.balanceOf(accounts[4])

    nft.approve(accounts[4], 1, {"from": accounts[2]})
    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[4]})

    assert nft.balanceOf(accounts[4]) == balance


def test_ownership_changes(nft, accounts):
    owner = nft.ownerOf(1)

    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[2]})

    assert nft.ownerOf(1) != owner


def test_total_supply_not_affected(nft, accounts):
    total_supply = nft.totalSupply()

    nft.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[2]})

    assert nft.totalSupply() == total_supply


def test_safe_transfer_from_approval(nft, accounts):
    nft.approve(accounts[4], 1, {"from": accounts[2]})
    nft.safeTransferFrom(accounts[2], accounts[4], 1, {"from": accounts[4]})
    assert nft.ownerOf(1) == accounts[4]


def test_safe_transfer_from_operator(nft, accounts):
    nft.setApprovalForAll(accounts[4], True, {"from": accounts[2]})
    nft.safeTransferFrom(accounts[2], accounts[3], 1, {"from": accounts[4]})
    assert nft.ownerOf(1) == accounts[3]


def test_transfer_no_approval(nft, accounts):
    with brownie.reverts("Caller is not owner nor approved"):
        nft.transferFrom(accounts[2], accounts[1], 1, {"from": accounts[4]})


def test_safe_transfer_nonexisting(nft, accounts):
    with brownie.reverts("Query for nonexistent tokenId"):
        nft.safeTransferFrom(accounts[0], accounts[1], 1337, {"from": accounts[0]})


def test_safe_transfer_to_zero_address(nft, accounts):
    with brownie.reverts():
        nft.safeTransferFrom(accounts[2], ZERO_ADDRESS, 1, {"from": accounts[2]})


def test_safe_transfer_from_no_approval(nft, accounts):
    with brownie.reverts("Caller is not owner nor approved"):
        nft.safeTransferFrom(accounts[0], accounts[1], 1, {"from": accounts[4]})


def test_safe_transfer_invalid_receiver(nft, accounts, receiver_invalid):
    with brownie.reverts("Transfer to non ERC721 receiver"):
        nft.safeTransferFrom(accounts[2], receiver_invalid, 1, {"from": accounts[2]})


def test_transfer_invalid_receiver(nft, accounts, receiver_invalid):
    nft.transferFrom(accounts[2], receiver_invalid, 1, {"from": accounts[2]})


def test_safe_transfer_invalid_receiver_return(nft, accounts, receiver_invalid_return):
    with brownie.reverts("Transfer to non ERC721 receiver"):
        nft.safeTransferFrom(accounts[2], receiver_invalid_return, 1, {"from": accounts[2]})


def test_safe_transfer_valid_receiver(nft, accounts, receiver_valid):
    nft.safeTransferFrom(accounts[2], receiver_valid, 1, {"from": accounts[2]})

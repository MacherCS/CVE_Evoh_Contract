#!/usr/bin/python3
import brownie
from brownie import ZERO_ADDRESS


def test_approve(nft, accounts):
    assert nft.getApproved(1) == ZERO_ADDRESS
    nft.approve(accounts[1], 1, {"from": accounts[2]})
    assert nft.getApproved(1) == accounts[1]


def test_change_approve(nft, accounts):
    nft.approve(accounts[1], 1, {"from": accounts[2]})
    nft.approve(accounts[0], 1, {"from": accounts[2]})
    assert nft.getApproved(1) == accounts[0]


def test_revoke_approve(nft, accounts):
    nft.approve(accounts[1], 1, {"from": accounts[2]})
    nft.approve(ZERO_ADDRESS, 1, {"from": accounts[2]})
    assert nft.getApproved(1) == ZERO_ADDRESS


def test_no_return_value(nft, accounts):
    tx = nft.approve(accounts[1], 1, {"from": accounts[2]})
    assert tx.return_value is None


def test_approval_event_fire(nft, accounts):
    tx = nft.approve(accounts[1], 1, {"from": accounts[2]})
    assert len(tx.events) == 1
    assert tx.events["Approval"].values() == [accounts[2], accounts[1], 1]


def test_illegal_approval(nft, accounts):
    with brownie.reverts("Not owner nor approved for all"):
        nft.approve(accounts[1], 1, {"from": accounts[1]})


def test_get_approved_nonexistent(nft, accounts):
    with brownie.reverts():
        nft.getApproved(1337)

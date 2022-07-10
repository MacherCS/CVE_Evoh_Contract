#!/usr/bin/python3
import brownie
from brownie import ZERO_ADDRESS


def test_balanceOf(nft):
    with brownie.reverts():
        nft.balanceOf(ZERO_ADDRESS)


def test_ownerOf(nft):
    with brownie.reverts():
        nft.ownerOf(5)

from brownie import web3
from brownie.network.account import Account
from itertools import zip_longest
from eth_utils import encode_hex
from eth_abi.packed import encode_abi_packed


class MerkleTree:
    def __init__(self, elements):
        self.elements = sorted(set(web3.keccak(hexstr=el) for el in elements))
        self.layers = MerkleTree.get_layers(self.elements)

    @property
    def root(self):
        return self.layers[-1][0]

    def get_proof(self, el):
        el = web3.keccak(hexstr=el)
        idx = self.elements.index(el)
        proof = []
        for layer in self.layers:
            pair_idx = idx + 1 if idx % 2 == 0 else idx - 1
            if pair_idx < len(layer):
                proof.append(encode_hex(layer[pair_idx]))
            idx //= 2
        return proof

    @staticmethod
    def get_layers(elements):
        layers = [elements]
        while len(layers[-1]) > 1:
            layers.append(MerkleTree.get_next_layer(layers[-1]))
        return layers

    @staticmethod
    def get_next_layer(elements):
        return [
            MerkleTree.combined_hash(a, b) for a, b in zip_longest(elements[::2], elements[1::2])
        ]

    @staticmethod
    def combined_hash(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return web3.keccak(b"".join(sorted([a, b])))


def generate_hash_proof(ipfs_hash_list):
    """
    Generate a hash proof.

    The merkle root should be provided within the constructor of `EvohClaimable`.
    """
    nodes = [
        encode_hex(encode_abi_packed(["uint256", "string"], [i, value]))
        for i, value in enumerate(ipfs_hash_list)
    ]
    tree = MerkleTree(nodes)
    return {
        "merkleRoot": encode_hex(tree.root),
        "proofs": [
            {
                "index": i,
                "hash": value,
                "proof": tree.get_proof(
                    encode_hex(encode_abi_packed(["uint256", "string"], [i, value]))
                ),
            }
            for i, value in enumerate(ipfs_hash_list)
        ],
    }


def generate_claim_proof(acct_list):
    """
    Generate a claim proof.

    The merkle root should then be added using `EvohClaimable.addClaimRoot`
    """
    acct_list = [i.address if isinstance(i, Account) else i for i in acct_list]
    nodes = [encode_hex(encode_abi_packed(["address"], [acct])) for acct in acct_list]
    tree = MerkleTree(nodes)
    return {
        "merkleRoot": encode_hex(tree.root),
        "proofs": {acct: tree.get_proof(acct) for acct in acct_list},
    }

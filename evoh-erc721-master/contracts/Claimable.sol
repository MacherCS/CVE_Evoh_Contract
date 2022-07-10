pragma solidity 0.8.3;

import "./EvohERC721.sol";

contract EvohClaimable is EvohERC721 {

    uint256 public maxTotalSupply;
    bytes32 public hashRoot;
    address public owner;
    uint256 public startTime;

    struct ClaimData {
        bytes32 root;
        uint256 count;
        uint256 limit;
        mapping(address => bool) claimed;
    }

    ClaimData[] public claimData;

    constructor(
        string memory _name,
        string memory _symbol,
        bytes32 _hashRoot,
        uint256 _maxTotalSupply,
        uint256 _startTime
    )
        EvohERC721(_name, _symbol)
    {
        owner = msg.sender;
        hashRoot = _hashRoot;
        maxTotalSupply = _maxTotalSupply;
        startTime = _startTime;
    }

    function addClaimRoots(bytes32[] calldata _merkleRoots, uint256[] calldata _claimLimits) external {
        require(msg.sender == owner);
        for (uint256 i = 0; i < _merkleRoots.length; i++) {
            ClaimData storage data = claimData.push();
            data.root = _merkleRoots[i];
            data.limit = _claimLimits[i];
        }
    }

    function isClaimed(uint256 _claimIndex, address _account) public view returns (bool) {
        return claimData[_claimIndex].claimed[_account];
    }

    /**
        @notice Claim an NFT using an eligible account
        @param _claimIndex Index of the claim hash to validate `_claimProof` against
        @param _claimProof Proof to validate against the claim root
     */
    function claim(
        uint256 _claimIndex,
        bytes32[] calldata _claimProof
    )
        external
    {
        require(block.timestamp >= startTime, "Cannot claim before start time");
        uint256 claimed = totalSupply;
        require(maxTotalSupply > claimed, "All NFTs claimed");

        // Verify the claim
        bytes32 node = keccak256(abi.encodePacked(msg.sender));
        ClaimData storage data = claimData[_claimIndex];

        require(_claimIndex < claimData.length, "Invalid merkleIndex");
        require(data.count < data.limit, "All NFTs claimed in this airdrop");
        require(!data.claimed[msg.sender], "User has claimed in this airdrop");
        require(verify(_claimProof, data.root, node), "Invalid claim proof");

        // Mark as claimed, write the hash and send the token.
        data.count++;
        data.claimed[msg.sender] = true;

        addOwnership(msg.sender, claimed);
        emit Transfer(address(0), msg.sender, claimed);
        totalSupply = claimed + 1;
    }

     /**
        @notice Submit NFT hashes on-chain.
        @param _indexes Indexes of the hashes being added.
        @param _hashes IPFS hashes being added.
        @param _proofs Proofs for the IPFS hashes. These are checked against `hashRoot`.
     */
    function submitHashes(
        uint256[] calldata _indexes,
        string[] calldata _hashes,
        bytes32[][] calldata _proofs
    ) external {
        require(_indexes.length == _proofs.length);
        bytes32 root = hashRoot;
        for (uint256 i = 0; i < _indexes.length; i++) {
            bytes32 node = keccak256(abi.encodePacked(_indexes[i], _hashes[i]));
            require(verify(_proofs[i], root, node), "Invalid hash proof");
            tokenURIs[_indexes[i]] = _hashes[i];
        }
    }

    function verify(
        bytes32[] calldata proof,
        bytes32 root,
        bytes32 leaf
    )
        internal
        pure
        returns (bool)
    {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            if (computedHash <= proofElement) {
                // Hash(current computed hash + current element of the proof)
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                // Hash(current element of the proof + current computed hash)
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        // Check if the computed hash (root) is equal to the provided root
        return computedHash == root;
    }

}

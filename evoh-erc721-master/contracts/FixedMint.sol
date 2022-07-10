pragma solidity 0.8.3;

import "./EvohERC721.sol";

contract EvohFixedMint is EvohERC721 {

    constructor(
        string memory _name,
        string memory _symbol,
        string[] memory _tokenURIs,
        address[] memory _owners
    )
        EvohERC721(_name, _symbol)
    {
        require(_tokenURIs.length == _owners.length);
        for (uint256 i = 0; i < _owners.length; i++) {
            tokenURIs[i] = _tokenURIs[i];
            addOwnership(_owners[i], i);
            emit Transfer(address(0), _owners[i], i);
        }
        totalSupply = _owners.length;
    }

}

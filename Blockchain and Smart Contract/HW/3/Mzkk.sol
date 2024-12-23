// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MZKKToken is ERC20, Ownable {
    uint256 public constant MAX_SUPPLY = 1000000 * 10 ** 18; // 1 million tokens

    // Constructor specifying the initial owner
    constructor() ERC20("MZKKToken", "MZKK") Ownable(msg.sender) {}

    function mint(uint256 amount) external onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Max supply exceeded");
        _mint(msg.sender, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}

contract MZKKNFT is ERC721, Ownable {
    uint256 public nextTokenId;
    mapping(uint256 => string) private _tokenURIs;
    mapping(address => uint256) private _royalties;

    // Constructor specifying the initial owner
    constructor() ERC721("MZKKNFT", "MZKN") Ownable(msg.sender) {}

    function mint(string calldata uri) external onlyOwner {
        _mint(msg.sender, nextTokenId);
        _setTokenURI(nextTokenId, uri);
        nextTokenId++;
    }

    function _setTokenURI(uint256 tokenId, string memory uri) internal {
        _tokenURIs[tokenId] = uri;
    }

    function getTokenURI(uint256 tokenId) external view returns (string memory) {
        return _tokenURIs[tokenId];
    }

    function setRoyalty(address creator, uint256 amount) external onlyOwner {
        _royalties[creator] = amount;
    }

    function getRoyalty(address creator) external view returns (uint256) {
        return _royalties[creator];
    }
}
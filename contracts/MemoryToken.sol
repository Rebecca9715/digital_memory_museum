// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MemoryToken
 * @dev NFT合约，用于铸造人文故事记忆代币
 * 支持用户自己铸造（公开铸造）和管理员铸造
 */
contract MemoryToken is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;
    
    // 铸造费用（设置为0实现免费铸造）
    uint256 public mintPrice = 0;
    
    // 是否启用公开铸造
    bool public publicMintEnabled = true;
    
    // 事件：当新的NFT被铸造时触发
    event TokenMinted(address indexed recipient, uint256 indexed tokenId, string tokenURI);

    constructor() ERC721("MemoryToken", "MEMORY") Ownable(msg.sender) {
        _tokenIdCounter = 0;
    }

    /**
     * @dev 用户自己铸造NFT（公开铸造）
     * @param _tokenURI NFT的元数据URI
     */
    function mint(string memory _tokenURI) public payable returns (uint256) {
        require(publicMintEnabled, "Public minting is disabled");
        require(msg.value >= mintPrice, "Insufficient payment");
        require(bytes(_tokenURI).length > 0, "Token URI cannot be empty");
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, _tokenURI);
        
        emit TokenMinted(msg.sender, tokenId, _tokenURI);
        return tokenId;
    }

    /**
     * @dev 管理员铸造NFT给指定地址（仅合约所有者）
     * @param recipient 接收NFT的地址
     * @param _tokenURI NFT的元数据URI
     */
    function mintToken(address recipient, string memory _tokenURI) 
        public 
        onlyOwner 
        returns (uint256) 
    {
        require(recipient != address(0), "Invalid recipient address");
        require(bytes(_tokenURI).length > 0, "Token URI cannot be empty");

        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        _safeMint(recipient, tokenId);
        _setTokenURI(tokenId, _tokenURI);

        emit TokenMinted(recipient, tokenId, _tokenURI);
        return tokenId;
    }

    /**
     * @dev 设置铸造价格（仅合约所有者）
     */
    function setMintPrice(uint256 _price) public onlyOwner {
        mintPrice = _price;
    }

    /**
     * @dev 启用或禁用公开铸造（仅合约所有者）
     */
    function setPublicMintEnabled(bool _enabled) public onlyOwner {
        publicMintEnabled = _enabled;
    }

    /**
     * @dev 提取合约余额（仅合约所有者）
     */
    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }

    /**
     * @dev 获取当前Token计数
     */
    function getCurrentTokenId() public view returns (uint256) {
        return _tokenIdCounter;
    }

    /**
     * @dev 获取用户拥有的所有NFT ID
     */
    function tokensOfOwner(address _owner) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(_owner);
        uint256[] memory tokenIds = new uint256[](tokenCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < _tokenIdCounter; i++) {
            if (_ownerOf(i) == _owner) {
                tokenIds[index] = i;
                index++;
            }
        }
        
        return tokenIds;
    }

    // 以下函数为必需的override
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

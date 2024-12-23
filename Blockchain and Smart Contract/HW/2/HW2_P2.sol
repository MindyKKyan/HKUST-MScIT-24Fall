// Blockchain HW2 Problem2
// 21108128 
// Mingzhen JIANG


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract RewardToken is ERC20, Ownable {
    constructor() ERC20("RewardToken", "RTK") {}

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}

contract FanEngagementSystem is Ownable {
    struct Activity {
        string activityType;
        string activityProof;
        bool verified;
    }

    struct LoyaltyTier {
        string tierName;
        uint256 threshold;
    }

    RewardToken public rewardToken;
    mapping(address => Activity[]) public activities;
    mapping(address => uint256) public totalTokens;
    LoyaltyTier[] public loyaltyTiers;
    uint256 public proposalCount;

    event TokensEarned(address indexed fan, uint256 amount, string activityType);
    event TokensTransferred(address indexed from, address indexed to, uint256 amount);
    event TokensRedeemed(address indexed fan, uint256 amount, string rewardType);
    event ProposalSubmitted(uint256 proposalId, string description);
    event Voted(uint256 proposalId, address indexed fan);

    constructor() {
        rewardToken = new RewardToken();
        loyaltyTiers.push(LoyaltyTier("Bronze", 100));
        loyaltyTiers.push(LoyaltyTier("Silver", 500));
        loyaltyTiers.push(LoyaltyTier("Gold", 1000));
    }

    // Earn tokens for completed activities
    function earnTokens(address fan, uint256 amount, string memory activityType, string memory activityProof) public onlyOwner {
        activities[fan].push(Activity(activityType, activityProof, false));
        totalTokens[fan] += amount;
        rewardToken.mint(fan, amount);
        emit TokensEarned(fan, amount, activityType);
    }

    // Transfer tokens between fans
    function transferTokens(address to, uint256 amount) public {
        require(rewardToken.balanceOf(msg.sender) >= amount, "Insufficient balance.");
        rewardToken.transfer(to, amount);
        emit TokensTransferred(msg.sender, to, amount);
    }

    // Redeem tokens for rewards
    function redeemTokens(uint256 amount, string memory rewardType) public {
        require(totalTokens[msg.sender] >= amount, "Insufficient tokens.");
        totalTokens[msg.sender] -= amount;
        rewardToken.burn(amount);
        emit TokensRedeemed(msg.sender, amount, rewardType);
    }

    // Submit proposals for new rewards
    function submitProposal(string memory proposalDescription) public {
        proposalCount++;
        emit ProposalSubmitted(proposalCount, proposalDescription);
    }

    // Vote on proposals
    function voteOnProposal(uint256 proposalId) public {
        // Implement voting logic (e.g., tracking votes for proposals)
        emit Voted(proposalId, msg.sender);
    }

    // Get fan loyalty tier based on token balance
    function getFanLoyaltyTier(address fan) public view returns (string memory) {
        uint256 tokens = totalTokens[fan];
        for (uint256 i = loyaltyTiers.length; i > 0; i--) {
            if (tokens >= loyaltyTiers[i - 1].threshold) {
                return loyaltyTiers[i - 1].tierName;
            }
        }
        return "No Tier";
    }

    // Get reward history for a fan
    function getRewardHistory(address fan) public view returns (string[] memory) {
        uint256 count = activities[fan].length;
        string[] memory rewardHistory = new string[](count);
        for (uint256 i = 0; i < count; i++) {
            rewardHistory[i] = activities[fan][i].activityType;
        }
        return rewardHistory;
    }
}

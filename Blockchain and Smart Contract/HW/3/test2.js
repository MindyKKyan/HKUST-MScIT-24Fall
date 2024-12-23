const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("FanEngagementSystem", function () {
  let RewardToken;
  let FanEngagementSystem;
  let rewardToken;
  let fanEngagementSystem;
  let owner;
  let fan1;
  let fan2;

  beforeEach(async function () {
    [owner, fan1, fan2] = await ethers.getSigners();
    
    // Deploy contracts
    RewardToken = await ethers.getContractFactory("RewardToken");
    FanEngagementSystem = await ethers.getContractFactory("FanEngagementSystem");
    
    fanEngagementSystem = await FanEngagementSystem.deploy();
    await fanEngagementSystem.deployed();
    
    // Get RewardToken address from FanEngagementSystem
    const rewardTokenAddress = await fanEngagementSystem.rewardToken();
    rewardToken = RewardToken.attach(rewardTokenAddress);
  });

    describe("Token Earning and Loyalty Tiers", function () {
    it("Should earn tokens and update loyalty tier", async function () {
      await fanEngagementSystem.earnTokens(
        fan1.address,
        200,
        "Watch Game",
        "proof123"
      );

      expect(await rewardToken.balanceOf(fan1.address)).to.equal(200);
      expect(await fanEngagementSystem.getFanLoyaltyTier(fan1.address))
        .to.equal("Bronze");

      await fanEngagementSystem.earnTokens(
        fan1.address,
        400,
        "Season Ticket",
        "proof456"
      );

      expect(await rewardToken.balanceOf(fan1.address)).to.equal(600);
      expect(await fanEngagementSystem.getFanLoyaltyTier(fan1.address))
        .to.equal("Gold");
    });

    it("Should store activity history", async function () {
      await fanEngagementSystem.earnTokens(
        fan1.address,
        100,
        "Watch Game",
        "proof123"
      );

      const history = await fanEngagementSystem.getRewardHistory(fan1.address);
      expect(history[0]).to.equal("Watch Game");
    });
  });

    describe("Token Transfers and Redemption", function () {
    beforeEach(async function () {
      await fanEngagementSystem.earnTokens(
        fan1.address,
        500,
        "Initial Balance",
        "proof"
      );
    });

    it("Should transfer tokens between fans", async function () {
      await rewardToken.connect(fan1).approve(fan1.address, 200);
      await fanEngagementSystem.connect(fan1).transferTokens(fan2.address, 200);

      expect(await rewardToken.balanceOf(fan1.address)).to.equal(300);
      expect(await rewardToken.balanceOf(fan2.address)).to.equal(200);
    });

    it("Should redeem tokens for rewards", async function () {
      await fanEngagementSystem.connect(fan1).redeemTokens(200, "VIP Access");
      
      expect(await rewardToken.balanceOf(fan1.address)).to.equal(300);
      expect(await fanEngagementSystem.totalTokens(fan1.address)).to.equal(300);
    });
  });

    describe("Proposal and Voting System", function () {
    it("Should submit proposals", async function () {
      await expect(fanEngagementSystem.submitProposal("New Reward Type"))
        .to.emit(fanEngagementSystem, "ProposalSubmitted")
        .withArgs(1, "New Reward Type");

      expect(await fanEngagementSystem.proposalCount()).to.equal(1);
    });

    it("Should allow voting on proposals", async function () {
      await fanEngagementSystem.submitProposal("New Reward Type");
      
      await expect(fanEngagementSystem.connect(fan1).voteOnProposal(1))
        .to.emit(fanEngagementSystem, "Voted")
        .withArgs(1, fan1.address);
    });
  });
});


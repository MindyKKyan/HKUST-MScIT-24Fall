const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("DecentralizedCharityFund", function () {
    let CharityFund, charityFund, owner, donor1, donor2, project1, project2;

    beforeEach(async function () {
        [owner, donor1, donor2, project1, project2] = await ethers.getSigners();

        // Deploy the contract
        const CharityFundFactory = await ethers.getContractFactory("DecentralizedCharityFund");
        charityFund = await CharityFundFactory.deploy();
    });

    it("Should allow users to donate and update their balances", async function () {
        await charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") });
        const donorBalance = await charityFund.donorBalances(donor1.address);

        expect(donorBalance).to.equal(ethers.utils.parseEther("1"));
    });

    it("Should emit Donated event on donation", async function () {
        await expect(charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") }))
            .to.emit(charityFund, "Donated")
            .withArgs(donor1.address, ethers.utils.parseEther("1"));
    });

    it("Should allow submitting funding requests", async function () {
        await charityFund
            .connect(owner)
            .submitFundingRequest(project1.address, ethers.utils.parseEther("2"), "Support Education");

        const [projectAddress, requestedAmount, description] = await charityFund.fundingRequests(0);

        expect(projectAddress).to.equal(project1.address);
        expect(requestedAmount).to.equal(ethers.utils.parseEther("2"));
        expect(description).to.equal("Support Education");
    });

    it("Should allow users to vote on funding requests", async function () {
        await charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") });

        await charityFund
            .connect(owner)
            .submitFundingRequest(project1.address, ethers.utils.parseEther("2"), "Support Education");

        await charityFund.connect(donor1).voteOnRequest(0);
        const requestVotes = (await charityFund.fundingRequests(0)).votes;

        expect(requestVotes).to.equal(ethers.utils.parseEther("1"));
    });

    it("Should prevent double voting", async function () {
        await charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") });

        await charityFund
            .connect(owner)
            .submitFundingRequest(project1.address, ethers.utils.parseEther("2"), "Support Education");

        await charityFund.connect(donor1).voteOnRequest(0);

        await expect(charityFund.connect(donor1).voteOnRequest(0)).to.be.revertedWith("You have already voted.");
    });

    it("Should allow finalizing a request if it has enough votes", async function () {
        await charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") });
        await charityFund.connect(donor2).donate({ value: ethers.utils.parseEther("1") });

        await charityFund
            .connect(owner)
            .submitFundingRequest(project1.address, ethers.utils.parseEther("1.5"), "Support Education");

        await charityFund.connect(donor1).voteOnRequest(0);
        await charityFund.connect(donor2).voteOnRequest(0);

        const projectInitialBalance = await ethers.provider.getBalance(project1.address);

        await charityFund.connect(owner).finalizeRequest(0);

        const projectFinalBalance = await ethers.provider.getBalance(project1.address);
        const requestFinalized = (await charityFund.fundingRequests(0)).finalized;

        expect(requestFinalized).to.equal(true);
        expect(projectFinalBalance.sub(projectInitialBalance)).to.equal(ethers.utils.parseEther("1.5"));
    });

    it("Should prevent finalizing a request without enough votes", async function () {
        await charityFund.connect(donor1).donate({ value: ethers.utils.parseEther("1") });

        await charityFund
            .connect(owner)
            .submitFundingRequest(project1.address, ethers.utils.parseEther("2"), "Support Education");

        await charityFund.connect(donor1).voteOnRequest(0);

        await expect(charityFund.connect(owner).finalizeRequest(0)).to.be.revertedWith(
            "Not enough votes to approve."
        );
    });
});

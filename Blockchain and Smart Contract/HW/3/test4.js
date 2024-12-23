const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("DecentralizedAuctionHouse", function () {
    let auctionHouse;
    let owner;
    let artist;
    let bidder1;
    let bidder2;

    beforeEach(async function () {
        [owner, artist, bidder1, bidder2] = await ethers.getSigners();
        const AuctionHouse = await ethers.getContractFactory("DecentralizedAuctionHouse");
        auctionHouse = await AuctionHouse.deploy();
        await auctionHouse.deployed();
    });

    it("should allow the artist to create an auction", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        const auction = await auctionHouse.auctions(0);
        expect(auction.artist).to.equal(artist.address);
        expect(auction.itemName).to.equal(itemName);
        expect(auction.reservePrice).to.equal(reservePrice);
        expect(auction.highestBid).to.equal(0);
        expect(auction.highestBidder).to.equal(ethers.constants.AddressZero);
        expect(auction.endTime).to.be.greaterThan(Math.floor(Date.now() / 1000));
        expect(auction.finalized).to.be.false;
    });

    it("should emit AuctionCreated event when an auction is created", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await expect(auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration))
            .to.emit(auctionHouse, "AuctionCreated")
            .withArgs(0, artist.address, itemName, reservePrice, auctionDuration + Math.floor(Date.now() / 1000));
    });

    it("should allow bidders to place bids", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") });

        const auction = await auctionHouse.auctions(0);
        expect(auction.highestBid).to.equal(ethers.utils.parseEther("1.5"));
        expect(auction.highestBidder).to.equal(bidder1.address);
    });

    it("should emit BidPlaced event when a bid is placed", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await expect(auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") }))
            .to.emit(auctionHouse, "BidPlaced")
            .withArgs(0, bidder1.address, ethers.utils.parseEther("1.5"));
    });

    it("should refund the previous highest bidder when a new bid is placed", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") });
        
        // Bidder 2 places a higher bid
        await expect(() => auctionHouse.connect(bidder2).placeBid(0, { value: ethers.utils.parseEther("2.0") }))
            .to.changeEtherBalances([bidder1, auctionHouse], [ethers.utils.parseEther("1.5"), ethers.utils.parseEther("-1.5")]);

        const auction = await auctionHouse.auctions(0);
        expect(auction.highestBid).to.equal(ethers.utils.parseEther("2.0"));
        expect(auction.highestBidder).to.equal(bidder2.address);
    });

    it("should not allow bids lower than the highest bid", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") });

        await expect(auctionHouse.connect(bidder2).placeBid(0, { value: ethers.utils.parseEther("1.0") }))
            .to.be.revertedWith("Bid amount must be higher than current highest bid.");
    });

    it("should not allow bids below the reserve price", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);

        await expect(auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("0.5") }))
            .to.be.revertedWith("Bid must meet reserve price.");
    });

    it("should allow bidders to withdraw their bids", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") });
        
        await expect(() => auctionHouse.connect(bidder1).withdrawBid(0))
            .to.changeEtherBalance(bidder1, ethers.utils.parseEther("1.5"));

        const auction = await auctionHouse.auctions(0);
        expect(auction.highestBid).to.equal(0);
        expect(auction.highestBidder).to.equal(ethers.constants.AddressZero);
    });

    it("should not allow the highest bidder to withdraw their bid", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("1.5") });

        await expect(auctionHouse.connect(bidder1).withdrawBid(0))
            .to.be.revertedWith("Highest bidder cannot withdraw.");
    });

    it("should finalize the auction and transfer funds to the artist", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 1; // 1 second for testing

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("2.0") });

        // Wait for auction to end
        await new Promise(resolve => setTimeout(resolve, 2000));

        await expect(() => auctionHouse.connect(artist).finalizeAuction(0))
            .to.changeEtherBalance(artist, ethers.utils.parseEther("2.0"));
        
        const auction = await auctionHouse.auctions(0);
        expect(auction.finalized).to.be.true;
    });

    it("should not allow finalizing an auction that has not ended", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);

        await expect(auctionHouse.connect(artist).finalizeAuction(0))
            .to.be.revertedWith("Auction is still active.");
    });

    it("should not allow finalizing an auction that has already been finalized", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 1; // 1 second for testing

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("2.0") });

        // Wait for auction to end
        await new Promise(resolve => setTimeout(resolve, 2000));

        await auctionHouse.connect(artist).finalizeAuction(0);

        await expect(auctionHouse.connect(artist).finalizeAuction(0))
            .to.be.revertedWith("Auction has already been finalized.");
    });

    it("should return auction details", async function () {
        const itemName = "Artwork 1";
        const reservePrice = ethers.utils.parseEther("1.0");
        const auctionDuration = 60 * 60; // 1 hour

        await auctionHouse.connect(artist).createAuction(itemName, reservePrice, auctionDuration);
        
        await auctionHouse.connect(bidder1).placeBid(0, { value: ethers.utils.parseEther("2.0") });

        const [name, highestBid, endTime, finalized] = await auctionHouse.getAuctionDetails(0);
        expect(name).to.equal(itemName);
        expect(highestBid).to.equal(ethers.utils.parseEther("2.0"));
        expect(endTime).to.be.greaterThan(Math.floor(Date.now() / 1000));
        expect(finalized).to.be.false;
    });
});
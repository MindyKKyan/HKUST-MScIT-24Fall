// Blockchain HW2 Problem4
// 21108128 
// Mingzhen JIANG


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract DecentralizedAuctionHouse is Ownable {
    struct Auction {
        address artist;
        string itemName;
        uint256 reservePrice;
        uint256 highestBid;
        address highestBidder;
        uint256 endTime;
        bool finalized;
    }

    Auction[] public auctions;

    event AuctionCreated(uint256 indexed auctionId, address indexed artist, string itemName, uint256 reservePrice, uint256 endTime);
    event BidPlaced(uint256 indexed auctionId, address indexed bidder, uint256 bidAmount);
    event BidWithdrawn(uint256 indexed auctionId, address indexed bidder, uint256 bidAmount);
    event AuctionFinalized(uint256 indexed auctionId, address indexed artist, address indexed winner, uint256 winningBid);

    // Constructor
    constructor() Ownable(msg.sender){}

    // Create a new auction
    function createAuction(string calldata itemName, uint256 reservePrice, uint256 auctionDuration) external {
        require(auctionDuration > 0, "Auction duration must be greater than zero.");

        uint256 endTime = block.timestamp + auctionDuration;
        auctions.push(Auction(msg.sender, itemName, reservePrice, 0, address(0), endTime, false));

        emit AuctionCreated(auctions.length - 1, msg.sender, itemName, reservePrice, endTime);
    }

    // Place a bid on an auction
    function placeBid(uint256 auctionId) external payable {
        Auction storage auction = auctions[auctionId];

        require(block.timestamp < auction.endTime, "Auction has ended.");
        require(msg.value > auction.highestBid, "Bid amount must be higher than current highest bid.");
        require(msg.value >= auction.reservePrice, "Bid must meet reserve price.");

        // Refund the previous highest bidder
        if (auction.highestBidder != address(0)) {
            payable(auction.highestBidder).transfer(auction.highestBid);
        }

        auction.highestBid = msg.value;
        auction.highestBidder = msg.sender;

        emit BidPlaced(auctionId, msg.sender, msg.value);
    }

    // Withdraw a bid
    function withdrawBid(uint256 auctionId) external {
        Auction storage auction = auctions[auctionId];

        require(block.timestamp < auction.endTime, "Auction has ended.");
        require(msg.sender != auction.highestBidder, "Highest bidder cannot withdraw.");

        uint256 refundAmount = auction.highestBid;
        auction.highestBid = 0;
        auction.highestBidder = address(0);

        payable(msg.sender).transfer(refundAmount);

        emit BidWithdrawn(auctionId, msg.sender, refundAmount);
    }

    // Finalize the auction
    function finalizeAuction(uint256 auctionId) external {
        Auction storage auction = auctions[auctionId];

        require(block.timestamp >= auction.endTime, "Auction is still active.");
        require(!auction.finalized, "Auction has already been finalized.");

        auction.finalized = true;

        if (auction.highestBidder != address(0)) {
            // Transfer ownership of the artwork and disburse funds to the artist
            emit AuctionFinalized(auctionId, auction.artist, auction.highestBidder, auction.highestBid);
            payable(auction.artist).transfer(auction.highestBid);
        }
    }

    // Get auction details
    function getAuctionDetails(uint256 auctionId) external view returns (string memory, uint256, uint256, bool) {
        Auction storage auction = auctions[auctionId];
        return (auction.itemName, auction.highestBid, auction.endTime, auction.finalized);
    }
}

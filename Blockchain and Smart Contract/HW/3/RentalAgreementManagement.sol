// Blockchain HW2 Problem3
// 21108128 
// Mingzhen JIANG

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract RentalAgreementManagement is Ownable {
    struct Agreement {
        address tenant;
        uint256 rentAmount;
        uint256 duration; // Duration in seconds
        uint256 startTime;
        bool isActive;
        uint256 totalPaid;
    }

    Agreement[] public agreements;

    event AgreementCreated(uint256 indexed agreementId, address indexed tenant, uint256 rentAmount, uint256 duration);
    event RentPaid(uint256 indexed agreementId, address indexed tenant, uint256 amount);
    event AgreementTerminated(uint256 indexed agreementId, address indexed landlord);

    // Constructor
    constructor() Ownable(msg.sender) {}

    // Create a rental agreement
    function createAgreement(address tenant, uint256 rentAmount, uint256 duration) public onlyOwner {
        require(tenant != address(0), "Invalid tenant address.");
        require(rentAmount > 0, "Rent amount must be greater than zero.");
        require(duration > 0, "Duration must be greater than zero.");

        uint256 agreementId = agreements.length;
        agreements.push(Agreement(tenant, rentAmount, duration, block.timestamp, true, 0));

        emit AgreementCreated(agreementId, tenant, rentAmount, duration);
    }

    // Pay rent for the agreement
    function payRent(uint256 agreementId) public payable {
        Agreement storage agreement = agreements[agreementId];

        require(msg.sender == agreement.tenant, "Only the tenant can pay rent.");
        require(agreement.isActive, "Agreement is not active.");
        require(msg.value == agreement.rentAmount, "Incorrect rent amount.");

        // Update payment records
        agreement.totalPaid += msg.value;

        emit RentPaid(agreementId, msg.sender, msg.value);
    }

    // Terminate an agreement
    function terminateAgreement(uint256 agreementId) public onlyOwner {
        Agreement storage agreement = agreements[agreementId];

        require(agreement.isActive, "Agreement is already terminated.");
        require(block.timestamp >= agreement.startTime + agreement.duration, "Agreement duration has not ended.");

        agreement.isActive = false;

        emit AgreementTerminated(agreementId, msg.sender);
    }

    // Get agreement status
    function getAgreementStatus(uint256 agreementId) public view returns (string memory) {
        Agreement storage agreement = agreements[agreementId];

        if (!agreement.isActive) {
            return "Terminated";
        } else if (block.timestamp < agreement.startTime + agreement.duration) {
            return "Active";
        } else {
            return "Expired";
        }
    }
}
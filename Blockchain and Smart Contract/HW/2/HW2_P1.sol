// Blockchain HW2 Problem1
// 21108128 
// Mingzhen JIANG

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DecentralizedCharityFund {
    struct FundingRequest {
        address projectAddress;
        uint256 requestedAmount;
        string projectDescription;
        uint256 votes;
        bool finalized;
    }

    mapping(address => uint256) public donorBalances;
    FundingRequest[] public fundingRequests;
    mapping(uint256 => mapping(address => bool)) public votes;
    uint256 public totalDonorBalance;

    event Donated(address indexed donor, uint256 amount);
    event FundingRequestSubmitted(uint256 requestId, address indexed projectAddress, uint256 requestedAmount);
    event Voted(uint256 requestId, address indexed donor);
    event RequestFinalized(uint256 requestId, address indexed projectAddress, uint256 amount);

    // Constructor
    constructor() {}

    // Donate Ether to the charity fund
    function donate() public payable {
        require(msg.value > 0, "Donation must be greater than zero.");

        donorBalances[msg.sender] += msg.value;
        totalDonorBalance += msg.value;

        emit Donated(msg.sender, msg.value);
    }

    // Submit a funding request
    function submitFundingRequest(address projectAddress, uint256 requestedAmount, string memory projectDescription) public {
        require(requestedAmount > 0, "Requested amount must be greater than zero.");
        require(projectAddress != address(0), "Invalid project address.");

        fundingRequests.push(FundingRequest({
            projectAddress: projectAddress,
            requestedAmount: requestedAmount,
            projectDescription: projectDescription,
            votes: 0,
            finalized: false
        }));

        emit FundingRequestSubmitted(fundingRequests.length - 1, projectAddress, requestedAmount);
    }

    // Vote on a funding request
    function voteOnRequest(uint256 requestId) public returns (bool) {
        require(requestId < fundingRequests.length, "Invalid request ID.");
        require(donorBalances[msg.sender] > 0, "You have no voting power.");
        require(!votes[requestId][msg.sender], "You have already voted.");

        votes[requestId][msg.sender] = true;
        fundingRequests[requestId].votes += donorBalances[msg.sender];

        emit Voted(requestId, msg.sender);
        return true;
    }

    // Finalize a funding request
    function finalizeRequest(uint256 requestId) public returns (bool) {
        require(requestId < fundingRequests.length, "Invalid request ID.");
        FundingRequest storage request = fundingRequests[requestId];
        require(!request.finalized, "Request already finalized.");
        require(request.votes > totalDonorBalance / 2, "Not enough votes to approve.");

        request.finalized = true;
        payable(request.projectAddress).transfer(request.requestedAmount);

        emit RequestFinalized(requestId, request.projectAddress, request.requestedAmount);
        return true;
    }

    // Get funding history
    function getFundingHistory() public view returns (address[] memory, uint256[] memory, string[] memory) {
        uint256 count = fundingRequests.length;
        address[] memory projectAddresses = new address[](count);
        uint256[] memory amounts = new uint256[](count);
        string[] memory descriptions = new string[](count);

        for (uint256 i = 0; i < count; i++) {
            projectAddresses[i] = fundingRequests[i].projectAddress;
            amounts[i] = fundingRequests[i].requestedAmount;
            descriptions[i] = fundingRequests[i].projectDescription;
        }

        return (projectAddresses, amounts, descriptions);
    }
}

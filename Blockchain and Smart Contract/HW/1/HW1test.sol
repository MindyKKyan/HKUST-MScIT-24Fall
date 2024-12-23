// Smart Contract for Rental Payments
contract RentalAgreement {
    address tenant;           // Alice
    address payable landlord; // Bob, must be payable to receive funds
    uint rentAmount;
    uint dueDate;             // Monthly due date in Unix timestamp
    uint penaltyAmount;
    bool isPaid;

    // Constructor to initialize the contract
    constructor(address _tenant, address payable _landlord, uint _rentAmount,
                uint _dueDate, uint _penaltyAmount) {
        tenant = _tenant;
        landlord = _landlord;
        rentAmount = _rentAmount;
        dueDate = _dueDate;
        penaltyAmount = _penaltyAmount;
        isPaid = false;
    }

    // Function to make rent payment
    function payRent() public payable {
        require(msg.sender == tenant, "Only the tenant can pay the rent.");
        // 5.1: Ensure rent is paid only once per month
        require(!isPaid, "Rent for this month has already been paid.");  
        
        // 5.2: Check if payment is late
        if (block.timestamp > dueDate) {
            // Apply penalty for late payment
            uint totalAmount = rentAmount + penaltyAmount;
            require(msg.value == totalAmount, "Incorrect payment amount with penalty.");
            landlord.transfer(totalAmount);
        } else {
            // Transfer rent to landlord without penalty
            require(msg.value == rentAmount, "Incorrect payment amount.");
            landlord.transfer(rentAmount);
        }

        isPaid = true;
    }

    // 5.3: Reset payment status at the start of each month
    function resetPaymentStatus() public {
        require(block.timestamp > dueDate && isPaid, 
                "Can only reset at the start of a new month after payment is made.");
        isPaid = false;

        // Update due date to the next month
        dueDate += 30 days;
    }

    // Function to check if rent is paid
    function checkPaymentStatus() public view returns (bool) {
        return isPaid;
    }
}

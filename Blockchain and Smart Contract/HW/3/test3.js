const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("RentalAgreementManagement", function () {
    let rentalManagement;
    let owner;
    let tenant;

    beforeEach(async function () {
        [owner, tenant] = await ethers.getSigners();
        const RentalAgreementManagement = await ethers.getContractFactory("RentalAgreementManagement");
        rentalManagement = await RentalAgreementManagement.deploy();
        await rentalManagement.deployed();
    });

    it("should allow the owner to create a rental agreement", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 30 * 24 * 60 * 60; // 30 days in seconds

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);

        const agreement = await rentalManagement.agreements(0);
        expect(agreement.tenant).to.equal(tenant.address);
        expect(agreement.rentAmount).to.equal(rentAmount);
        expect(agreement.duration).to.equal(duration);
        expect(agreement.isActive).to.be.true;
    });

    it("should emit an AgreementCreated event when an agreement is created", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 30 * 24 * 60 * 60; // 30 days in seconds

        await expect(rentalManagement.createAgreement(tenant.address, rentAmount, duration))
            .to.emit(rentalManagement, "AgreementCreated")
            .withArgs(0, tenant.address, rentAmount, duration);
    });

    it("should allow the tenant to pay rent", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 30 * 24 * 60 * 60; // 30 days in seconds

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        await expect(() => {
            return rentalManagement.connect(tenant).payRent(0, { value: rentAmount });
        }).to.changeEtherBalance(rentalManagement, rentAmount);

        const agreement = await rentalManagement.agreements(0);
        expect(agreement.totalPaid).to.equal(rentAmount);
    });

    it("should emit a RentPaid event when rent is paid", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 30 * 24 * 60 * 60; // 30 days in seconds

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        await expect(rentalManagement.connect(tenant).payRent(0, { value: rentAmount }))
            .to.emit(rentalManagement, "RentPaid")
            .withArgs(0, tenant.address, rentAmount);
    });

    it("should not allow non-tenants to pay rent", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 30 * 24 * 60 * 60; // 30 days in seconds

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        await expect(rentalManagement.connect(owner).payRent(0, { value: rentAmount }))
            .to.be.revertedWith("Only the tenant can pay rent.");
    });

    it("should allow the owner to terminate an agreement after its duration", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 1; // 1 second for testing

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        // Wait for the agreement to expire
        await new Promise(resolve => setTimeout(resolve, 2000));

        await rentalManagement.terminateAgreement(0);

        const agreement = await rentalManagement.agreements(0);
        expect(agreement.isActive).to.be.false;
    });

    it("should emit an AgreementTerminated event when an agreement is terminated", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 1; // 1 second for testing

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        // Wait for the agreement to expire
        await new Promise(resolve => setTimeout(resolve, 2000));

        await expect(rentalManagement.terminateAgreement(0))
            .to.emit(rentalManagement, "AgreementTerminated")
            .withArgs(0, owner.address);
    });

    it("should not allow terminating an agreement that is already terminated", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 1; // 1 second for testing

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);
        
        // Wait for the agreement to expire
        await new Promise(resolve => setTimeout(resolve, 2000));

        await rentalManagement.terminateAgreement(0);
        
        await expect(rentalManagement.terminateAgreement(0))
            .to.be.revertedWith("Agreement is already terminated.");
    });

    it("should return the correct status of an agreement", async function () {
        const rentAmount = ethers.utils.parseEther("1.0");
        const duration = 1; // 1 second for testing

        await rentalManagement.createAgreement(tenant.address, rentAmount, duration);

        let status = await rentalManagement.getAgreementStatus(0);
        expect(status).to.equal("Active");

        // Wait for the agreement to expire
        await new Promise(resolve => setTimeout(resolve, 2000));

        status = await rentalManagement.getAgreementStatus(0);
        expect(status).to.equal("Expired");

        await rentalManagement.terminateAgreement(0);
        status = await rentalManagement.getAgreementStatus(0);
        expect(status).to.equal("Terminated");
    });
});
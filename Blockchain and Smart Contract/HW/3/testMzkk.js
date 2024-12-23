const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MZKKToken", function () {
    let mzkkToken;
    let owner;
    let user;

    beforeEach(async function () {
        [owner, user] = await ethers.getSigners();
        const MZKKToken = await ethers.getContractFactory("MZKKToken");
        mzkkToken = await MZKKToken.deploy();
        await mzkkToken.deployed();
    });

    it("should mint tokens", async function () {
        await mzkkToken.mint(1000);
        expect(await mzkkToken.totalSupply()).to.equal(1000);
    });

    it("should not exceed max supply", async function () {
        await mzkkToken.mint(1000000); // Mint max supply
        await expect(mzkkToken.mint(1)).to.be.revertedWith("Max supply exceeded");
    });

    it("should allow token holders to burn tokens", async function () {
        await mzkkToken.mint(1000);
        await mzkkToken.burn(500);
        expect(await mzkkToken.totalSupply()).to.equal(500);
    });
});

describe("MZKKNFT", function () {
    let mzkkNFT;
    let owner;

    beforeEach(async function () {
        [owner] = await ethers.getSigners();
        const MZKKNFT = await ethers.getContractFactory("MZKKNFT");
        mzkkNFT = await MZKKNFT.deploy();
        await mzkkNFT.deployed();
    });

    it("should mint an NFT with a URI", async function () {
        await mzkkNFT.mint("http://example.com/metadata/1");
        expect(await mzkkNFT.getTokenURI(0)).to.equal("http://example.com/metadata/1");
    });

    it("should set royalty for a creator", async function () {
        await mzkkNFT.setRoyalty(owner.address, 10);
        expect(await mzkkNFT.getRoyalty(owner.address)).to.equal(10);
    });
});
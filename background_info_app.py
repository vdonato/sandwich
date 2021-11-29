import streamlit as st

"""
## Some useful things to know about Ethereum (and blockchains in general):

  * Transactions
    * Transactions are batched into blocks.
    * Transactions in the same block happen atomically.
    * ***BUT***, transaction ordering *within* a block may matter.
    * Pending transactions are sent to every node in the network, and while
      they are waiting for a miner to include them in a block, they're said
      to live in the "Mempool". Pending transactions are visible to all.
  * Gas
    * Gas is the fee that you pay so that a miner picks up and processes
      your transaction.
    * If you want your transaction to be processed earlier, you can pay
      more gas.
  * Market impact
    * In any market, buying or selling a LOT of an asset will affect the
      price and will push it up or down.
    * Example: look at what happened to TSLA after Elon sold a few billion
      dollars worth of it
  * DEXs: "Decentralized Exchanges"
    * Not operated by a centralized party (like Coinbase).
    * Instead, runs via smart contracts on a blockchain (like the Ethereum
      network).

### What is a 🥪 attack?

Essentially, it's a form of frontrunning, but it has some properties unique
to the blockchain.

Let's look at an example

  1. Mr. Whale put a few thousand dollars into Bitcoin in 2010, and now he
     has more money than he knows what to do with. His next play is to buy
     a bunch of this funny dog coin SHIB that everyone is talking about.
  2. He goes to Uniswap, a popular DEX, to buy some SHIB for USD
     (technically USDT).
  3. Señor Shark is keeping an eye on the mempool and sees a Uniswap
     transaction buying $1MM worth of SHIB. The transaction is offering 100
     gas to the miner in exchange for processing it. He then

     * Submits a buy for $100k worth of SHIB at a gas price of 101.
     * Simultaneously, he submits a sell for all of the SHIB he's about to
       buy.
  4. The miner then processes the transactions in this relative order:

     * Señor Shark's buy for $100k worth of SHIB
     * Mr. Whale's buy for $1MM worth of SHIB
     * Señor Shark's sell order for all of his SHIB
  5. Mr. Whale is sad because he got a worse average price that he would
     have gotten if Señor Shark hadn't made the sandwich attack.
"""

import pandas as pd
import streamlit as st

import sandwiches
import transactions
from sandwiches import calculate_profit, find_sandwiches_in_txs


@st.experimental_memo
def sandwich_data():
    # TODO: Remove the max_blocks parameter when running for real.
    txs_by_block = transactions.from_file(transactions.OUTPUT_FILE, max_blocks=1000)

    sandwiches_by_block = {}
    for block_number, txs in txs_by_block.items():
        sandos = find_sandwiches_in_txs(txs)
        if len(sandos) > 0:
            sandwiches_by_block[block_number] = sandos

    return sandwiches_by_block


@st.experimental_memo
def sandwich_profits_df():
    columns = [
        "block_number",
        "tx0",
        "tx1",
        "pair",
        "profit",
        "profitCoin",
    ]

    rows = []

    for block_number, sandwiches in sandwich_data().items():
        for sandwich in sandwiches:
            tx0, tx1 = sandwich

            swap = tx0["swaps"][0]
            coin0 = swap["pair"]["token0"]["symbol"]
            coin1 = swap["pair"]["token1"]["symbol"]

            profit = calculate_profit(sandwich)

            rows.append(
                [
                    block_number,
                    tx0["id"],
                    tx1["id"],
                    f"{coin0}/{coin1}",
                    profit[coin0] or profit[coin1],
                    coin0 if profit[coin0] > 0 else coin1,
                ]
            )

    return pd.DataFrame(columns=columns, data=rows)


@st.experimental_memo
def most_lucrative_sandwiches(coin):
    df = sandwich_profits_df()
    df = df[df["profitCoin"] == coin]
    return df.sort_values(by="profit", ascending=False).head().reset_index(drop=True)


@st.experimental_memo
def profits_by_coin():
    return sandwich_profits_df().groupby("profitCoin").agg("sum")[["profit"]]


@st.experimental_memo
def num_attacks_by_pair():
    return (
        sandwich_profits_df()
        .groupby(["pair"])
        .size()
        .reset_index(name="num_attacks")
        .sort_values(by="num_attacks", ascending=False)
        .reset_index(drop=True)
    )


@st.experimental_memo
def cumprofit_for_coin(coin):
    df = sandwich_profits_df()
    df = df[df["profitCoin"] == coin]
    df["total_profit"] = df["profit"].cumsum()
    df = df.filter(["block_number", "total_profit"]).set_index("block_number")
    return df


def txs_to_df(txs, sandwiches_in_block=None):
    txs = [tx for tx in txs if len(tx["swaps"]) > 0]
    txs.sort(key=lambda tx: int(tx["swaps"][0]["logIndex"]))
    columns = [
        "block_number",
        "tx",
        "pair",
        "coin0In",
        "coin0Out",
        "coin1In",
        "coin1Out",
        "logIndex",
    ]

    rows = []

    for tx in txs:
        swaps = tx["swaps"]

        for swap in swaps:
            coin0 = swap["pair"]["token0"]["symbol"]
            coin1 = swap["pair"]["token1"]["symbol"]
            pair = f"{coin0}/{coin1}"

            coin0In = float(swap["amount0In"])
            coin0Out = float(swap["amount0Out"])
            coin1In = float(swap["amount1In"])
            coin1Out = float(swap["amount1Out"])

            rows.append(
                [
                    int(tx["blockNumber"]),
                    tx["id"],
                    pair,
                    coin0In,
                    coin0Out,
                    coin1In,
                    coin1Out,
                    swap["logIndex"],
                ]
            )

    df = pd.DataFrame(columns=columns, data=rows)

    if sandwiches_in_block is not None:
        sandwich_tx_ids = set()
        for sando in sandwiches_in_block:
            tx0, tx1 = sando
            sandwich_tx_ids.add(tx0["id"])
            sandwich_tx_ids.add(tx1["id"])

        def highlight_tx_ids(val):
            bg_color = "red" if val in sandwich_tx_ids else "black"
            return f"background-color: {bg_color}"

        df = df.style.applymap(highlight_tx_ids)

    return df


"# Ethereum 🥪 attack data"

with st.expander("Background info"):
    """
    ### Some useful things to know about Ethereum (and blockchains in general):

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
      2. He goes to Uniswap, a popular DEX, to buy some SHIB for USDT
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


st.markdown("<br /> <br />", unsafe_allow_html=True)


"## All 🥪 attack profits"

"### Profits by coin"
st.dataframe(profits_by_coin())
"### Moost attacked pairs"
st.dataframe(num_attacks_by_pair())


st.markdown("<br /> <br />", unsafe_allow_html=True)


"## By coin"
coin = st.selectbox("Pick a coin", profits_by_coin().index)
f"### Profit vs time (block number) in {coin}"
st.line_chart(cumprofit_for_coin(coin))

f"### Most lucrative 🥪 attacks on {coin}"
st.dataframe(most_lucrative_sandwiches(coin))


st.markdown("<br /> <br />", unsafe_allow_html=True)


"## By block"
block_number = st.number_input("Input block number", value=0)

if block_number != 0:
    txs_in_block = transactions.fetch_txs_in_block(block_number)
    sandwiches_in_block = find_sandwiches_in_txs(txs_in_block)
    tx_df = txs_to_df(txs_in_block, sandwiches_in_block)
    st.dataframe(tx_df)

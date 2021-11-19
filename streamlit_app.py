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
def known_coins():
    coins = set()

    for block_number, sandwiches in sandwich_data().items():
        for sandwich in sandwiches:
            tx, _ = sandwich

            swap = tx["swaps"][0]
            coin0 = swap["pair"]["token0"]["symbol"]
            coin1 = swap["pair"]["token1"]["symbol"]

            coins.add(coin0)
            coins.add(coin1)

    return coins


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


st.header(f"All 🥪 attack profits")

st.subheader("Profits by coin")
st.write(profits_by_coin())
st.subheader("Most attacked pairs")
st.write(num_attacks_by_pair())

st.markdown("<br /> <br /> <br />", unsafe_allow_html=True)

coin = st.selectbox("Pick a coin", known_coins())

st.header(f"Profit vs time (block number) in {coin}")

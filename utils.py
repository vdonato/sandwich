import pandas as pd
import streamlit as st

import transactions
from sandwiches import calculate_profit, find_sandwiches_in_txs

@st.experimental_memo
def sandwich_data():
    txs_by_block = transactions.from_file(transactions.OUTPUT_FILE)

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

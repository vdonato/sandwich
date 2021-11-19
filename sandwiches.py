from collections import defaultdict


def _group_txs(txs):
    grouped_txs = defaultdict(list)

    for tx in txs:
        swap = tx["swaps"][0]
        pair = swap["pair"]

        token0 = pair["token0"]["symbol"]
        token1 = pair["token1"]["symbol"]
        pair_symbol = f"{token0}/{token1}"

        key = (pair_symbol, swap["to"])
        grouped_txs[key].append(tx)

    return grouped_txs


def is_pure_swap(tx):
    # Return True if and only if exactly one of x and y is zero.
    exactly_one_zero = lambda x, y: len([z for z in (x, y) if z == 0]) == 1

    swaps = tx["swaps"]
    if len(swaps) != 1:
        return False

    s = swaps[0]
    coin0In = float(s["amount0In"])
    coin0Out = float(s["amount0Out"])
    coin1In = float(s["amount1In"])
    coin1Out = float(s["amount1Out"])

    return exactly_one_zero(coin0In, coin0Out) and exactly_one_zero(coin1In, coin1Out)


log_index = lambda tx: int(tx["swaps"][0]["logIndex"])


def find_sandwiches_in_txs(txs):
    sandwiches = []

    # Drop txs with more than one swap for simplicity. This may cause us to
    # overlook some sandwich attacks that did indeed occur, but we expect
    # the effect to be minimal.
    txs = [tx for tx in txs if is_pure_swap(tx)]
    grouped_txs = _group_txs(txs)

    for _, group in grouped_txs.items():
        # We make another simplifying assumption here that may drop some
        # sandwich attacks, which is that the attacker will only submit two
        # attack transactions. Again, this is likely to be the case for the
        # overwhelming majority of attacks, so doing this is unlikely to make
        # much of a difference in our results.
        if len(group) == 2 and is_actually_sandwich(group):
            sandwiches.append(sorted(tuple(group), key=log_index))

    return sandwiches


def calculate_profit(sandwich_txs):
    tx0, tx1 = sandwich_txs
    swap0, swap1 = tx0["swaps"][0], tx1["swaps"][0]

    symbol0 = swap0["pair"]["token0"]["symbol"]
    symbol1 = swap0["pair"]["token1"]["symbol"]

    # We almost certainly lose a lot of accuracy by converting to floats here,
    # but we do so anyway for sake of time.
    tx0Coin0In = float(swap0["amount0In"])
    tx0Coin1In = float(swap0["amount1In"])
    tx0Coin0Out = float(swap0["amount0Out"])
    tx0Coin1Out = float(swap0["amount1Out"])

    tx1Coin0In = float(swap1["amount0In"])
    tx1Coin1In = float(swap1["amount1In"])
    tx1Coin0Out = float(swap1["amount0Out"])
    tx1Coin1Out = float(swap1["amount1Out"])

    profits = {}
    profits[symbol0] = (tx1Coin0Out - tx1Coin0In) - (tx0Coin0In - tx0Coin0Out)
    profits[symbol1] = (tx1Coin1Out - tx1Coin1In) - (tx0Coin1In - tx0Coin1Out)

    return profits


# TODO: Most of this code is duplicated from calculate_profit, and the two
# should be refactored / cleaned up if there's enough time.
def is_actually_sandwich(sandwich_txs):
    tx0, tx1 = sandwich_txs
    swap0, swap1 = tx0["swaps"][0], tx1["swaps"][0]

    tx0Coin0In = float(swap0["amount0In"])
    tx0Coin1In = float(swap0["amount1In"])
    tx0Coin0Out = float(swap0["amount0Out"])
    tx0Coin1Out = float(swap0["amount1Out"])

    tx1Coin0In = float(swap1["amount0In"])
    tx1Coin1In = float(swap1["amount1In"])
    tx1Coin0Out = float(swap1["amount0Out"])
    tx1Coin1Out = float(swap1["amount1Out"])

    return (tx0Coin0Out == tx1Coin0In) and (tx0Coin1Out == tx1Coin1In)

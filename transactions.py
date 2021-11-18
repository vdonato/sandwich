import json

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"

TXS_QUERY = """
query getTransactions ($block_number: Int) {
  transactions(block: {number: $block_number}, orderBy:blockNumber, orderDirection:desc) {
    id,
    blockNumber,
    swaps {
      id,
      pair {
        id,
        token0 {
          symbol
        },
        token1 {
          symbol
        }
      },
      to,
      amount0In,
      amount0Out,
      amount1In,
      amount1Out,
    }
  }
}
"""

transport = AIOHTTPTransport(url=SUBGRAPH_URL)
client = Client(transport=transport, fetch_schema_from_transport=True)


def fetch_txs_in_block(block_number):
    variable_values = {"block_number": block_number}
    query = gql(TXS_QUERY)
    result = client.execute(query, variable_values=variable_values)

    txs = result["transactions"]

    # For whatever reason, the Uniswap Subgraph doesn't allow exact matches
    # on block height??? So I guess we have to manually filter out everything
    # older than the requested block.
    filtered_txs = []
    for tx in txs:
        if int(tx["blockNumber"]) != block_number:
            break
        filtered_txs.append(tx)

    return filtered_txs


if __name__ == "__main__":
    STARTING_BLOCK = 13588033  # Some random block mined on Nov 10, 2021
    ENDING_BLOCK = 13637842  # The most recent block when this comment was written
    BLOCKS_TO_PROCESS = ENDING_BLOCK - STARTING_BLOCK

    OUTPUT_FILE = "transaction_data.txt"

    # Clear out any data that may be in the file.
    with open(OUTPUT_FILE, "w") as fp:
        pass

    for block_number in range(STARTING_BLOCK, ENDING_BLOCK):
        print(f"Collecting data for block {block_number}.")

        try:
            txs = fetch_txs_in_block(block_number)
            with open(OUTPUT_FILE, "a") as fp:
                fp.write(json.dumps(txs))
                fp.write("\n")

            print(f"Successfully collected {len(txs)} transactions in {block_number}.")
        except TransportQueryError:
            print(f"Hit error attempting to fetch txs for block: {block_number}.")

        blocks_processed = block_number - STARTING_BLOCK + 1
        progress_pct = blocks_processed / BLOCKS_TO_PROCESS * 100
        formatter = "{0:.2f}"
        print(f"Blocks processed: {blocks_processed}")
        print(f"Progress: {formatter.format(progress_pct)}%")
        print("")

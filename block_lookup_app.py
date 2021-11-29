import streamlit as st

import transactions
import utils
from sandwiches import find_sandwiches_in_txs

"## By block"
block_number = st.number_input("Input block number", value=0)

if block_number != 0:
    txs_in_block = transactions.fetch_txs_in_block(block_number)
    sandwiches_in_block = find_sandwiches_in_txs(txs_in_block)
    tx_df = utils.txs_to_df(txs_in_block, sandwiches_in_block)
    st.dataframe(tx_df)

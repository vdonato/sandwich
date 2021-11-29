import streamlit as st

import utils

"## 🥪 attack data by coin"
coin = st.selectbox("Pick a coin", utils.profits_by_coin().index)

f"### Profit vs time (block number) in {coin}"
st.line_chart(utils.cumprofit_for_coin(coin))

f"### Most lucrative 🥪 attacks on {coin}"
st.dataframe(utils.most_lucrative_sandwiches(coin))

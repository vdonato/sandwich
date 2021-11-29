import streamlit as st

import utils


"## 🥪 attack profit summary"

"### Profits by coin"
st.dataframe(utils.profits_by_coin())

"### Most attacked pairs"
st.dataframe(utils.num_attacks_by_pair())

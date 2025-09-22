import streamlit as st
import pandas as pd
import numpy as np


# entry=st.text_input("Name: ", key="Name")

# x = st.button("Submit Name")  # 👈 this is a widget 

# st.write(st.session_state.Name)



df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['second column'])

'You selected: ', option
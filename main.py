import streamlit as st
from loadexcel import browseexcel
from plot import showdata

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
 


 
# Main content
if st.session_state.page == 'home':
    browseexcel()
   
   
elif st.session_state.page == 'Plot':
    
    showdata()
    #st.write(st.session_state["GPC"])
    
   
elif st.session_state.page == 'contact':
    st.title("Contact Page")
    st.write("Get in touch with us on this page.")
   
    
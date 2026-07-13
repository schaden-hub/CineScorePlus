import streamlit as st

st.title("CineScore+ Ver 2")

option = st.sidebar.selectbox(
    "Choose an action:",
    ["Search", "Review", "Filter by Genre", "View Movieboard"]
)

if option == "Search":
    st.header("Search for a Movie")
    title = st.text_input("Enter a movie title")
    year = st.text_input("Enter a release year (optional)")
    if st.button("Search"):
        st.write("Search results displayed here.")

elif option == "Review":
    st.header("Review a movie.")
    st.write("Review interface WIP")

elif option == "Filter by Genre":
    st.header("Filter by Genre")
    st.write("Genre filter interfaec WIP.")

elif option == "View Movieboard":
    st.header("Movieboard")
    st.write("Movieboard display in progress.")



import streamlit as st
import os
import spacy
import tl_calamancy_lg

# Get the absolute path of the script directory
cwd = os.getcwd()

# Read the CSV file
csv_path = os.path.join(cwd, "dataset_v2.json")


def main():

    st.title("TagaCare")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize chat history
    if "nlp" not in st.session_state:
        st.session_state.nlp = tl_calamancy_lg.load() 
        st.write(st.session_state.nlp("rhandy").vector)


    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Display card data when button is clicked
    if chat_input := st.chat_input("Find Card"):

        # Display user message in chat message container
        st.chat_message("user").markdown(f"You: {chat_input}")

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": f"You: {chat_input}"})

        responses = ["^_^"]

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            for response in responses:
                print(response)
                st.markdown(f"{response}")

        # Add assistant response to chat history
        for response in responses:
            st.session_state.messages.append({"role": "assistant", "content": f"{response}"})


if __name__ == "__main__":
    main()

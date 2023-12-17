import streamlit as st
import tl_calamancy_lg
import os
import pandas as pd
import json
from sklearn.metrics.pairwise import cosine_similarity

# Define the cache decorator for loading the spaCy model
@st.cache_resource()
def load_nlp_model():
    return tl_calamancy_lg.load()

# Load the spaCy model using the cached function
nlp = load_nlp_model()


def remove_stop_words_spacy(text):
    doc = nlp(text)
    filtered_words = [token.text for token in doc if not token.is_stop]
    
    # Remove symbols using regular expressions
    clean_text = ' '.join(filtered_words)
    clean_text = re.sub(r'[^\w\s]', '', clean_text)

    return clean_text

# Example usage:
#text = "Anong itlog ang tumatae sa bubong ng bah?ay ni aling sumisipa?! Anong gamot sa pagtatae?"
#result = remove_stop_words_spacy(text)



# Define the cache decorator for loading the DataFrame
@st.cache_data
def load_data(file_path):
    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the JSON data
        data = json.load(file)

    # Extract patterns and responses into separate lists
    patterns_data = []
    responses_data = []

    for intent in data["intents"]:
        tag = intent["tag"]
        patterns = intent.get("patterns", [])
        responses = intent.get("responses", [])

        for pattern in patterns:
            patterns_data.append({"tag": tag, "pattern": pattern})

        for response in responses:
            responses_data.append({"tag": tag, "response": response})

    # Create and return DataFrames
    patterns_df = pd.DataFrame(patterns_data)
    responses_df = pd.DataFrame(responses_data)
    return patterns_df, responses_df

# Get the absolute path of the script directory
cwd = os.getcwd()

# Read the CSV file
file_path = os.path.join(cwd, "dataset_v3.json")

# Load the DataFrames using the cached function
patterns_df, responses_df = load_data(file_path)

# Define the cache decorator for the similarity function
@st.cache_data
def get_most_similar_tag(user_query, dataframe):

    # Process user query and existing queries with spaCy
    all_queries = list(dataframe['pattern']) + [remove_stop_words_spacy(user_query)]
    processed_queries = [nlp(remove_stop_words_spacy(query)) for query in all_queries]

    # Assuming processed_queries is a list of Doc objects
    vectors = [query.vector for query in processed_queries]

    # Calculate cosine similarity
    similarity_matrix = [[query1.similarity(query2) for query2 in processed_queries] for query1 in processed_queries]

    # Extract similarity scores for the user # Extract similarity scores for the user query
    user_similarity_scores = similarity_matrix[-1][:-1]

    # Find the index of the tag with the highest similarity score
    most_similar_index = user_similarity_scores.index(max(user_similarity_scores))

    # Get the most similar tag
    most_similar_tag = dataframe['tag'].iloc[most_similar_index]

    print(dataframe['pattern'].iloc[most_similar_index])

    # Return the most similar tag and its similarity score
    return most_similar_tag, user_similarity_scores[most_similar_index]


def main():
    # StreamLit Title
    st.title("🏥 TagaCare: Healthcare Tagalog Chatbot 🤖")
    st.write("Enhancing Healthcare Accessibility through Tagalog Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    #st.write(result)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Magtanong ng lunas sa sakit: (e.g. Anong gamot sa sakit ng ulo)"):

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Use the cached function to get the most similar tag
        returned_tag, returned_score = get_most_similar_tag(prompt, patterns_df)

        if (returned_score >= 0.6):
            response = responses_df[responses_df['tag']==returned_tag].iloc[0]['response']
            
            st.success("Sakit: "+returned_tag)
            st.success(response)
    
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": f"{response}"})

        else:        
            response = "Pasensya kaibigan, wala sa aking talaan ng mga kaalaman ang iyong katanungan" 
            
            st.error(response)
            
            st.session_state.messages.append({"role": "assistant", "content": f"{response}"})
        
if __name__ == "__main__":
    main()

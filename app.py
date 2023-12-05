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
    all_queries = list(dataframe['pattern']) + [user_query]
    processed_queries = [nlp(query) for query in all_queries]

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
    # st.write(patterns_df)
    # st.write(responses_df)

    # React to user input
    if prompt := st.chat_input("Magtanong ng lunas sa sakit"):

        # Use the cached function to get the most similar tag
        returned_tag, returned_score = get_most_similar_tag(prompt, patterns_df)

        # Use the cached function to get the most similar tag
        returned_tag, returned_score = get_most_similar_tag(prompt, patterns_df)

        if (returned_score >= 0.5)
            st.success(returned_tag)
            st.success(responses_df[responses_df['tag']==returned_tag].iloc[0]['response'])
        else:        
            st.error("Pasensya kaibigan, wala sa aking talaan ng mga kaalaman ang iyong katanungan")
        
if __name__ == "__main__":
    main()

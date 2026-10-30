import json
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
from sqldb import execute_query, get_schema

# Load environment variables
load_dotenv()

# Initialize Gemini Client
@st.cache_resource
def get_client():
    return genai.Client()

client = get_client()

# Define the expected JSON structure
class QueryResult(BaseModel):
    sql: str
    question: str

# Streamlit UI Setup
st.set_page_config(page_title="Talk to Your Data", page_icon="🤖", layout="wide")
st.title("🤖 Talk to Your Data")
st.markdown("Ask a question in plain English, and the app will generate the T-SQL query and fetch the results from your database.")

# User Input
user_input = st.text_input("Enter your question about the orders:")

if st.button("Run Query"):
    if user_input:
        with st.spinner("Generating SQL and fetching results..."):
            try:
                # 1. Get schema
                schema = get_schema("orders")

                # 2. Build prompt
                prompt = f"""write the (SSMS / T-SQL) query based on question below:
                {user_input}
                use below orders table schema
                {schema}
                """

                # 3. Configure Gemini
                config = types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=QueryResult,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )

                # 4. Generate Content
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config=config
                )

                # 5. Parse response
                json_response = json.loads(response.text)
                final_sql = json_response['sql']

               # 5. Parse response
                json_response = json.loads(response.text)
                final_sql = json_response['sql']

                # 6. Execute query
                final_result = execute_query(final_sql)
                
                # 7. Display results as a user-friendly table
                if final_result:
                    # Unpack the tuple: (columns, data_rows) based on your execute_query output structure
                    columns, data = final_result
                    
                    # Convert to pandas DataFrame for a clean table UI
                    df = pd.DataFrame(data, columns=columns)
                    
                    st.subheader("Query Results")
                    st.dataframe(df, use_container_width=False) 
                else:
                    st.info("Query executed successfully, but returned no data.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question first.")
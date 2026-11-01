import json
import streamlit as st
import pandas as pd
import os  # <-- This is the missing line
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
from sqldb import execute_query, get_schema

# Load environment variables
load_dotenv()

# Fetch login credentials from .env or Streamlit Secrets
EXPECTED_USER = os.getenv("APP_USERNAME")
EXPECTED_PASS = os.getenv("APP_PASSWORD")

# Initialize session state to track if the user is logged in
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Display the Login Window if not authenticated
if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    
    # Create the login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username == EXPECTED_USER and password == EXPECTED_PASS:
                st.session_state.authenticated = True
                st.rerun() # Refresh the page to hide the login and show the app
            else:
                st.error("Invalid username or password.")
                
    # st.stop() prevents the rest of your code from running until authenticated
    st.stop()

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
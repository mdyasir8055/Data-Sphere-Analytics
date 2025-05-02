import streamlit as st
import os
import requests
import json
import re
import pandas as pd
import google.generativeai as genai
from groq import Groq

class NLPProcessor:
    def __init__(self):
        # Initialize session state for API keys if not already set
        if "groq_api_key" not in st.session_state:
            st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
        if "gemini_api_key" not in st.session_state:
            st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Initialize Groq client if API key is available
        self.groq_client = None
        self.gemini_model = None
        self._update_clients()
        
        # Initialize session state variables
        if "current_query" not in st.session_state:
            st.session_state.current_query = ""
        
        if "natural_language_query" not in st.session_state:
            st.session_state.natural_language_query = ""
            
        # Initialize chat history for follow-up questions
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Initialize database Q&A history
        if "db_qa_history" not in st.session_state:
            st.session_state.db_qa_history = []
            
        # Initialize active conversation flag
        if "active_conversation" not in st.session_state:
            st.session_state.active_conversation = False
    
    def _update_clients(self):
        """Update API clients based on current session state API keys"""
        # Update Groq client
        if st.session_state.groq_api_key:
            self.groq_client = Groq(api_key=st.session_state.groq_api_key)
        else:
            self.groq_client = None
            
        # Update Gemini client
        if st.session_state.gemini_api_key:
            genai.configure(api_key=st.session_state.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
    
    def text_to_sql_ui(self, db_manager):
        """UI for converting natural language to SQL with follow-up chat"""
        st.subheader("Convert Natural Language to SQL")
        
        # Create tabs for different query modes
        query_tab, chat_tab, db_qa_tab = st.tabs(["Query Generator", "Follow-up Chat", "Database Q&A"])
        
        with query_tab:
            # Select LLM model
            model_provider = st.selectbox(
                "Select AI Model Provider", 
                options=["Groq", "Gemini"],
                key="model_provider"
            )
            
            # API Key Configuration
            with st.expander("API Key Configuration", expanded=not (st.session_state.groq_api_key or st.session_state.gemini_api_key)):
                st.info("You need to provide API keys to use the text-to-SQL feature. These keys are stored only in your current session.")
                
                # Groq API Key
                groq_api_key = st.text_input(
                    "Groq API Key", 
                    value=st.session_state.groq_api_key,
                    type="password",
                    help="Get your Groq API key from https://console.groq.com/keys",
                    key="groq_api_input"
                )
                
                # Gemini API Key
                gemini_api_key = st.text_input(
                    "Gemini API Key", 
                    value=st.session_state.gemini_api_key,
                    type="password",
                    help="Get your Gemini API key from https://ai.google.dev/",
                    key="gemini_api_input"
                )
                
                # Update API keys in session state
                if groq_api_key != st.session_state.groq_api_key:
                    st.session_state.groq_api_key = groq_api_key
                    self._update_clients()
                    
                if gemini_api_key != st.session_state.gemini_api_key:
                    st.session_state.gemini_api_key = gemini_api_key
                    self._update_clients()
            
            # Show API status
            if model_provider == "Groq":
                if not st.session_state.groq_api_key:
                    st.warning("Groq API key is not configured. Please enter your API key in the configuration section.")
            elif model_provider == "Gemini":
                if not st.session_state.gemini_api_key:
                    st.warning("Gemini API key is not configured. Please enter your API key in the configuration section.")
            
            # Natural language input
            nl_query = st.text_area(
                "Enter your question in natural language",
                value=st.session_state.natural_language_query,
                height=100,
                key="nl_query_input"
            )
            
            # Context information
            st.info("Providing context about your database structure helps generate better queries.")
            
            # Display database schema information if available
            if st.session_state.db_schema:
                schema_info = self._format_schema_info(st.session_state.db_schema)
                with st.expander("Database Schema Information (Used for Context)", expanded=False):
                    st.text_area("Schema", value=schema_info, height=150, key="schema_display", disabled=True)
            else:
                schema_info = ""
                st.warning("No database schema information available. Connect to a database to see schema details.")
            
            # Generate SQL button
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                generate_button = st.button("Generate SQL", key="generate_sql_btn")
            
            with col2:
                # Add a button to start a conversation for follow-ups
                if st.button("Start Conversation", key="start_conversation_btn"):
                    if not nl_query:
                        st.warning("Please enter a question first.")
                    else:
                        st.session_state.active_conversation = True
                        st.session_state.chat_history = []
                        st.rerun()
            
            # Update session state for nl_query
            if nl_query != st.session_state.natural_language_query:
                st.session_state.natural_language_query = nl_query
            
            # Process when generate button is clicked
            if generate_button and nl_query:
                # Check if API key is configured for selected model
                if model_provider == "Groq" and not st.session_state.groq_api_key:
                    st.error("Groq API key is not configured. Please enter your API key in the configuration section.")
                    return
                
                if model_provider == "Gemini" and not st.session_state.gemini_api_key:
                    st.error("Gemini API key is not configured. Please enter your API key in the configuration section.")
                    return
                    
                with st.spinner("Generating SQL query..."):
                    try:
                        sql_query = None
                        if model_provider == "Groq":
                            sql_query = self._generate_sql_groq(nl_query, schema_info)
                        elif model_provider == "Gemini":
                            sql_query = self._generate_sql_gemini(nl_query, schema_info)
                        
                        if sql_query:
                            st.session_state.current_query = sql_query
                            
                            # Add to chat history if in conversation mode
                            if st.session_state.active_conversation:
                                st.session_state.chat_history.append({
                                    "role": "user",
                                    "content": nl_query
                                })
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": f"I've generated this SQL query based on your question:\n\n```sql\n{sql_query}\n```"
                                })
                            
                            st.success("SQL query generated successfully!")
                        else:
                            st.error("Failed to generate SQL query. Please try rephrasing your question.")
                    except Exception as e:
                        st.error(f"Error generating SQL query: {str(e)}")
        
        with chat_tab:
            self._follow_up_chat_ui(db_manager)
            
        with db_qa_tab:
            self._database_qa_ui(db_manager)
        
        # Display the generated SQL query
        if st.session_state.current_query:
            st.subheader("Generated SQL Query")
            st.code(st.session_state.current_query, language="sql")
            
            # Execute query button
            if st.button("Execute Query", key="execute_nl_query_btn"):
                with st.spinner("Executing query..."):
                    result = db_manager.execute_query(st.session_state.current_query)
                    if isinstance(result, pd.DataFrame):
                        st.success(f"Query executed successfully! {len(result)} rows returned.")
                    else:
                        st.success("Query executed successfully!")
                    
                    # Switch to Query Results tab
                    st.session_state["query_tab"] = "Query Results"
                    st.rerun()
    
    def sql_editor_ui(self, db_manager):
        """UI for SQL editor"""
        st.subheader("SQL Query Editor")
        
        # Query name and description (for saving to workspace)
        col1, col2 = st.columns(2)
        with col1:
            query_name = st.text_input(
                "Query Name",
                value=st.session_state.get("query_name", ""),
                key="query_name_input",
                placeholder="Enter a name for this query"
            )
        
        with col2:
            query_description = st.text_input(
                "Description",
                value=st.session_state.get("query_description", ""),
                key="query_description_input",
                placeholder="Optional description"
            )
        
        # SQL query editor
        sql_query = st.text_area(
            "Enter SQL Query",
            value=st.session_state.current_query,
            height=150,
            key="sql_editor"
        )
        
        # Update session state for current_query
        if sql_query != st.session_state.current_query:
            st.session_state.current_query = sql_query
        
        # Store query name and description in session state
        st.session_state.query_name = query_name
        st.session_state.query_description = query_description
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Execute query button
            if st.button("Execute Query", key="execute_sql_btn"):
                if not sql_query:
                    st.warning("Please enter a SQL query.")
                    return
                
                with st.spinner("Executing query..."):
                    result = db_manager.execute_query(sql_query)
                    if isinstance(result, pd.DataFrame):
                        st.success(f"Query executed successfully! {len(result)} rows returned.")
                    else:
                        st.success("Query executed successfully!")
        
        with col2:
            # Save to workspace button
            if st.button("Save to Workspace", key="save_to_workspace_btn"):
                if not sql_query:
                    st.warning("Please enter a SQL query.")
                    return
                
                if not query_name:
                    st.warning("Please enter a name for this query.")
                    return
                
                # Check if user is logged in
                current_user = None
                if "user_management" in st.session_state:
                    current_user = st.session_state.user_management.get_current_user()
                
                if not current_user:
                    st.warning("Please log in to save queries to workspaces.")
                    return
                
                # Check if collaboration module is available
                if "collaboration" in st.session_state:
                    # Generate a unique ID for the query
                    import uuid
                    query_id = str(uuid.uuid4())
                    
                    # Create query data
                    query_data = {
                        "name": query_name,
                        "description": query_description,
                        "sql": sql_query,
                        "created_by": current_user,
                        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "modified_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "database": st.session_state.get("connected_db", "Unknown")
                    }
                    
                    # Add to workspace
                    if st.session_state.collaboration.add_to_workspace("query", query_id, query_data):
                        st.success(f"Query '{query_name}' saved to workspace '{st.session_state.current_workspace}'.")
                    else:
                        st.error("Failed to save query to workspace.")
                else:
                    st.error("Collaboration module not available.")
        
        with col3:
            # Clear button
            if st.button("Clear Editor", key="clear_sql_btn"):
                st.session_state.current_query = ""
                st.session_state.query_name = ""
                st.session_state.query_description = ""
                st.rerun()
    
    def _generate_sql_groq(self, nl_query, schema_info):
        """Generate SQL query using Groq API"""
        if not self.groq_client:
            st.error("Groq API key is not configured. Please enter your API key in the configuration section.")
            return None
        
        prompt = self._create_prompt(nl_query, schema_info)
        
        try:
            # Use Groq API to generate SQL
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful SQL expert. Your task is to convert natural language questions into correct SQL queries based on the database schema provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024
            )
            
            # Extract the SQL query from the response
            sql = self._extract_sql_from_response(response.choices[0].message.content)
            return sql
        except Exception as e:
            st.error(f"Error calling Groq API: {str(e)}")
            return None
    
    def _generate_sql_gemini(self, nl_query, schema_info):
        """Generate SQL query using Gemini API"""
        if not self.gemini_model:
            st.error("Gemini API key is not configured. Please enter your API key in the configuration section.")
            return None
        
        prompt = self._create_prompt(nl_query, schema_info)
        
        try:
            # Use Gemini API to generate SQL
            response = self.gemini_model.generate_content(prompt)
            
            # Extract the SQL query from the response
            sql = self._extract_sql_from_response(response.text)
            return sql
        except Exception as e:
            st.error(f"Error calling Gemini API: {str(e)}")
            return None
    
    def _create_prompt(self, nl_query, schema_info):
        """Create a prompt for the language model"""
        # Check if we're connected to SQLite
        is_sqlite = False
        if st.session_state.current_connection and st.session_state.current_connection["type"] == "SQLite":
            is_sqlite = True
            
        # Define SQLite-specific instructions outside of f-strings to avoid backslash issues
        sqlite_intro = "IMPORTANT: This is a SQLite database. Do not use INFORMATION_SCHEMA.TABLES in your query. Instead, use sqlite_master table to query metadata."
        sqlite_tables_query = "- Instead of INFORMATION_SCHEMA.TABLES, use 'SELECT * FROM sqlite_master WHERE type=\"table\"'"
        sqlite_columns_query = "- To get column information, use 'PRAGMA table_info(table_name)'"
        sqlite_count_query = "- To count tables, use 'SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"'"
        sqlite_section_header = "For SQLite metadata queries:"
            
        if schema_info:
            prompt = f"""
            Database Schema:
            {schema_info}
            
            Natural Language Query: {nl_query}
            
            {sqlite_intro if is_sqlite else ""}
            
            Generate a SQL query that answers this question based on the database schema provided.
            Return only the SQL query without any explanations or markdown formatting.
            """
            
            # Add SQLite-specific instructions if needed
            if is_sqlite:
                prompt += f"""
                
                {sqlite_section_header}
                {sqlite_tables_query}
                {sqlite_columns_query}
                {sqlite_count_query}
                """
        else:
            prompt = f"""
            Natural Language Query: {nl_query}
            
            {sqlite_intro if is_sqlite else ""}
            
            Generate a SQL query that answers this question.
            Return only the SQL query without any explanations or markdown formatting.
            """
            
            # Add SQLite-specific instructions if needed
            if is_sqlite:
                prompt += f"""
                
                {sqlite_section_header}
                {sqlite_tables_query}
                {sqlite_columns_query}
                {sqlite_count_query}
                """
        
        return prompt
    
    def _extract_sql_from_response(self, response_text):
        """Extract SQL query from model response"""
        # Try to extract SQL from code blocks (markdown format)
        sql_pattern = r"```sql(.*?)```"
        match = re.search(sql_pattern, response_text, re.DOTALL)
        
        if match:
            # Extract SQL from code block
            return match.group(1).strip()
        else:
            # If no code block found, try to extract what looks like a SQL query
            # This is a simple heuristic and may need improvement
            lines = response_text.strip().split('\n')
            sql_lines = []
            
            # Filter lines that look like SQL (starting with SELECT, INSERT, UPDATE, etc.)
            sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "WITH"]
            
            in_sql = False
            for line in lines:
                line = line.strip()
                
                # Check if line starts with SQL keyword
                if any(line.upper().startswith(keyword) for keyword in sql_keywords):
                    in_sql = True
                    sql_lines.append(line)
                elif in_sql and line:
                    sql_lines.append(line)
            
            if sql_lines:
                return '\n'.join(sql_lines)
            else:
                # If no clear SQL structure found, return the whole response
                # but clean it up a bit
                return response_text.replace("```", "").strip()
    
    def _format_schema_info(self, schema):
        """Format database schema for the prompt"""
        formatted_text = []
        
        if "tables" in schema:
            # SQL-based databases
            formatted_text.append("Tables:")
            for table_name, table_info in schema["tables"].items():
                formatted_text.append(f"  Table: {table_name}")
                formatted_text.append("    Columns:")
                
                for column in table_info["columns"]:
                    col_name = column["name"]
                    col_type = column["type"]
                    
                    # Indicate primary key
                    if col_name in table_info["primary_keys"]:
                        formatted_text.append(f"      {col_name} ({col_type}) - Primary Key")
                    else:
                        formatted_text.append(f"      {col_name} ({col_type})")
                
                # Foreign keys
                if table_info["foreign_keys"]:
                    formatted_text.append("    Foreign Keys:")
                    for fk in table_info["foreign_keys"]:
                        formatted_text.append(f"      {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
        
        elif "collections" in schema:
            # MongoDB
            formatted_text.append("Collections:")
            for collection_name, collection_info in schema["collections"].items():
                formatted_text.append(f"  Collection: {collection_name}")
                
                if collection_info["fields"]:
                    formatted_text.append("    Fields:")
                    for field in collection_info["fields"]:
                        formatted_text.append(f"      {field['name']} ({field['type']})")
        
        return "\n".join(formatted_text)
        
    def _follow_up_chat_ui(self, db_manager):
        """UI for follow-up chat about SQL queries"""
        st.subheader("Follow-up Chat")
        
        # Check if API keys are configured
        if not st.session_state.groq_api_key and not st.session_state.gemini_api_key:
            st.warning("Please configure at least one API key in the Query Generator tab to use the follow-up chat feature.")
            return
            
        # Display chat history
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #1e1e1e; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            if st.session_state.active_conversation:
                st.info("Your conversation has started. Ask a follow-up question below.")
            else:
                st.info("Start a conversation in the Query Generator tab by entering a question and clicking 'Start Conversation'.")
                return
                
        # Input for follow-up questions
        follow_up = st.text_area(
            "Ask a follow-up question",
            key="follow_up_input",
            height=100,
            placeholder="Example: 'Can you modify that query to also include...?' or 'What if I want to filter by...?'"
        )
        
        # Get schema info
        if st.session_state.db_schema:
            schema_info = self._format_schema_info(st.session_state.db_schema)
        else:
            schema_info = ""
            
        # Send button
        if st.button("Send", key="send_follow_up_btn") and follow_up:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": follow_up
            })
            
            # Determine which model to use
            model_provider = st.session_state.get("model_provider", "Groq" if st.session_state.groq_api_key else "Gemini")
            
            with st.spinner("Generating response..."):
                try:
                    # Construct the conversation history for context
                    conversation_history = "\n\n".join([
                        f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                        for msg in st.session_state.chat_history[:-1]  # Exclude the latest user message
                    ])
                    
                    # Generate response
                    if model_provider == "Groq" and st.session_state.groq_api_key:
                        response = self._generate_follow_up_response_groq(follow_up, conversation_history, schema_info)
                    elif model_provider == "Gemini" and st.session_state.gemini_api_key:
                        response = self._generate_follow_up_response_gemini(follow_up, conversation_history, schema_info)
                    else:
                        st.error("No API key configured for the selected model.")
                        return
                    
                    if response:
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        # Check if response contains SQL query and update current_query
                        sql_match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
                        if sql_match:
                            sql_query = sql_match.group(1).strip()
                            st.session_state.current_query = sql_query
                    else:
                        st.error("Failed to generate a response. Please try again.")
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
            
            # Rerun to update the UI
            st.rerun()
            
        # End conversation button
        if st.session_state.active_conversation and st.button("End Conversation", key="end_conversation_btn"):
            st.session_state.active_conversation = False
            st.success("Conversation ended. You can start a new one from the Query Generator tab.")
            st.rerun()
            
    def _database_qa_ui(self, db_manager):
        """UI for natural language Q&A about the database"""
        st.subheader("Database Q&A")
        
        # Check if API keys are configured
        if not st.session_state.groq_api_key and not st.session_state.gemini_api_key:
            st.warning("Please configure at least one API key in the Query Generator tab to use the Database Q&A feature.")
            return
            
        # Check if connected to a database
        if not st.session_state.db_schema:
            st.warning("Please connect to a database first to use this feature.")
            return
            
        # Display previous Q&A
        if st.session_state.db_qa_history:
            for qa in st.session_state.db_qa_history:
                st.markdown(f"""
                <div style="background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Question:</strong> {qa["question"]}
                </div>
                <div style="background-color: #1e1e1e; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                    <strong>Answer:</strong> {qa["answer"]}
                </div>
                """, unsafe_allow_html=True)
                
        # Input for database questions
        db_question = st.text_area(
            "Ask a question about your database",
            key="db_question_input",
            height=100,
            placeholder="Example: 'What tables are in my database?' or 'What columns are in the customers table?'"
        )
        
        # Get schema info
        schema_info = self._format_schema_info(st.session_state.db_schema)
        
        # Ask button
        if st.button("Ask", key="ask_db_question_btn") and db_question:
            # Determine which model to use
            model_provider = st.session_state.get("model_provider", "Groq" if st.session_state.groq_api_key else "Gemini")
            
            with st.spinner("Generating answer..."):
                try:
                    # Generate answer
                    if model_provider == "Groq" and st.session_state.groq_api_key:
                        answer = self._generate_db_answer_groq(db_question, schema_info)
                    elif model_provider == "Gemini" and st.session_state.gemini_api_key:
                        answer = self._generate_db_answer_gemini(db_question, schema_info)
                    else:
                        st.error("No API key configured for the selected model.")
                        return
                    
                    if answer:
                        # Add to Q&A history
                        st.session_state.db_qa_history.append({
                            "question": db_question,
                            "answer": answer
                        })
                    else:
                        st.error("Failed to generate an answer. Please try again.")
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
            
            # Rerun to update the UI
            st.rerun()
            
        # Clear history button
        if st.session_state.db_qa_history and st.button("Clear History", key="clear_db_qa_history_btn"):
            st.session_state.db_qa_history = []
            st.success("Q&A history cleared.")
            st.rerun()
            
    def _generate_follow_up_response_groq(self, follow_up, conversation_history, schema_info):
        """Generate a response to a follow-up question using Groq API"""
        if not self.groq_client:
            return None
            
        # Construct the prompt
        prompt = f"""
        You are an expert SQL assistant helping with follow-up questions about SQL queries. You have access to the conversation history and database schema.
        
        Database Schema Information:
        {schema_info}
        
        Conversation History:
        {conversation_history}
        
        User's Follow-up Question:
        {follow_up}
        
        Please respond to the follow-up question. If the user is asking for a modified SQL query, provide the complete SQL query in a code block using markdown formatting (```sql ... ```). Also provide a brief explanation of what you changed and why.
        
        If the user is asking for clarification about the existing query, explain the relevant parts clearly.
        """
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert SQL assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            response = completion.choices[0].message.content.strip()
            return response
        except Exception as e:
            st.error(f"Error with Groq API: {str(e)}")
            return None
            
    def _generate_follow_up_response_gemini(self, follow_up, conversation_history, schema_info):
        """Generate a response to a follow-up question using Gemini API"""
        if not self.gemini_model:
            return None
            
        # Construct the prompt
        prompt = f"""
        You are an expert SQL assistant helping with follow-up questions about SQL queries. You have access to the conversation history and database schema.
        
        Database Schema Information:
        {schema_info}
        
        Conversation History:
        {conversation_history}
        
        User's Follow-up Question:
        {follow_up}
        
        Please respond to the follow-up question. If the user is asking for a modified SQL query, provide the complete SQL query in a code block using markdown formatting (```sql ... ```). Also provide a brief explanation of what you changed and why.
        
        If the user is asking for clarification about the existing query, explain the relevant parts clearly.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error with Gemini API: {str(e)}")
            return None
            
    def _generate_db_answer_groq(self, question, schema_info):
        """Generate an answer to a database question using Groq API"""
        if not self.groq_client:
            return None
            
        # Construct the prompt
        prompt = f"""
        You are an expert database assistant. Your task is to answer questions about a database based on its schema.
        
        Database Schema Information:
        {schema_info}
        
        User's Question:
        {question}
        
        Please provide a clear, concise answer to the question. Focus on explaining database concepts in simple terms.
        Do not generate SQL queries unless specifically asked. Instead, explain the database structure, relationships, and concepts in plain English.
        """
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert database assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            response = completion.choices[0].message.content.strip()
            return response
        except Exception as e:
            st.error(f"Error with Groq API: {str(e)}")
            return None
            
    def _generate_db_answer_gemini(self, question, schema_info):
        """Generate an answer to a database question using Gemini API"""
        if not self.gemini_model:
            return None
            
        # Construct the prompt
        prompt = f"""
        You are an expert database assistant. Your task is to answer questions about a database based on its schema.
        
        Database Schema Information:
        {schema_info}
        
        User's Question:
        {question}
        
        Please provide a clear, concise answer to the question. Focus on explaining database concepts in simple terms.
        Do not generate SQL queries unless specifically asked. Instead, explain the database structure, relationships, and concepts in plain English.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error with Gemini API: {str(e)}")
            return None

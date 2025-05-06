import streamlit as st
import pandas as pd
import requests
import json
import time
from bs4 import BeautifulSoup
import io
import re
from urllib.parse import urlparse

class ExternalDataSources:
    def __init__(self):
        # Initialize saved data sources
        if "external_data_sources" not in st.session_state:
            st.session_state.external_data_sources = []
        
        # Initialize current data
        if "current_external_data" not in st.session_state:
            st.session_state.current_external_data = None
            
        # Initialize data source name
        if "data_source_name" not in st.session_state:
            st.session_state.data_source_name = ""
    
    def external_data_ui(self, db_manager=None):
        """Main UI for external data sources integration"""
        
        tabs = st.tabs(["API Integration", "Web Scraping", "Saved Data Sources"])
        
        with tabs[0]:
            self.api_integration_ui(db_manager)
            
        with tabs[1]:
            self.web_scraping_ui(db_manager)
            
        with tabs[2]:
            self.saved_data_sources_ui(db_manager)
    
    def api_integration_ui(self, db_manager=None):
        """UI for API integration"""
        st.subheader("API Data Integration")
        
        # API configuration
        api_url = st.text_input("API URL", placeholder="https://api.example.com/data")
        
        # Method selection
        method = st.selectbox("Request Method", ["GET", "POST", "PUT", "DELETE"])
        
        # Headers
        st.subheader("Headers")
        col1, col2 = st.columns(2)
        headers = {}
        
        with st.expander("Add Headers"):
            header_key = st.text_input("Header Name", placeholder="Content-Type")
            header_value = st.text_input("Header Value", placeholder="application/json")
            if st.button("Add Header") and header_key and header_value:
                headers[header_key] = header_value
                st.success(f"Added header: {header_key}")
        
        # Display current headers
        if headers:
            st.json(headers)
        
        # Parameters/Body
        st.subheader("Parameters or Body")
        param_type = st.radio("Parameter Type", ["Query Parameters", "JSON Body", "Form Data"])
        
        params = {}
        json_body = {}
        form_data = {}
        
        if param_type == "Query Parameters":
            with st.expander("Add Query Parameter"):
                param_key = st.text_input("Parameter Name", placeholder="page")
                param_value = st.text_input("Parameter Value", placeholder="1")
                if st.button("Add Parameter") and param_key and param_value:
                    params[param_key] = param_value
                    st.success(f"Added parameter: {param_key}")
            
            if params:
                st.json(params)
                
        elif param_type == "JSON Body":
            json_str = st.text_area("JSON Body", placeholder='{\n  "key": "value"\n}')
            if json_str:
                try:
                    json_body = json.loads(json_str)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
        
        elif param_type == "Form Data":
            with st.expander("Add Form Field"):
                form_key = st.text_input("Field Name", placeholder="username")
                form_value = st.text_input("Field Value", placeholder="user123")
                if st.button("Add Field") and form_key and form_value:
                    form_data[form_key] = form_value
                    st.success(f"Added field: {form_key}")
            
            if form_data:
                st.json(form_data)
        
        # Authentication
        st.subheader("Authentication (Optional)")
        auth_type = st.selectbox("Authentication Type", ["None", "Basic Auth", "Bearer Token", "API Key"])
        
        auth = None
        if auth_type == "Basic Auth":
            auth_user = st.text_input("Username")
            auth_pass = st.text_input("Password", type="password")
            if auth_user and auth_pass:
                auth = (auth_user, auth_pass)
        
        elif auth_type == "Bearer Token":
            token = st.text_input("Bearer Token", type="password")
            if token:
                if "Authorization" not in headers:
                    headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == "API Key":
            key_name = st.text_input("API Key Name", placeholder="X-API-Key")
            key_value = st.text_input("API Key Value", type="password")
            key_location = st.radio("Key Location", ["Header", "Query Parameter"])
            
            if key_name and key_value:
                if key_location == "Header":
                    headers[key_name] = key_value
                else:
                    params[key_name] = key_value
        
        # Execute request
        if st.button("Fetch Data", type="primary"):
            if not api_url:
                st.error("API URL is required")
                return
            
            with st.spinner("Fetching data from API..."):
                try:
                    # Prepare request arguments
                    request_kwargs = {
                        "url": api_url,
                        "headers": headers if headers else None,
                    }
                    
                    if auth:
                        request_kwargs["auth"] = auth
                    
                    if param_type == "Query Parameters":
                        request_kwargs["params"] = params
                    elif param_type == "JSON Body":
                        request_kwargs["json"] = json_body
                    elif param_type == "Form Data":
                        request_kwargs["data"] = form_data
                    
                    # Make the request
                    response = requests.request(method, **request_kwargs)
                    
                    # Check if successful
                    response.raise_for_status()
                    
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        st.success(f"Successfully fetched data (Status code: {response.status_code})")
                        
                        # Try to convert to DataFrame if it's a list or simple object
                        try:
                            if isinstance(data, list):
                                df = pd.DataFrame(data)
                                st.session_state.current_external_data = df
                                st.dataframe(df)
                                
                                # Save data source name
                                source_name = st.text_input("Save this data source as:", 
                                                          placeholder="My API Data Source")
                                if st.button("Save Data Source") and source_name:
                                    self._save_data_source(source_name, "api", df, {
                                        "url": api_url,
                                        "method": method,
                                        "headers": headers,
                                        "params": params if param_type == "Query Parameters" else None,
                                        "json_body": json_body if param_type == "JSON Body" else None,
                                        "form_data": form_data if param_type == "Form Data" else None,
                                        "auth_type": auth_type
                                    })
                                
                                # Import to database option
                                if db_manager and db_manager.is_connected():
                                    st.subheader("Import to Database")
                                    table_name = st.text_input("Table name", 
                                                             placeholder="api_data")
                                    if st.button("Import to Database") and table_name:
                                        self._import_to_database(db_manager, df, table_name)
                            
                            elif isinstance(data, dict):
                                # Try to normalize the dictionary to a dataframe
                                try:
                                    df = pd.json_normalize(data)
                                    st.session_state.current_external_data = df
                                    st.dataframe(df)
                                    
                                    # Save data source name
                                    source_name = st.text_input("Save this data source as:", 
                                                              placeholder="My API Data Source")
                                    if st.button("Save Data Source") and source_name:
                                        self._save_data_source(source_name, "api", df, {
                                            "url": api_url,
                                            "method": method,
                                            "headers": headers,
                                            "params": params if param_type == "Query Parameters" else None,
                                            "json_body": json_body if param_type == "JSON Body" else None,
                                            "form_data": form_data if param_type == "Form Data" else None,
                                            "auth_type": auth_type
                                        })
                                    
                                    # Import to database option
                                    if db_manager and db_manager.is_connected():
                                        st.subheader("Import to Database")
                                        table_name = st.text_input("Table name", 
                                                                 placeholder="api_data")
                                        if st.button("Import to Database") and table_name:
                                            self._import_to_database(db_manager, df, table_name)
                                except:
                                    # Just show the raw JSON
                                    st.json(data)
                            else:
                                st.json(data)
                        except Exception as e:
                            st.error(f"Could not convert to DataFrame: {str(e)}")
                            st.json(data)
                    
                    except json.JSONDecodeError:
                        # Not JSON, show as text
                        st.text(response.text)
                
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching data: {str(e)}")
    
    def web_scraping_ui(self, db_manager=None):
        """UI for web scraping"""
        st.subheader("Web Scraping")
        
        # URL input
        url = st.text_input("Website URL", placeholder="https://example.com")
        
        # Scraping options
        scrape_type = st.radio("What to scrape", ["Tables", "Custom Elements"])
        
        if scrape_type == "Tables":
            if st.button("Scrape Tables", type="primary") and url:
                with st.spinner("Scraping tables from website..."):
                    try:
                        # Fetch the webpage
                        response = requests.get(url)
                        response.raise_for_status()
                        
                        # Parse HTML
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find all tables
                        tables = soup.find_all('table')
                        
                        if not tables:
                            st.warning("No tables found on this webpage")
                        else:
                            st.success(f"Found {len(tables)} tables")
                            
                            # Parse each table
                            dfs = pd.read_html(response.text)
                            
                            # Display each table with option to select
                            for i, df in enumerate(dfs):
                                with st.expander(f"Table {i+1} ({len(df)} rows x {len(df.columns)} columns)"):
                                    st.dataframe(df)
                                    
                                    if st.button(f"Select Table {i+1}", key=f"select_table_{i}"):
                                        st.session_state.current_external_data = df
                                        
                                        # Save data source name
                                        source_name = st.text_input("Save this data source as:", 
                                                                  placeholder=f"Table from {urlparse(url).netloc}",
                                                                  key=f"save_name_{i}")
                                        if st.button("Save Data Source", key=f"save_btn_{i}") and source_name:
                                            self._save_data_source(source_name, "web_table", df, {
                                                "url": url,
                                                "table_index": i
                                            })
                                        
                                        # Import to database option
                                        if db_manager and db_manager.is_connected():
                                            st.subheader("Import to Database")
                                            table_name = st.text_input("Table name", 
                                                                     placeholder="web_data",
                                                                     key=f"table_name_{i}")
                                            if st.button("Import to Database", key=f"import_btn_{i}") and table_name:
                                                self._import_to_database(db_manager, df, table_name)
                    
                    except Exception as e:
                        st.error(f"Error scraping website: {str(e)}")
        
        elif scrape_type == "Custom Elements":
            # CSS Selector input
            css_selector = st.text_input("CSS Selector", placeholder="div.product-item")
            
            # Attribute extraction
            st.subheader("Attributes to Extract")
            extract_text = st.checkbox("Extract text content", value=True)
            
            # Custom attributes
            custom_attrs = []
            with st.expander("Add Custom Attribute"):
                attr_name = st.text_input("Attribute Name", placeholder="price")
                attr_selector = st.text_input("CSS Selector (relative to main selector)", 
                                            placeholder=".price-tag")
                attr_type = st.radio("Extract", ["Text", "Attribute Value"])
                
                if attr_type == "Attribute Value":
                    attr_value = st.text_input("Attribute Name", placeholder="href")
                else:
                    attr_value = None
                
                if st.button("Add Attribute") and attr_name and attr_selector:
                    custom_attrs.append({
                        "name": attr_name,
                        "selector": attr_selector,
                        "type": attr_type,
                        "attr_value": attr_value
                    })
                    st.success(f"Added attribute: {attr_name}")
            
            # Display current attributes
            if custom_attrs:
                for i, attr in enumerate(custom_attrs):
                    st.text(f"{i+1}. {attr['name']} - {attr['selector']} ({attr['type']})")
            
            # Execute scraping
            if st.button("Scrape Elements", type="primary") and url and css_selector:
                with st.spinner("Scraping elements from website..."):
                    try:
                        # Fetch the webpage
                        response = requests.get(url)
                        response.raise_for_status()
                        
                        # Parse HTML
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find all matching elements
                        elements = soup.select(css_selector)
                        
                        if not elements:
                            st.warning(f"No elements found matching selector: {css_selector}")
                        else:
                            st.success(f"Found {len(elements)} matching elements")
                            
                            # Extract data
                            data = []
                            for element in elements:
                                item = {}
                                
                                # Extract text if requested
                                if extract_text:
                                    item["text"] = element.get_text(strip=True)
                                
                                # Extract custom attributes
                                for attr in custom_attrs:
                                    # Find the sub-element
                                    sub_elements = element.select(attr["selector"])
                                    if sub_elements:
                                        sub_element = sub_elements[0]
                                        
                                        if attr["type"] == "Text":
                                            item[attr["name"]] = sub_element.get_text(strip=True)
                                        else:  # Attribute Value
                                            item[attr["name"]] = sub_element.get(attr["attr_value"], "")
                                    else:
                                        item[attr["name"]] = ""
                                
                                data.append(item)
                            
                            # Convert to DataFrame
                            df = pd.DataFrame(data)
                            st.session_state.current_external_data = df
                            st.dataframe(df)
                            
                            # Save data source name
                            source_name = st.text_input("Save this data source as:", 
                                                      placeholder=f"Data from {urlparse(url).netloc}")
                            if st.button("Save Data Source") and source_name:
                                self._save_data_source(source_name, "web_custom", df, {
                                    "url": url,
                                    "css_selector": css_selector,
                                    "extract_text": extract_text,
                                    "custom_attrs": custom_attrs
                                })
                            
                            # Import to database option
                            if db_manager and db_manager.is_connected():
                                st.subheader("Import to Database")
                                table_name = st.text_input("Table name", 
                                                         placeholder="web_data")
                                if st.button("Import to Database") and table_name:
                                    self._import_to_database(db_manager, df, table_name)
                    
                    except Exception as e:
                        st.error(f"Error scraping website: {str(e)}")
    
    def saved_data_sources_ui(self, db_manager=None):
        """UI for managing saved data sources"""
        st.subheader("Saved Data Sources")
        
        if not st.session_state.external_data_sources:
            st.info("No saved data sources yet. Use the API Integration or Web Scraping tabs to create data sources.")
            return
        
        # Display saved data sources
        for i, source in enumerate(st.session_state.external_data_sources):
            with st.expander(f"{source['name']} ({source['type']})"):
                st.text(f"Created: {source['created_at']}")
                st.text(f"Type: {source['type']}")
                
                # Show configuration
                if st.checkbox("Show configuration", key=f"show_config_{i}"):
                    st.json(source['config'])
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Load Data", key=f"load_{i}"):
                        if source['type'] == 'api':
                            self._reload_api_data(source)
                        elif source['type'] in ['web_table', 'web_custom']:
                            self._reload_web_data(source)
                        else:
                            # Just load the cached data
                            st.session_state.current_external_data = source['data']
                            st.success(f"Loaded data from {source['name']}")
                
                with col2:
                    if st.button("Delete", key=f"delete_{i}"):
                        st.session_state.external_data_sources.pop(i)
                        st.rerun()
                
                with col3:
                    if db_manager and db_manager.is_connected():
                        if st.button("Import to DB", key=f"import_db_{i}"):
                            table_name = st.text_input("Table name", 
                                                     placeholder="external_data",
                                                     key=f"table_name_saved_{i}")
                            if st.button("Confirm Import", key=f"confirm_import_{i}") and table_name:
                                self._import_to_database(db_manager, source['data'], table_name)
    
    def _save_data_source(self, name, source_type, data, config):
        """Save a data source to session state"""
        st.session_state.external_data_sources.append({
            "name": name,
            "type": source_type,
            "data": data,
            "config": config,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"Saved data source: {name}")
    
    def _import_to_database(self, db_manager, df, table_name):
        """Import a DataFrame to the connected database"""
        try:
            # Get the database connection
            engine = db_manager.get_engine()
            
            if engine:
                # Import the data
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                st.success(f"Successfully imported data to table: {table_name}")
            else:
                st.error("No active database connection")
        except Exception as e:
            st.error(f"Error importing to database: {str(e)}")
    
    def _reload_api_data(self, source):
        """Reload data from an API source"""
        config = source['config']
        
        with st.spinner("Refreshing API data..."):
            try:
                # Prepare request arguments
                request_kwargs = {
                    "url": config['url'],
                    "headers": config['headers'] if config.get('headers') else None,
                }
                
                # Add parameters based on type
                if config.get('params'):
                    request_kwargs["params"] = config['params']
                elif config.get('json_body'):
                    request_kwargs["json"] = config['json_body']
                elif config.get('form_data'):
                    request_kwargs["data"] = config['form_data']
                
                # Make the request
                response = requests.request(config['method'], **request_kwargs)
                
                # Check if successful
                response.raise_for_status()
                
                # Try to parse as JSON
                data = response.json()
                
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.json_normalize(data)
                else:
                    st.error("Could not convert API response to DataFrame")
                    return
                
                # Update the data in the source
                source['data'] = df
                st.session_state.current_external_data = df
                st.success(f"Successfully refreshed data from {source['name']}")
                st.dataframe(df)
            
            except Exception as e:
                st.error(f"Error refreshing API data: {str(e)}")
    
    def _reload_web_data(self, source):
        """Reload data from a web source"""
        config = source['config']
        
        with st.spinner("Refreshing web data..."):
            try:
                # Fetch the webpage
                response = requests.get(config['url'])
                response.raise_for_status()
                
                if source['type'] == 'web_table':
                    # Parse tables
                    dfs = pd.read_html(response.text)
                    
                    if config['table_index'] < len(dfs):
                        df = dfs[config['table_index']]
                        source['data'] = df
                        st.session_state.current_external_data = df
                        st.success(f"Successfully refreshed data from {source['name']}")
                        st.dataframe(df)
                    else:
                        st.error("Table no longer exists on the webpage")
                
                elif source['type'] == 'web_custom':
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all matching elements
                    elements = soup.select(config['css_selector'])
                    
                    if not elements:
                        st.warning(f"No elements found matching selector: {config['css_selector']}")
                        return
                    
                    # Extract data
                    data = []
                    for element in elements:
                        item = {}
                        
                        # Extract text if requested
                        if config.get('extract_text'):
                            item["text"] = element.get_text(strip=True)
                        
                        # Extract custom attributes
                        for attr in config.get('custom_attrs', []):
                            # Find the sub-element
                            sub_elements = element.select(attr["selector"])
                            if sub_elements:
                                sub_element = sub_elements[0]
                                
                                if attr["type"] == "Text":
                                    item[attr["name"]] = sub_element.get_text(strip=True)
                                else:  # Attribute Value
                                    item[attr["name"]] = sub_element.get(attr["attr_value"], "")
                            else:
                                item[attr["name"]] = ""
                        
                        data.append(item)
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data)
                    source['data'] = df
                    st.session_state.current_external_data = df
                    st.success(f"Successfully refreshed data from {source['name']}")
                    st.dataframe(df)
            
            except Exception as e:
                st.error(f"Error refreshing web data: {str(e)}")
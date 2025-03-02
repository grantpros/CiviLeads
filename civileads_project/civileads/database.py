# database.py
import sqlite3
import pandas as pd
from civileads.config import DATABASE_PATH

def create_database():
    """Create the SQLite database and required tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create municipalities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS municipalities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        county TEXT,
        population INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, state)
    )
    ''')
    
    # Create officials table with linkedin_url column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS officials (
        id INTEGER PRIMARY KEY,
        municipality_id INTEGER,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        linkedin_url TEXT,
        confidence_score REAL,
        last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source TEXT,
        FOREIGN KEY (municipality_id) REFERENCES municipalities (id),
        UNIQUE(municipality_id, name, title)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def import_municipalities_from_excel(excel_path, state):
    """Import municipalities data from Excel file to the database"""
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Process each row
        for _, row in df.iterrows():
            # Extract data from DataFrame
            name = row['Municipality']
            county = row.get('County', None)
            population = row.get('Population', None)
            
            # Insert into database (ignore if already exists)
            cursor.execute('''
            INSERT OR IGNORE INTO municipalities (name, state, county, population)
            VALUES (?, ?, ?, ?)
            ''', (name, state, county, population))
        
        conn.commit()
        conn.close()
        print(f"Successfully imported municipalities for {state}.")
        return True
    except Exception as e:
        print(f"Error importing municipalities: {e}")
        return False

def get_municipalities(state=None, limit=None):
    """Get municipalities from the database, optionally filtered by state"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = "SELECT * FROM municipalities"
    params = []
    
    if state:
        query += " WHERE state = ?"
        params.append(state)
    
    query += " ORDER BY population DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def save_official(municipality_id, name, title, email, phone, linkedin_url, confidence_score, source):
    """Save an official's information to the database"""
    # Ensure municipality_id is an integer
    municipality_id = int(municipality_id)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO officials 
    (municipality_id, name, title, email, phone, linkedin_url, confidence_score, source, last_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (municipality_id, name, title, email, phone, linkedin_url, confidence_score, source))
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_officials(municipality_id=None):
    """Get officials from the database, optionally filtered by municipality"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = "SELECT o.*, m.name as municipality, m.state FROM officials o JOIN municipalities m ON o.municipality_id = m.id"
    params = []
    
    if municipality_id:
        query += " WHERE o.municipality_id = ?"
        params.append(municipality_id)
    
    query += " ORDER BY o.confidence_score DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def export_officials_to_excel(output_path, state=None):
    """Export officials data to Excel file"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Debug: Check if there are any officials in the database
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM officials")
    count = cursor.fetchone()[0]
    print(f"Found {count} officials in database.")
    
    if count == 0:
        conn.close()
        print("No officials in database to export.")
        return False
    
    # Prepare the SQL query
    if state:
        query = """
        SELECT 
            m.name as Municipality,
            m.state as State,
            m.county as County,
            m.population as Population,
            o.name as Official_Name,
            o.title as Title,
            o.email as Email,
            o.phone as Phone,
            o.linkedin_url as LinkedIn,
            o.confidence_score as Confidence,
            o.source as Source,
            o.last_verified as Last_Verified
        FROM officials o
        JOIN municipalities m ON o.municipality_id = m.id
        WHERE m.state = ?
        """
        params = [state]
    else:
        query = """
        SELECT 
            m.name as Municipality,
            m.state as State,
            m.county as County,
            m.population as Population,
            o.name as Official_Name,
            o.title as Title,
            o.email as Email,
            o.phone as Phone,
            o.linkedin_url as LinkedIn,
            o.confidence_score as Confidence,
            o.source as Source,
            o.last_verified as Last_Verified
        FROM officials o
        JOIN municipalities m ON o.municipality_id = m.id
        """
        params = []
    
    # Execute the query and convert to DataFrame
    df = pd.read_sql_query(query, conn, params=params)
    
    # Debug: Print DataFrame info
    print(f"Query returned {len(df)} rows")
    
    conn.close()
    
    if not df.empty:
        # Add additional formatting if needed
        df.to_excel(output_path, index=False)
        print(f"Officials data exported to {output_path}")
        return True
    else:
        print("Query returned no results. Please check database connections.")
        return False
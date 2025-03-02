#!/usr/bin/env python
"""
CiviLeads main execution script.
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from civileads.config import DATA_DIR
from civileads.database import (
    create_database, 
    get_municipalities, 
    import_municipalities_from_excel, 
    save_official,
    export_officials_to_excel
)
from civileads.scraper import search_for_officials

def initialize_sample_data():
    """Create sample data file if it doesn't exist."""
    sample_excel = os.path.join(DATA_DIR, 'sample_iowa.xlsx')
    
    if not os.path.exists(sample_excel):
        print("Creating sample data...")
        import pandas as pd
        # Create a small sample dataset
        df = pd.DataFrame({
            'Municipality': ['Des Moines', 'Cedar Rapids', 'Davenport'],
            'County': ['Polk', 'Linn', 'Scott'],
            'Population': [214133, 137710, 102320]
        })
        df.to_excel(sample_excel, index=False)
        print(f"Sample data created at {sample_excel}")
    
    # Import sample data
    print("Importing sample municipalities...")
    import_municipalities_from_excel(sample_excel, 'IA')
    
    # Check if import worked
    municipalities = get_municipalities('IA')
    print(f"Found {len(municipalities)} municipalities in database:")
    print(municipalities)
    
    return len(municipalities) > 0

def test_scraper(municipality_name='Des Moines', state='IA'):
    """Test scraper functionality for a specific municipality."""
    print(f"\nTesting scraper for {municipality_name}, {state}...")
    # Get municipality ID
    municipalities = get_municipalities(state)
    
    # Ensure municipality exists
    if municipality_name not in municipalities['name'].values:
        print(f"Error: Municipality '{municipality_name}' not found in database.")
        return False

    muni_id = municipalities[municipalities['name'] == municipality_name]['id'].values[0]
    
    # Search for officials
    print("Searching for officials...")
    officials = search_for_officials(municipality_name, state)
    
    if officials:
        print(f"Found {len(officials)} officials:")
        for official in officials:
            print(f"- {official['name']} ({official['title']}): Score {official['confidence_score']}")
            print(f"  Email: {official['email']}, Phone: {official['phone']}")
            if 'linkedin_url' in official and official['linkedin_url']:
                print(f"  LinkedIn: {official['linkedin_url']}")
            print(f"  Source: {official['source']}")
            
            # Save to database
            save_official(
                muni_id,
                official['name'],
                official['title'],
                official['email'],
                official['phone'],
                official.get('linkedin_url'),
                official['confidence_score'],
                official['source']
            )
        return True
    else:
        print("No officials found.")
        return False

def export_officials():
    """Export officials data to Excel."""
    export_path = os.path.join(DATA_DIR, 'municipal_officials.xlsx')
    print(f"\nExporting officials data to {export_path}...")
    success = export_officials_to_excel(export_path, 'IA')
    return success

def main():
    """Main execution function."""
    print("CiviLeads - Municipal Data Collection Tool")
    print("----------------------------------------")

    # Initialize database
    print("Initializing database...")
    create_database()
    
    # Set up sample data
    if initialize_sample_data():
        print("Database initialized successfully!")
        
        # Test scraper with multiple municipalities
        test_scraper('Des Moines', 'IA')
        test_scraper('Cedar Rapids', 'IA')
        
        # Export the collected officials data
        if export_officials():
            print("Officials data exported successfully!")
        else:
            print("Failed to export officials data.")
    else:
        print("Failed to initialize sample data. Check the errors above.")

if __name__ == "__main__":
    main()
"""
Export Data Utilities
Functions to export trip data to JSON, CSV, and Excel formats
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

def export_data(db_manager, trip_id, format_type):
    """Export trip data in specified format"""
    
    try:
        # Get all trip data
        trip_data = get_complete_trip_data(db_manager, trip_id)
        
        if format_type.lower() == 'json':
            export_json(trip_data)
        elif format_type.lower() == 'csv':
            export_csv(trip_data)
        elif format_type.lower() == 'excel':
            export_excel(trip_data)
        else:
            st.error(f"Unsupported export format: {format_type}")
    
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def get_complete_trip_data(db_manager, trip_id):
    """Get complete trip data from database"""
    
    # Get trip information
    trip = db_manager.get_trip(trip_id)
    
    # Get all related data
    destinations = db_manager.get_destinations(trip_id)
    activities = db_manager.get_activities(trip_id)
    transportation = db_manager.get_transportation(trip_id)
    
    # Get budget categories
    budget_categories = db_manager.get_budget_categories(trip_id)
    
    # Get expenses
    with db_manager.get_connection() as conn:
        expenses = [dict(row) for row in conn.execute("""
            SELECT * FROM expenses WHERE trip_id = ?
        """, (trip_id,))]
    
    # Get hotels
    with db_manager.get_connection() as conn:
        hotels = [dict(row) for row in conn.execute("""
            SELECT * FROM hotels WHERE trip_id = ?
        """, (trip_id,))]
    
    # Get emergency contacts
    with db_manager.get_connection() as conn:
        emergency_contacts = [dict(row) for row in conn.execute("""
            SELECT * FROM emergency_contacts WHERE trip_id = ?
        """, (trip_id,))]
    
    return {
        'trip': trip,
        'destinations': destinations,
        'activities': activities,
        'transportation': transportation,
        'budget_categories': budget_categories,
        'expenses': expenses,
        'hotels': hotels,
        'emergency_contacts': emergency_contacts,
        'export_timestamp': datetime.now().isoformat()
    }

def export_json(trip_data):
    """Export trip data as JSON"""
    
    json_data = json.dumps(trip_data, indent=2, default=str)
    
    trip_name = trip_data['trip']['name'].replace(' ', '_') if trip_data['trip'] else 'trip'
    filename = f"{trip_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    st.download_button(
        label="📥 Download JSON Export",
        data=json_data,
        file_name=filename,
        mime="application/json"
    )
    
    st.success(f"JSON export ready for download: {filename}")

def export_csv(trip_data):
    """Export trip data as CSV (multiple files in ZIP)"""
    
    import zipfile
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Export each data type as separate CSV
        data_types = [
            ('trip', [trip_data['trip']] if trip_data['trip'] else []),
            ('destinations', trip_data['destinations']),
            ('activities', trip_data['activities']),
            ('transportation', trip_data['transportation']),
            ('budget_categories', trip_data['budget_categories']),
            ('expenses', trip_data['expenses']),
            ('hotels', trip_data['hotels']),
            ('emergency_contacts', trip_data['emergency_contacts'])
        ]
        
        for data_name, data_list in data_types:
            if data_list:
                df = pd.DataFrame(data_list)
                csv_data = df.to_csv(index=False)
                zip_file.writestr(f"{data_name}.csv", csv_data)
    
    zip_buffer.seek(0)
    
    trip_name = trip_data['trip']['name'].replace(' ', '_') if trip_data['trip'] else 'trip'
    filename = f"{trip_name}_csv_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    st.download_button(
        label="📥 Download CSV Export (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=filename,
        mime="application/zip"
    )
    
    st.success(f"CSV export ready for download: {filename}")

def export_excel(trip_data):
    """Export trip data as Excel with multiple sheets"""
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        
        # Export each data type as separate sheet
        data_types = [
            ('Trip_Info', [trip_data['trip']] if trip_data['trip'] else []),
            ('Destinations', trip_data['destinations']),
            ('Activities', trip_data['activities']),
            ('Transportation', trip_data['transportation']),
            ('Budget_Categories', trip_data['budget_categories']),
            ('Expenses', trip_data['expenses']),
            ('Hotels', trip_data['hotels']),
            ('Emergency_Contacts', trip_data['emergency_contacts'])
        ]
        
        for sheet_name, data_list in data_types:
            if data_list:
                df = pd.DataFrame(data_list)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Create empty sheet with headers
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Add summary sheet
        create_summary_sheet(writer, trip_data)
    
    excel_buffer.seek(0)
    
    trip_name = trip_data['trip']['name'].replace(' ', '_') if trip_data['trip'] else 'trip'
    filename = f"{trip_name}_excel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    st.download_button(
        label="📥 Download Excel Export",
        data=excel_buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.success(f"Excel export ready for download: {filename}")

def create_summary_sheet(writer, trip_data):
    """Create a summary sheet for Excel export"""
    
    summary_data = []
    
    # Trip overview
    trip = trip_data['trip']
    if trip:
        summary_data.extend([
            ['TRIP OVERVIEW', ''],
            ['Trip Name', trip.get('name', 'N/A')],
            ['Description', trip.get('description', 'N/A')],
            ['Start Date', trip.get('start_date', 'N/A')],
            ['End Date', trip.get('end_date', 'N/A')],
            ['Total Budget', f"${trip.get('total_budget', 0):,.0f}"],
            ['', '']
        ])
    
    # Statistics
    destinations_count = len(trip_data['destinations'])
    activities_count = len(trip_data['activities'])
    transportation_count = len(trip_data['transportation'])
    hotels_count = len(trip_data['hotels'])
    
    summary_data.extend([
        ['STATISTICS', ''],
        ['Total Destinations', destinations_count],
        ['Total Activities', activities_count],
        ['Transportation Segments', transportation_count],
        ['Hotel Bookings', hotels_count],
        ['', '']
    ])
    
    # Budget summary
    total_expenses = sum(float(exp.get('amount', 0)) for exp in trip_data['expenses'])
    total_hotel_costs = sum(float(hotel.get('total_cost', 0)) for hotel in trip_data['hotels'])
    
    summary_data.extend([
        ['BUDGET SUMMARY', ''],
        ['Total Expenses Recorded', f"${total_expenses:,.2f}"],
        ['Total Hotel Costs', f"${total_hotel_costs:,.2f}"],
        ['', '']
    ])
    
    # Destinations summary
    summary_data.extend([
        ['DESTINATIONS', '']
    ])
    
    for dest in trip_data['destinations']:
        dest_activities = len([a for a in trip_data['activities'] if a.get('destination_id') == dest['id']])
        summary_data.append([
            f"{dest['name']}, {dest['country']}",
            f"{dest.get('duration_days', 0)} days, {dest_activities} activities, ${dest.get('budget', 0):,.0f}"
        ])
    
    # Create DataFrame and write to Excel
    summary_df = pd.DataFrame(summary_data, columns=['Category', 'Value'])
    summary_df.to_excel(writer, sheet_name='Summary', index=False)


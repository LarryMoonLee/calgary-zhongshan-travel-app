"""
Import Data Utilities
Functions to import trip data from JSON, CSV, and Excel formats
"""

import streamlit as st
import pandas as pd
import json
import zipfile
import io
from datetime import datetime

def import_data(db_manager, uploaded_file):
    """Import trip data from uploaded file"""
    
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'json':
            import_json(db_manager, uploaded_file)
        elif file_extension == 'csv':
            import_csv(db_manager, uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            import_excel(db_manager, uploaded_file)
        elif file_extension == 'zip':
            import_zip_csv(db_manager, uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return
        
        st.success("Data imported successfully!")
    
    except Exception as e:
        st.error(f"Import failed: {str(e)}")
        raise e

def import_json(db_manager, uploaded_file):
    """Import trip data from JSON file"""
    
    # Read JSON data
    json_data = json.load(uploaded_file)
    
    # Create new trip
    trip_data = json_data.get('trip', {})
    trip_id = db_manager.create_trip(
        name=trip_data.get('name', 'Imported Trip'),
        description=trip_data.get('description', 'Imported from JSON'),
        start_date=trip_data.get('start_date'),
        end_date=trip_data.get('end_date'),
        total_budget=float(trip_data.get('total_budget', 0))
    )
    
    # Import destinations
    destinations_map = {}
    for dest_data in json_data.get('destinations', []):
        dest_id = db_manager.add_destination(
            trip_id=trip_id,
            name=dest_data.get('name'),
            country=dest_data.get('country'),
            arrival_date=dest_data.get('arrival_date'),
            departure_date=dest_data.get('departure_date'),
            duration_days=dest_data.get('duration_days'),
            budget=float(dest_data.get('budget', 0)),
            description=dest_data.get('description'),
            weather=dest_data.get('weather'),
            accommodation=dest_data.get('accommodation')
        )
        destinations_map[dest_data.get('id')] = dest_id
    
    # Import activities
    for activity_data in json_data.get('activities', []):
        original_dest_id = activity_data.get('destination_id')
        new_dest_id = destinations_map.get(original_dest_id)
        
        if new_dest_id:
            db_manager.add_activity(
                trip_id=trip_id,
                destination_id=new_dest_id,
                title=activity_data.get('title'),
                description=activity_data.get('description'),
                planned_date=activity_data.get('planned_date'),
                planned_time=activity_data.get('planned_time'),
                duration_minutes=activity_data.get('duration_minutes'),
                cost=float(activity_data.get('cost', 0)),
                priority=activity_data.get('priority', 1),
                status=activity_data.get('status', 'pending'),
                category=activity_data.get('category'),
                location=activity_data.get('location'),
                notes=activity_data.get('notes')
            )
    
    # Import transportation
    for transport_data in json_data.get('transportation', []):
        from_dest_id = destinations_map.get(transport_data.get('from_destination_id'))
        to_dest_id = destinations_map.get(transport_data.get('to_destination_id'))
        
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO transportation (
                    trip_id, from_destination_id, to_destination_id, transport_type,
                    departure_datetime, arrival_datetime, cost, booking_reference,
                    notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trip_id, from_dest_id, to_dest_id,
                transport_data.get('transport_type'),
                transport_data.get('departure_datetime'),
                transport_data.get('arrival_datetime'),
                float(transport_data.get('cost', 0)),
                transport_data.get('booking_reference'),
                transport_data.get('notes'),
                transport_data.get('status', 'planned')
            ))
    
    # Import budget categories
    for budget_data in json_data.get('budget_categories', []):
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO budget_categories (
                    trip_id, category_name, allocated_amount, spent_amount, description
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                trip_id,
                budget_data.get('category_name'),
                float(budget_data.get('allocated_amount', 0)),
                float(budget_data.get('spent_amount', 0)),
                budget_data.get('description')
            ))
    
    # Import expenses
    for expense_data in json_data.get('expenses', []):
        original_dest_id = expense_data.get('destination_id')
        new_dest_id = destinations_map.get(original_dest_id) if original_dest_id else None
        
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO expenses (
                    trip_id, destination_id, category, description, amount,
                    expense_date, payment_method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trip_id, new_dest_id,
                expense_data.get('category'),
                expense_data.get('description'),
                float(expense_data.get('amount', 0)),
                expense_data.get('expense_date'),
                expense_data.get('payment_method'),
                expense_data.get('notes')
            ))
    
    # Import hotels
    for hotel_data in json_data.get('hotels', []):
        original_dest_id = hotel_data.get('destination_id')
        new_dest_id = destinations_map.get(original_dest_id)
        
        if new_dest_id:
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO hotels (
                        trip_id, destination_id, name, address, phone, email,
                        check_in_date, check_out_date, room_type, rate_per_night,
                        total_cost, booking_reference, rating, notes, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trip_id, new_dest_id,
                    hotel_data.get('name'),
                    hotel_data.get('address'),
                    hotel_data.get('phone'),
                    hotel_data.get('email'),
                    hotel_data.get('check_in_date'),
                    hotel_data.get('check_out_date'),
                    hotel_data.get('room_type'),
                    float(hotel_data.get('rate_per_night', 0)),
                    float(hotel_data.get('total_cost', 0)),
                    hotel_data.get('booking_reference'),
                    float(hotel_data.get('rating', 0)),
                    hotel_data.get('notes'),
                    hotel_data.get('status', 'planned')
                ))
    
    # Import emergency contacts
    for contact_data in json_data.get('emergency_contacts', []):
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO emergency_contacts (
                    trip_id, name, relationship, phone, email, address
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trip_id,
                contact_data.get('name'),
                contact_data.get('relationship'),
                contact_data.get('phone'),
                contact_data.get('email'),
                contact_data.get('address')
            ))
    
    # Update session state to show new trip
    st.session_state.current_trip_id = trip_id

def import_csv(db_manager, uploaded_file):
    """Import trip data from single CSV file"""
    
    # For single CSV, assume it's a destinations file
    df = pd.read_csv(uploaded_file)
    
    # Create new trip
    trip_id = db_manager.create_trip(
        name=f"Imported Trip {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description="Imported from CSV file",
        start_date=datetime.now().date(),
        end_date=datetime.now().date(),
        total_budget=0.0
    )
    
    # Import destinations from CSV
    for _, row in df.iterrows():
        db_manager.add_destination(
            trip_id=trip_id,
            name=row.get('name', 'Unknown'),
            country=row.get('country', 'Unknown'),
            arrival_date=row.get('arrival_date'),
            departure_date=row.get('departure_date'),
            duration_days=int(row.get('duration_days', 1)),
            budget=float(row.get('budget', 0)),
            description=row.get('description', ''),
            weather=row.get('weather', ''),
            accommodation=row.get('accommodation', '')
        )
    
    st.session_state.current_trip_id = trip_id

def import_zip_csv(db_manager, uploaded_file):
    """Import trip data from ZIP file containing multiple CSVs"""
    
    # Create new trip
    trip_id = db_manager.create_trip(
        name=f"Imported Trip {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description="Imported from ZIP/CSV files",
        start_date=datetime.now().date(),
        end_date=datetime.now().date(),
        total_budget=0.0
    )
    
    destinations_map = {}
    
    with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
        
        # Import trip info if available
        if 'trip.csv' in zip_file.namelist():
            trip_df = pd.read_csv(zip_file.open('trip.csv'))
            if not trip_df.empty:
                trip_row = trip_df.iloc[0]
                db_manager.update_trip(
                    trip_id,
                    name=trip_row.get('name', 'Imported Trip'),
                    description=trip_row.get('description', 'Imported from CSV'),
                    start_date=trip_row.get('start_date'),
                    end_date=trip_row.get('end_date'),
                    total_budget=float(trip_row.get('total_budget', 0))
                )
        
        # Import destinations
        if 'destinations.csv' in zip_file.namelist():
            dest_df = pd.read_csv(zip_file.open('destinations.csv'))
            for _, row in dest_df.iterrows():
                dest_id = db_manager.add_destination(
                    trip_id=trip_id,
                    name=row.get('name'),
                    country=row.get('country'),
                    arrival_date=row.get('arrival_date'),
                    departure_date=row.get('departure_date'),
                    duration_days=int(row.get('duration_days', 1)),
                    budget=float(row.get('budget', 0)),
                    description=row.get('description', ''),
                    weather=row.get('weather', ''),
                    accommodation=row.get('accommodation', '')
                )
                destinations_map[row.get('id')] = dest_id
        
        # Import activities
        if 'activities.csv' in zip_file.namelist():
            activities_df = pd.read_csv(zip_file.open('activities.csv'))
            for _, row in activities_df.iterrows():
                original_dest_id = row.get('destination_id')
                new_dest_id = destinations_map.get(original_dest_id)
                
                if new_dest_id:
                    db_manager.add_activity(
                        trip_id=trip_id,
                        destination_id=new_dest_id,
                        title=row.get('title'),
                        description=row.get('description'),
                        planned_date=row.get('planned_date'),
                        planned_time=row.get('planned_time'),
                        duration_minutes=int(row.get('duration_minutes', 60)),
                        cost=float(row.get('cost', 0)),
                        priority=int(row.get('priority', 1)),
                        status=row.get('status', 'pending'),
                        category=row.get('category'),
                        location=row.get('location'),
                        notes=row.get('notes')
                    )
        
        # Import other data types similarly...
        # (Transportation, budget categories, expenses, hotels, emergency contacts)
    
    st.session_state.current_trip_id = trip_id

def import_excel(db_manager, uploaded_file):
    """Import trip data from Excel file with multiple sheets"""
    
    # Read Excel file
    excel_file = pd.ExcelFile(uploaded_file)
    
    # Create new trip
    trip_id = db_manager.create_trip(
        name=f"Imported Trip {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description="Imported from Excel file",
        start_date=datetime.now().date(),
        end_date=datetime.now().date(),
        total_budget=0.0
    )
    
    destinations_map = {}
    
    # Import trip info
    if 'Trip_Info' in excel_file.sheet_names:
        trip_df = pd.read_excel(uploaded_file, sheet_name='Trip_Info')
        if not trip_df.empty:
            trip_row = trip_df.iloc[0]
            db_manager.update_trip(
                trip_id,
                name=trip_row.get('name', 'Imported Trip'),
                description=trip_row.get('description', 'Imported from Excel'),
                start_date=trip_row.get('start_date'),
                end_date=trip_row.get('end_date'),
                total_budget=float(trip_row.get('total_budget', 0))
            )
    
    # Import destinations
    if 'Destinations' in excel_file.sheet_names:
        dest_df = pd.read_excel(uploaded_file, sheet_name='Destinations')
        for _, row in dest_df.iterrows():
            dest_id = db_manager.add_destination(
                trip_id=trip_id,
                name=row.get('name'),
                country=row.get('country'),
                arrival_date=row.get('arrival_date'),
                departure_date=row.get('departure_date'),
                duration_days=int(row.get('duration_days', 1)),
                budget=float(row.get('budget', 0)),
                description=row.get('description', ''),
                weather=row.get('weather', ''),
                accommodation=row.get('accommodation', '')
            )
            destinations_map[row.get('id')] = dest_id
    
    # Import activities
    if 'Activities' in excel_file.sheet_names:
        activities_df = pd.read_excel(uploaded_file, sheet_name='Activities')
        for _, row in activities_df.iterrows():
            original_dest_id = row.get('destination_id')
            new_dest_id = destinations_map.get(original_dest_id)
            
            if new_dest_id:
                db_manager.add_activity(
                    trip_id=trip_id,
                    destination_id=new_dest_id,
                    title=row.get('title'),
                    description=row.get('description'),
                    planned_date=row.get('planned_date'),
                    planned_time=row.get('planned_time'),
                    duration_minutes=int(row.get('duration_minutes', 60)),
                    cost=float(row.get('cost', 0)),
                    priority=int(row.get('priority', 1)),
                    status=row.get('status', 'pending'),
                    category=row.get('category'),
                    location=row.get('location'),
                    notes=row.get('notes')
                )
    
    # Import budget categories
    if 'Budget_Categories' in excel_file.sheet_names:
        budget_df = pd.read_excel(uploaded_file, sheet_name='Budget_Categories')
        for _, row in budget_df.iterrows():
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO budget_categories (
                        trip_id, category_name, allocated_amount, spent_amount, description
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    trip_id,
                    row.get('category_name'),
                    float(row.get('allocated_amount', 0)),
                    float(row.get('spent_amount', 0)),
                    row.get('description')
                ))
    
    # Import expenses
    if 'Expenses' in excel_file.sheet_names:
        expenses_df = pd.read_excel(uploaded_file, sheet_name='Expenses')
        for _, row in expenses_df.iterrows():
            original_dest_id = row.get('destination_id')
            new_dest_id = destinations_map.get(original_dest_id) if pd.notna(original_dest_id) else None
            
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO expenses (
                        trip_id, destination_id, category, description, amount,
                        expense_date, payment_method, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trip_id, new_dest_id,
                    row.get('category'),
                    row.get('description'),
                    float(row.get('amount', 0)),
                    row.get('expense_date'),
                    row.get('payment_method'),
                    row.get('notes')
                ))
    
    # Import hotels
    if 'Hotels' in excel_file.sheet_names:
        hotels_df = pd.read_excel(uploaded_file, sheet_name='Hotels')
        for _, row in hotels_df.iterrows():
            original_dest_id = row.get('destination_id')
            new_dest_id = destinations_map.get(original_dest_id)
            
            if new_dest_id:
                with db_manager.get_connection() as conn:
                    conn.execute("""
                        INSERT INTO hotels (
                            trip_id, destination_id, name, address, phone, email,
                            check_in_date, check_out_date, room_type, rate_per_night,
                            total_cost, booking_reference, rating, notes, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        trip_id, new_dest_id,
                        row.get('name'),
                        row.get('address'),
                        row.get('phone'),
                        row.get('email'),
                        row.get('check_in_date'),
                        row.get('check_out_date'),
                        row.get('room_type'),
                        float(row.get('rate_per_night', 0)),
                        float(row.get('total_cost', 0)),
                        row.get('booking_reference'),
                        float(row.get('rating', 0)),
                        row.get('notes'),
                        row.get('status', 'planned')
                    ))
    
    # Import emergency contacts
    if 'Emergency_Contacts' in excel_file.sheet_names:
        contacts_df = pd.read_excel(uploaded_file, sheet_name='Emergency_Contacts')
        for _, row in contacts_df.iterrows():
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO emergency_contacts (
                        trip_id, name, relationship, phone, email, address
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trip_id,
                    row.get('name'),
                    row.get('relationship'),
                    row.get('phone'),
                    row.get('email'),
                    row.get('address')
                ))
    
    st.session_state.current_trip_id = trip_id


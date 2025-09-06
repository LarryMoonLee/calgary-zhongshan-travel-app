"""
Calgary to Zhongshan Travel Planner
A comprehensive Streamlit application for managing your travel journeys

Author: Travel Planning Assistant
Version: 1.0.0
Platform: Windows 11, Python 3.10.10
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import csv
import io
from datetime import datetime, date, time, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import DatabaseManager
from src.pages import (
    journey_page, route_page, destinations_page, 
    budget_page, itinerary_page, hotels_page, tools_page
)
from src.utils import export_data, import_data

# Page configuration
st.set_page_config(
    page_title="Calgary to Zhongshan Travel Planner - Demo",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Demo Mode Warning - Prominent Display
st.markdown("""
<div style="background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%); 
            padding: 1rem; border-radius: 10px; color: white; text-align: center; 
            margin-bottom: 1rem; border: 2px solid #ff4757;">
    <h3>🌐 DEMO MODE - ONLINE VERSION</h3>
    <p><strong>⚠️ Important:</strong> This is a demonstration version running on Streamlit Community Cloud.</p>
    <p><strong>📝 Data Notice:</strong> All trip data resets when the app restarts. Export your data regularly!</p>
    <p><strong>💾 Tip:</strong> Use the Export/Import features in the sidebar to save your travel plans.</p>
</div>
""", unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .tab-content {
        padding: 1rem 0;
    }
    
    .edit-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .trip-card {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 3px solid #007bff;
        margin: 0.5rem 0;
        cursor: pointer;
    }
    
    .trip-card:hover {
        background: #e9ecef;
    }
    
    .trip-card.active {
        background: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .sidebar-section {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize the application and database"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
        st.session_state.db_manager.initialize_database()
    
    if 'current_trip_id' not in st.session_state:
        # Get existing trips or create default
        trips = st.session_state.db_manager.get_all_trips()
        if trips:
            st.session_state.current_trip_id = trips[0]['id']
        else:
            # Create default Calgary to Zhongshan trip
            trip_id = st.session_state.db_manager.create_trip(
                "Calgary to Zhongshan Journey",
                "50-day cultural odyssey through Japan and China",
                date(2024, 11, 8),
                date(2024, 12, 28),
                10000.0
            )
            st.session_state.current_trip_id = trip_id
            
            # Add default destinations
            add_default_destinations(st.session_state.db_manager, trip_id)

def add_default_destinations(db_manager, trip_id):
    """Add default destinations for the Calgary to Zhongshan trip"""
    
    default_destinations = [
        {
            "name": "Tokyo",
            "country": "Japan",
            "arrival_date": date(2024, 11, 8),
            "departure_date": date(2024, 11, 11),
            "duration_days": 3,
            "budget": 730.0,
            "description": "Experience the perfect blend of ancient traditions and cutting-edge modernity in Japan's vibrant capital.",
            "weather": "Cool autumn, 10-18°C",
            "accommodation": "Hotel Nikko Narita"
        },
        {
            "name": "Shenzhen",
            "country": "China",
            "arrival_date": date(2024, 11, 11),
            "departure_date": date(2024, 11, 14),
            "duration_days": 3,
            "budget": 360.0,
            "description": "Modern metropolis showcasing China's technological advancement and innovation.",
            "weather": "Warm subtropical, 18-25°C",
            "accommodation": "Vienna Hotel Shenzhen North"
        },
        {
            "name": "Zhongshan",
            "country": "China",
            "arrival_date": date(2024, 11, 14),
            "departure_date": date(2024, 11, 18),
            "duration_days": 4,
            "budget": 360.0,
            "description": "Historic city with rich cultural heritage and beautiful landscapes.",
            "weather": "Pleasant subtropical, 20-26°C",
            "accommodation": "Local guesthouse"
        },
        {
            "name": "Jinan",
            "country": "China",
            "arrival_date": date(2024, 11, 18),
            "departure_date": date(2024, 11, 23),
            "duration_days": 5,
            "budget": 600.0,
            "description": "City of Springs with natural beauty and cultural significance.",
            "weather": "Cool autumn, 8-15°C",
            "accommodation": "Jinan Central Hotel"
        },
        {
            "name": "Beijing",
            "country": "China",
            "arrival_date": date(2024, 11, 23),
            "departure_date": date(2024, 11, 26),
            "duration_days": 3,
            "budget": 900.0,
            "description": "China's imperial capital with rich history, iconic landmarks, and political significance.",
            "weather": "Cold autumn, 0-10°C",
            "accommodation": "Hampton by Hilton Beijing South"
        }
    ]
    
    for dest_data in default_destinations:
        db_manager.add_destination(trip_id=trip_id, **dest_data)

def render_sidebar():
    """Render the enhanced sidebar with trip management"""
    
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h2>🎯 Trip Management</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Create new trip section
        with st.expander("➕ Create New Trip", expanded=False):
            with st.form("create_new_trip"):
                st.subheader("Create New Trip")
                
                trip_name = st.text_input("Trip Name*", placeholder="e.g., European Adventure")
                trip_description = st.text_area("Description", placeholder="Brief description of your journey...")
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=date.today())
                with col2:
                    end_date = st.date_input("End Date", value=date.today())
                
                total_budget = st.number_input("Total Budget ($)", min_value=0.0, value=5000.0, step=100.0)
                
                if st.form_submit_button("🚀 Create Trip"):
                    if trip_name and start_date and end_date and start_date <= end_date:
                        trip_id = st.session_state.db_manager.create_trip(
                            name=trip_name,
                            description=trip_description,
                            start_date=start_date,
                            end_date=end_date,
                            total_budget=total_budget
                        )
                        st.session_state.current_trip_id = trip_id
                        st.success(f"Trip '{trip_name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields and ensure start date is before end date.")
        
        st.divider()
        
        # Trip selector and list
        st.markdown("""
        <div class="sidebar-section">
            <h3>📋 Your Trips</h3>
        </div>
        """, unsafe_allow_html=True)
        
        trips = st.session_state.db_manager.get_all_trips()
        
        if trips:
            # Display trip list with selection
            for trip in trips:
                is_active = trip['id'] == st.session_state.current_trip_id
                
                # Calculate trip duration
                if trip.get('start_date') and trip.get('end_date'):
                    start = datetime.strptime(trip['start_date'], '%Y-%m-%d').date()
                    end = datetime.strptime(trip['end_date'], '%Y-%m-%d').date()
                    duration = (end - start).days + 1
                else:
                    duration = 0
                
                # Trip card
                card_class = "trip-card active" if is_active else "trip-card"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{'🎯' if is_active else '📍'} {trip['name']}</h4>
                    <p><small>{trip.get('description', 'No description')[:50]}{'...' if len(trip.get('description', '')) > 50 else ''}</small></p>
                    <p><small>📅 {duration} days • 💰 ${trip.get('total_budget', 0):,.0f}</small></p>
                    <p><small>🗓️ {trip.get('start_date', 'N/A')} to {trip.get('end_date', 'N/A')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Trip action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if not is_active and st.button("📂", key=f"select_{trip['id']}", help="Select this trip"):
                        st.session_state.current_trip_id = trip['id']
                        st.rerun()
                
                with col2:
                    if st.button("✏️", key=f"edit_{trip['id']}", help="Edit trip"):
                        st.session_state[f"edit_trip_{trip['id']}"] = True
                
                with col3:
                    if st.button("🗑️", key=f"delete_{trip['id']}", help="Delete trip"):
                        st.session_state[f"confirm_delete_{trip['id']}"] = True
                
                # Edit trip form
                if st.session_state.get(f"edit_trip_{trip['id']}", False):
                    with st.form(f"edit_trip_form_{trip['id']}"):
                        st.subheader(f"Edit: {trip['name']}")
                        
                        new_name = st.text_input("Name", value=trip.get('name', ''))
                        new_description = st.text_area("Description", value=trip.get('description', ''))
                        new_start = st.date_input(
                            "Start Date",
                            value=datetime.strptime(trip.get('start_date', '2024-01-01'), '%Y-%m-%d').date() if trip.get('start_date') else date.today()
                        )
                        new_end = st.date_input(
                            "End Date",
                            value=datetime.strptime(trip.get('end_date', '2024-01-01'), '%Y-%m-%d').date() if trip.get('end_date') else date.today()
                        )
                        new_budget = st.number_input("Budget ($)", value=float(trip.get('total_budget', 0)), min_value=0.0)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save"):
                                st.session_state.db_manager.update_trip(
                                    trip['id'],
                                    name=new_name,
                                    description=new_description,
                                    start_date=new_start,
                                    end_date=new_end,
                                    total_budget=new_budget
                                )
                                st.success("Trip updated!")
                                st.session_state[f"edit_trip_{trip['id']}"] = False
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_trip_{trip['id']}"] = False
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{trip['id']}", False):
                    st.warning(f"⚠️ Delete '{trip['name']}'?")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🗑️ Yes, Delete", key=f"confirm_yes_{trip['id']}"):
                            # Delete trip and all related data
                            with st.session_state.db_manager.get_connection() as conn:
                                conn.execute("DELETE FROM trips WHERE id = ?", (trip['id'],))
                            
                            # If this was the current trip, select another one
                            if trip['id'] == st.session_state.current_trip_id:
                                remaining_trips = [t for t in trips if t['id'] != trip['id']]
                                if remaining_trips:
                                    st.session_state.current_trip_id = remaining_trips[0]['id']
                                else:
                                    # Create a new default trip
                                    new_trip_id = st.session_state.db_manager.create_trip(
                                        "New Journey",
                                        "Plan your next adventure",
                                        date.today(),
                                        date.today() + timedelta(days=7),
                                        5000.0
                                    )
                                    st.session_state.current_trip_id = new_trip_id
                            
                            st.success("Trip deleted!")
                            st.session_state[f"confirm_delete_{trip['id']}"] = False
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_{trip['id']}"):
                            st.session_state[f"confirm_delete_{trip['id']}"] = False
                            st.rerun()
                
                st.divider()
        else:
            st.info("No trips found. Create your first trip above!")
        
        st.divider()
        
        # Current trip quick stats
        if st.session_state.current_trip_id:
            current_trip = st.session_state.db_manager.get_trip(st.session_state.current_trip_id)
            if current_trip:
                st.markdown(f"""
                <div class="sidebar-section">
                    <h3>📊 Current Trip Stats</h3>
                    <h4>{current_trip['name']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                trip_stats = st.session_state.db_manager.get_trip_statistics(st.session_state.current_trip_id)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Days", trip_stats.get('total_days', 0))
                    st.metric("Cities", trip_stats.get('total_cities', 0))
                with col2:
                    st.metric("Budget", f"${trip_stats.get('total_budget', 0):,.0f}")
                    st.metric("Activities", trip_stats.get('total_activities', 0))
        
        st.divider()
        
        # Import/Export section
        st.markdown("""
        <div class="sidebar-section">
            <h3>📁 Data Management</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Export/Import for Demo Mode
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #007bff;">
            <h4>💾 Data Backup (Important for Demo)</h4>
            <p><strong>Export regularly</strong> to save your travel plans!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Export options
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "CSV", "Excel"],
            help="Choose format for downloading your trip data"
        )
        
        if st.button("📤 Export Current Trip", type="primary"):
            if st.session_state.current_trip_id:
                export_data(st.session_state.db_manager, 
                           st.session_state.current_trip_id, 
                           export_format.lower())
                st.success("✅ Export ready! Download will start automatically.")
            else:
                st.warning("No trip selected for export.")
        
        st.divider()
        
        # Import file uploader
        st.markdown("**📥 Restore Trip Data**")
        uploaded_file = st.file_uploader(
            "Choose file to import",
            type=['json', 'csv', 'xlsx'],
            help="Import trip data from a previously exported file"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 File selected: {uploaded_file.name}")
            if st.button("📥 Import Data", type="secondary"):
                try:
                    import_data(st.session_state.db_manager, uploaded_file)
                    st.success("✅ Data imported successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Import failed: {str(e)}")
        
        # Quick backup reminder
        st.markdown("""
        <div style="background: #fff3cd; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
            <small>💡 <strong>Pro Tip:</strong> Export after making changes!</small>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_app()
    
    # Render sidebar
    render_sidebar()
    
    # Get current trip for header
    current_trip = st.session_state.db_manager.get_trip(st.session_state.current_trip_id)
    trip_name = current_trip['name'] if current_trip else "Travel Planner"
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>✈️ {trip_name}</h1>
        <p>{current_trip.get('description', 'Your comprehensive travel planning companion') if current_trip else 'Your comprehensive travel planning companion'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Journey", "🗺️ Route", "📍 Destinations", 
        "💰 Budget", "📅 Itinerary", "🏨 Hotels", "🛠️ Tools"
    ])
    
    with tab1:
        journey_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab2:
        route_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab3:
        destinations_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab4:
        budget_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab5:
        itinerary_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab6:
        hotels_page.render(st.session_state.db_manager, st.session_state.current_trip_id)
    
    with tab7:
        tools_page.render(st.session_state.db_manager, st.session_state.current_trip_id)

if __name__ == "__main__":
    main()


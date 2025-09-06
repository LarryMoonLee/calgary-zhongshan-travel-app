"""
Journey Page - Trip Overview and Management
Main dashboard for trip information and quick access
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

def render(db_manager, trip_id):
    """Render the journey overview page"""
    
    # Get trip information
    trip = db_manager.get_trip(trip_id)
    if not trip:
        st.error("Trip not found!")
        return
    
    # Header with trip info
    st.markdown(f"""
    <div class="main-header">
        <h1>🌏 {trip['name']}</h1>
        <p>{trip.get('description', 'Your amazing journey awaits!')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Trip statistics
    stats = db_manager.get_trip_statistics(trip_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Total Days", stats.get('total_days', 0))
    
    with col2:
        st.metric("🏙️ Cities", stats.get('total_cities', 0))
    
    with col3:
        st.metric("💰 Budget", f"${stats.get('total_budget', 0):,.0f}")
    
    with col4:
        st.metric("✅ Activities", stats.get('total_activities', 0))
    
    st.divider()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🎯 Trip Overview", "📝 Manage Trip", "📊 Quick Stats"])
    
    with tab1:
        render_trip_overview(db_manager, trip_id, trip)
    
    with tab2:
        render_trip_management(db_manager, trip_id, trip)
    
    with tab3:
        render_quick_stats(db_manager, trip_id)

def render_trip_overview(db_manager, trip_id, trip):
    """Render trip overview section"""
    
    st.subheader("🎯 Journey Overview")
    
    # Trip timeline
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="edit-section">
            <h4>📅 Trip Timeline</h4>
            <p><strong>Start Date:</strong> {trip.get('start_date', 'Not set')}</p>
            <p><strong>End Date:</strong> {trip.get('end_date', 'Not set')}</p>
            <p><strong>Duration:</strong> {(datetime.strptime(trip['end_date'], '%Y-%m-%d') - datetime.strptime(trip['start_date'], '%Y-%m-%d')).days + 1 if trip.get('start_date') and trip.get('end_date') else 'Unknown'} days</p>
            <p><strong>Budget:</strong> ${trip.get('total_budget', 0):,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🌟 Journey Highlights</h4>
            <p>• Cultural immersion in Japan</p>
            <p>• Modern China exploration</p>
            <p>• High-speed rail experience</p>
            <p>• Senior-friendly accommodations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Destinations overview
    destinations = db_manager.get_destinations(trip_id)
    
    if destinations:
        st.subheader("🏙️ Destinations")
        
        for dest in destinations:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{dest['name']}, {dest['country']}**")
                if dest.get('description'):
                    st.caption(dest['description'][:100] + "..." if len(dest.get('description', '')) > 100 else dest.get('description', ''))
            
            with col2:
                st.write(f"📅 {dest.get('duration_days', 'N/A')} days")
            
            with col3:
                st.write(f"💰 ${dest.get('budget', 0):,.0f}")
            
            with col4:
                activities_count = len(db_manager.get_activities(trip_id, dest['id']))
                st.write(f"✅ {activities_count} activities")
    else:
        st.info("No destinations added yet. Add destinations to start planning your journey!")
    
    # Recent activities
    st.subheader("📋 Recent Activities")
    
    all_activities = db_manager.get_activities(trip_id)
    recent_activities = sorted(all_activities, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    if recent_activities:
        for activity in recent_activities:
            dest_name = "Unknown"
            for dest in destinations:
                if dest['id'] == activity.get('destination_id'):
                    dest_name = dest['name']
                    break
            
            status_icons = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }
            
            status_icon = status_icons.get(activity.get('status', 'pending'), '⚪')
            
            st.write(f"{status_icon} **{activity.get('title', 'Untitled')}** in {dest_name}")
    else:
        st.info("No activities added yet.")

def render_trip_management(db_manager, trip_id, trip):
    """Render trip management section"""
    
    st.subheader("📝 Manage Trip Information")
    
    # Edit trip details
    with st.form("edit_trip"):
        st.write("**Edit Trip Details**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Trip Name", value=trip.get('name', ''))
            new_description = st.text_area("Description", value=trip.get('description', ''))
            new_start_date = st.date_input(
                "Start Date",
                value=datetime.strptime(trip.get('start_date', '2024-11-08'), '%Y-%m-%d').date() if trip.get('start_date') else date.today()
            )
        
        with col2:
            new_end_date = st.date_input(
                "End Date",
                value=datetime.strptime(trip.get('end_date', '2024-12-28'), '%Y-%m-%d').date() if trip.get('end_date') else date.today()
            )
            new_budget = st.number_input("Total Budget ($)", value=float(trip.get('total_budget', 0)), min_value=0.0)
        
        if st.form_submit_button("💾 Update Trip"):
            db_manager.update_trip(
                trip_id,
                name=new_name,
                description=new_description,
                start_date=new_start_date,
                end_date=new_end_date,
                total_budget=new_budget
            )
            st.success("Trip updated successfully!")
            st.rerun()
    
    st.divider()
    
    # Add new destination
    with st.expander("➕ Add New Destination"):
        with st.form("add_destination"):
            st.subheader("Add New Destination")
            
            col1, col2 = st.columns(2)
            
            with col1:
                dest_name = st.text_input("Destination Name*")
                dest_country = st.text_input("Country*")
                arrival_date = st.date_input("Arrival Date")
                departure_date = st.date_input("Departure Date")
            
            with col2:
                duration_days = st.number_input("Duration (days)", min_value=1, value=1)
                dest_budget = st.number_input("Budget for this destination ($)", min_value=0.0, value=0.0)
                weather = st.text_input("Weather Info")
                accommodation = st.text_input("Accommodation")
            
            description = st.text_area("Description")
            
            if st.form_submit_button("➕ Add Destination"):
                if dest_name and dest_country:
                    dest_id = db_manager.add_destination(
                        trip_id=trip_id,
                        name=dest_name,
                        country=dest_country,
                        arrival_date=arrival_date,
                        departure_date=departure_date,
                        duration_days=duration_days,
                        budget=dest_budget,
                        weather=weather,
                        accommodation=accommodation,
                        description=description
                    )
                    st.success(f"Destination added successfully! ID: {dest_id}")
                    st.rerun()
                else:
                    st.error("Please enter destination name and country.")

def render_quick_stats(db_manager, trip_id):
    """Render quick statistics and charts"""
    
    st.subheader("📊 Trip Statistics")
    
    # Get data
    destinations = db_manager.get_destinations(trip_id)
    activities = db_manager.get_activities(trip_id)
    transportation = db_manager.get_transportation(trip_id)
    
    if not destinations:
        st.info("Add destinations to see statistics.")
        return
    
    # Budget breakdown by destination
    if destinations:
        dest_names = [dest['name'] for dest in destinations]
        dest_budgets = [float(dest.get('budget', 0)) for dest in destinations]
        
        if sum(dest_budgets) > 0:
            fig = px.pie(
                values=dest_budgets,
                names=dest_names,
                title="Budget Distribution by Destination"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Activities by status
    if activities:
        status_counts = {}
        for activity in activities:
            status = activity.get('status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                title="Activities by Status",
                labels={'x': 'Status', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Transportation costs
    if transportation:
        transport_costs = {}
        for transport in transportation:
            t_type = transport.get('transport_type', 'unknown')
            cost = float(transport.get('cost', 0))
            transport_costs[t_type] = transport_costs.get(t_type, 0) + cost
        
        if transport_costs and sum(transport_costs.values()) > 0:
            fig = px.bar(
                x=list(transport_costs.keys()),
                y=list(transport_costs.values()),
                title="Transportation Costs by Type",
                labels={'x': 'Transportation Type', 'y': 'Cost ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.subheader("📋 Summary")
    
    summary_data = []
    for dest in destinations:
        dest_activities = [a for a in activities if a.get('destination_id') == dest['id']]
        completed_activities = len([a for a in dest_activities if a.get('status') == 'completed'])
        total_activities = len(dest_activities)
        completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        summary_data.append({
            'Destination': f"{dest['name']}, {dest['country']}",
            'Duration (days)': dest.get('duration_days', 0),
            'Budget ($)': f"${dest.get('budget', 0):,.0f}",
            'Activities': f"{completed_activities}/{total_activities}",
            'Completion (%)': f"{completion_rate:.1f}%"
        })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)


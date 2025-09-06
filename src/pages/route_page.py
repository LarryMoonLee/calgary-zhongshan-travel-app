"""
Route Page - Interactive Transportation Management
Allows full editing of flights, trains, buses, and other transportation
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, time
import json

def render(db_manager, trip_id):
    """Render the route page with editable transportation"""
    
    st.header("🗺️ Journey Route & Transportation")
    st.markdown("Manage all your transportation details with full editing capabilities")
    
    # Get current transportation data
    transportation_data = db_manager.get_transportation(trip_id)
    destinations = db_manager.get_destinations(trip_id)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["🚗 Transportation Manager", "🗺️ Route Map", "📊 Journey Statistics"])
    
    with tab1:
        render_transportation_manager(db_manager, trip_id, transportation_data, destinations)
    
    with tab2:
        render_route_map(transportation_data, destinations)
    
    with tab3:
        render_journey_statistics(transportation_data)

def render_transportation_manager(db_manager, trip_id, transportation_data, destinations):
    """Render the transportation management interface"""
    
    st.subheader("✈️ Transportation Management")
    
    # Add new transportation segment
    with st.expander("➕ Add New Transportation Segment", expanded=False):
        add_transportation_form(db_manager, trip_id, destinations)
    
    # Display existing transportation with edit capabilities
    if transportation_data:
        st.subheader("📋 Current Transportation Schedule")
        
        for i, transport in enumerate(transportation_data):
            with st.container():
                st.markdown(f"""
                <div class="edit-section">
                    <h4>🚌 Segment {i+1}: {transport.get('from_destination_name', 'Unknown')} → {transport.get('to_destination_name', 'Unknown')}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Create columns for editing
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    # Transport details
                    transport_type = st.selectbox(
                        "Transport Type",
                        ["flight", "train", "bus", "ferry", "car", "taxi", "walk"],
                        value=transport.get('transport_type', 'flight'),
                        key=f"type_{transport['id']}"
                    )
                    
                    provider = st.text_input(
                        "Provider/Company",
                        value=transport.get('provider', ''),
                        key=f"provider_{transport['id']}"
                    )
                    
                    route_number = st.text_input(
                        "Flight/Train/Route Number",
                        value=transport.get('route_number', ''),
                        key=f"route_{transport['id']}"
                    )
                
                with col2:
                    # Departure details
                    st.write("**Departure**")
                    departure_date = st.date_input(
                        "Date",
                        value=datetime.strptime(transport.get('departure_datetime', '2024-11-08 00:00:00')[:10], '%Y-%m-%d').date() if transport.get('departure_datetime') else date.today(),
                        key=f"dep_date_{transport['id']}"
                    )
                    
                    departure_time = st.time_input(
                        "Time",
                        value=datetime.strptime(transport.get('departure_datetime', '2024-11-08 08:00:00')[11:16], '%H:%M').time() if transport.get('departure_datetime') else time(8, 0),
                        key=f"dep_time_{transport['id']}"
                    )
                    
                    departure_location = st.text_input(
                        "Location",
                        value=transport.get('departure_location', ''),
                        key=f"dep_loc_{transport['id']}"
                    )
                
                with col3:
                    # Arrival details
                    st.write("**Arrival**")
                    arrival_date = st.date_input(
                        "Date",
                        value=datetime.strptime(transport.get('arrival_datetime', '2024-11-08 00:00:00')[:10], '%Y-%m-%d').date() if transport.get('arrival_datetime') else date.today(),
                        key=f"arr_date_{transport['id']}"
                    )
                    
                    arrival_time = st.time_input(
                        "Time",
                        value=datetime.strptime(transport.get('arrival_datetime', '2024-11-08 12:00:00')[11:16], '%H:%M').time() if transport.get('arrival_datetime') else time(12, 0),
                        key=f"arr_time_{transport['id']}"
                    )
                    
                    arrival_location = st.text_input(
                        "Location",
                        value=transport.get('arrival_location', ''),
                        key=f"arr_loc_{transport['id']}"
                    )
                
                with col4:
                    # Action buttons
                    st.write("**Actions**")
                    if st.button("💾 Update", key=f"update_{transport['id']}"):
                        update_transportation_segment(
                            db_manager, transport['id'],
                            transport_type, provider, route_number,
                            departure_date, departure_time, departure_location,
                            arrival_date, arrival_time, arrival_location
                        )
                        st.success("Updated!")
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{transport['id']}"):
                        db_manager.delete_transportation(transport['id'])
                        st.success("Deleted!")
                        st.rerun()
                
                # Additional details in expandable section
                with st.expander(f"📝 Additional Details for Segment {i+1}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        cost = st.number_input(
                            "Cost ($)",
                            value=float(transport.get('cost', 0)),
                            min_value=0.0,
                            key=f"cost_{transport['id']}"
                        )
                        
                        class_type = st.selectbox(
                            "Class",
                            ["economy", "premium economy", "business", "first"],
                            value=transport.get('class_type', 'economy'),
                            key=f"class_{transport['id']}"
                        )
                    
                    with col2:
                        booking_reference = st.text_input(
                            "Booking Reference",
                            value=transport.get('booking_reference', ''),
                            key=f"booking_{transport['id']}"
                        )
                        
                        seat_number = st.text_input(
                            "Seat Number",
                            value=transport.get('seat_number', ''),
                            key=f"seat_{transport['id']}"
                        )
                    
                    with col3:
                        is_standby = st.checkbox(
                            "Standby Flight",
                            value=bool(transport.get('is_standby', False)),
                            key=f"standby_{transport['id']}"
                        )
                        
                        status = st.selectbox(
                            "Status",
                            ["planned", "booked", "completed", "cancelled"],
                            value=transport.get('status', 'planned'),
                            key=f"status_{transport['id']}"
                        )
                    
                    notes = st.text_area(
                        "Notes",
                        value=transport.get('notes', ''),
                        key=f"notes_{transport['id']}"
                    )
                    
                    if st.button("💾 Update Details", key=f"update_details_{transport['id']}"):
                        db_manager.update_transportation(
                            transport['id'],
                            cost=cost,
                            class_type=class_type,
                            booking_reference=booking_reference,
                            seat_number=seat_number,
                            is_standby=is_standby,
                            status=status,
                            notes=notes
                        )
                        st.success("Details updated!")
                        st.rerun()
                
                st.divider()
    else:
        st.info("No transportation segments added yet. Use the form above to add your first segment.")

def add_transportation_form(db_manager, trip_id, destinations):
    """Form to add new transportation segment"""
    
    with st.form("add_transportation"):
        st.subheader("Add New Transportation Segment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic transport info
            transport_type = st.selectbox(
                "Transportation Type",
                ["flight", "train", "bus", "ferry", "car", "taxi", "walk"]
            )
            
            provider = st.text_input("Provider/Company (e.g., WestJet, China Railways)")
            route_number = st.text_input("Flight/Train/Route Number")
            
            # Departure
            st.subheader("Departure")
            departure_date = st.date_input("Departure Date")
            departure_time = st.time_input("Departure Time")
            departure_location = st.text_input("Departure Location")
        
        with col2:
            # Cost and class
            cost = st.number_input("Cost ($)", min_value=0.0, value=0.0)
            class_type = st.selectbox("Class", ["economy", "premium economy", "business", "first"])
            
            # Arrival
            st.subheader("Arrival")
            arrival_date = st.date_input("Arrival Date")
            arrival_time = st.time_input("Arrival Time")
            arrival_location = st.text_input("Arrival Location")
        
        # Additional options
        col3, col4 = st.columns(2)
        with col3:
            booking_reference = st.text_input("Booking Reference")
            seat_number = st.text_input("Seat Number")
        
        with col4:
            is_standby = st.checkbox("Standby Flight")
            status = st.selectbox("Status", ["planned", "booked", "completed", "cancelled"])
        
        notes = st.text_area("Additional Notes")
        
        if st.form_submit_button("➕ Add Transportation Segment"):
            # Combine date and time
            departure_datetime = datetime.combine(departure_date, departure_time)
            arrival_datetime = datetime.combine(arrival_date, arrival_time)
            
            # Calculate duration
            duration_minutes = int((arrival_datetime - departure_datetime).total_seconds() / 60)
            
            transport_id = db_manager.add_transportation(
                trip_id=trip_id,
                transport_type=transport_type,
                provider=provider,
                route_number=route_number,
                departure_datetime=departure_datetime,
                arrival_datetime=arrival_datetime,
                departure_location=departure_location,
                arrival_location=arrival_location,
                duration_minutes=duration_minutes,
                cost=cost,
                class_type=class_type,
                booking_reference=booking_reference,
                seat_number=seat_number,
                is_standby=is_standby,
                status=status,
                notes=notes
            )
            
            st.success(f"Transportation segment added successfully! ID: {transport_id}")
            st.rerun()

def update_transportation_segment(db_manager, transport_id, transport_type, provider, route_number,
                                departure_date, departure_time, departure_location,
                                arrival_date, arrival_time, arrival_location):
    """Update transportation segment with new details"""
    
    departure_datetime = datetime.combine(departure_date, departure_time)
    arrival_datetime = datetime.combine(arrival_date, arrival_time)
    duration_minutes = int((arrival_datetime - departure_datetime).total_seconds() / 60)
    
    db_manager.update_transportation(
        transport_id,
        transport_type=transport_type,
        provider=provider,
        route_number=route_number,
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime,
        departure_location=departure_location,
        arrival_location=arrival_location,
        duration_minutes=duration_minutes
    )

def render_route_map(transportation_data, destinations):
    """Render interactive route map"""
    
    st.subheader("🗺️ Interactive Journey Map")
    
    if not transportation_data:
        st.info("Add transportation segments to see your route map.")
        return
    
    # Create route visualization
    fig = go.Figure()
    
    # Define colors for different transport types
    transport_colors = {
        'flight': '#FF6B6B',
        'train': '#4ECDC4',
        'bus': '#45B7D1',
        'ferry': '#96CEB4',
        'car': '#FFEAA7',
        'taxi': '#DDA0DD',
        'walk': '#98D8C8'
    }
    
    # Add route segments
    for i, transport in enumerate(transportation_data):
        color = transport_colors.get(transport.get('transport_type', 'flight'), '#666666')
        
        # Create route line (simplified - in real app you'd use actual coordinates)
        fig.add_trace(go.Scatter(
            x=[i, i+1],
            y=[1, 1],
            mode='lines+markers',
            name=f"{transport.get('transport_type', 'Unknown').title()}: {transport.get('from_destination_name', 'Unknown')} → {transport.get('to_destination_name', 'Unknown')}",
            line=dict(color=color, width=4),
            marker=dict(size=10, color=color),
            hovertemplate=f"""
            <b>{transport.get('transport_type', 'Unknown').title()}</b><br>
            From: {transport.get('departure_location', 'Unknown')}<br>
            To: {transport.get('arrival_location', 'Unknown')}<br>
            Provider: {transport.get('provider', 'Unknown')}<br>
            Route: {transport.get('route_number', 'N/A')}<br>
            Cost: ${transport.get('cost', 0)}<br>
            Status: {transport.get('status', 'Unknown')}<br>
            <extra></extra>
            """
        ))
    
    fig.update_layout(
        title="Journey Route Overview",
        xaxis_title="Journey Progression",
        yaxis_title="",
        height=400,
        showlegend=True,
        yaxis=dict(showticklabels=False),
        xaxis=dict(showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Transportation legend
    st.subheader("🚦 Transportation Types")
    
    cols = st.columns(len(transport_colors))
    for i, (transport_type, color) in enumerate(transport_colors.items()):
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background-color: {color}; border-radius: 3px; margin-right: 10px;"></div>
                <span>{transport_type.title()}</span>
            </div>
            """, unsafe_allow_html=True)

def render_journey_statistics(transportation_data):
    """Render journey statistics and analytics"""
    
    st.subheader("📊 Journey Analytics")
    
    if not transportation_data:
        st.info("Add transportation segments to see statistics.")
        return
    
    # Calculate statistics
    total_cost = sum(float(t.get('cost', 0)) for t in transportation_data)
    total_segments = len(transportation_data)
    
    # Transport type breakdown
    transport_counts = {}
    for transport in transportation_data:
        t_type = transport.get('transport_type', 'unknown')
        transport_counts[t_type] = transport_counts.get(t_type, 0) + 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Segments", total_segments)
    
    with col2:
        st.metric("Total Transport Cost", f"${total_cost:,.0f}")
    
    with col3:
        avg_cost = total_cost / total_segments if total_segments > 0 else 0
        st.metric("Average Cost per Segment", f"${avg_cost:,.0f}")
    
    with col4:
        unique_types = len(transport_counts)
        st.metric("Transport Types Used", unique_types)
    
    # Transport type pie chart
    if transport_counts:
        fig = px.pie(
            values=list(transport_counts.values()),
            names=list(transport_counts.keys()),
            title="Transportation Methods Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost breakdown by transport type
    cost_by_type = {}
    for transport in transportation_data:
        t_type = transport.get('transport_type', 'unknown')
        cost = float(transport.get('cost', 0))
        cost_by_type[t_type] = cost_by_type.get(t_type, 0) + cost
    
    if cost_by_type:
        fig = px.bar(
            x=list(cost_by_type.keys()),
            y=list(cost_by_type.values()),
            title="Cost Breakdown by Transportation Type",
            labels={'x': 'Transportation Type', 'y': 'Total Cost ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed transportation table
    st.subheader("📋 Transportation Summary Table")
    
    if transportation_data:
        df = pd.DataFrame(transportation_data)
        
        # Select relevant columns for display
        display_columns = [
            'transport_type', 'provider', 'route_number',
            'departure_location', 'arrival_location',
            'departure_datetime', 'arrival_datetime',
            'cost', 'status'
        ]
        
        # Filter to only existing columns
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            display_df = df[available_columns].copy()
            
            # Format datetime columns
            for col in ['departure_datetime', 'arrival_datetime']:
                if col in display_df.columns:
                    display_df[col] = pd.to_datetime(display_df[col]).dt.strftime('%Y-%m-%d %H:%M')
            
            # Format cost column
            if 'cost' in display_df.columns:
                display_df['cost'] = display_df['cost'].apply(lambda x: f"${float(x):,.0f}")
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No data available to display in table format.")
    
    # Export transportation data
    st.subheader("📤 Export Transportation Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as CSV"):
            df = pd.DataFrame(transportation_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transportation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Export as Excel"):
            df = pd.DataFrame(transportation_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Transportation', index=False)
            
            st.download_button(
                label="Download Excel",
                data=output.getvalue(),
                file_name=f"transportation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if st.button("📋 Export as JSON"):
            json_data = json.dumps(transportation_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"transportation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


"""
Itinerary Page - Visual Timeline and Schedule Management
Interactive timeline with editable dates and times
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta

def render(db_manager, trip_id):
    """Render the itinerary page with timeline visualization"""
    
    st.header("📅 Journey Itinerary")
    st.markdown("Visual timeline of your complete journey with editable dates and times")
    
    # Get trip data
    trip = db_manager.get_trip(trip_id)
    destinations = db_manager.get_destinations(trip_id)
    activities = db_manager.get_activities(trip_id)
    transportation = db_manager.get_transportation(trip_id)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📅 Visual Timeline", 
        "📋 Daily Schedule", 
        "⏰ Time Management"
    ])
    
    with tab1:
        render_visual_timeline(db_manager, trip_id, trip, destinations, activities, transportation)
    
    with tab2:
        render_daily_schedule(db_manager, trip_id, destinations, activities)
    
    with tab3:
        render_time_management(db_manager, trip_id, destinations, activities, transportation)

def render_visual_timeline(db_manager, trip_id, trip, destinations, activities, transportation):
    """Render visual timeline of the journey"""
    
    st.subheader("📅 Journey Timeline")
    
    if not destinations:
        st.info("Add destinations to see your timeline.")
        return
    
    # Create timeline data
    timeline_data = []
    
    # Add destinations to timeline
    for dest in destinations:
        if dest.get('arrival_date') and dest.get('departure_date'):
            timeline_data.append({
                'Task': f"{dest['name']}, {dest['country']}",
                'Start': dest['arrival_date'],
                'Finish': dest['departure_date'],
                'Type': 'Destination',
                'Resource': dest['name']
            })
    
    # Add transportation to timeline
    for transport in transportation:
        if transport.get('departure_datetime'):
            dep_date = transport['departure_datetime'][:10]  # Extract date part
            timeline_data.append({
                'Task': f"{transport.get('transport_type', 'Transport').title()}: {transport.get('from_destination_name', 'Unknown')} → {transport.get('to_destination_name', 'Unknown')}",
                'Start': dep_date,
                'Finish': dep_date,
                'Type': 'Transportation',
                'Resource': transport.get('transport_type', 'transport')
            })
    
    if timeline_data:
        # Create Gantt chart
        df = pd.DataFrame(timeline_data)
        
        # Color mapping
        color_map = {
            'Destination': '#3498db',
            'Transportation': '#e74c3c'
        }
        
        fig = px.timeline(
            df, 
            x_start="Start", 
            x_end="Finish", 
            y="Task",
            color="Type",
            color_discrete_map=color_map,
            title="Journey Timeline"
        )
        
        fig.update_layout(
            height=max(400, len(timeline_data) * 40),
            xaxis_title="Date",
            yaxis_title="Journey Segments"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Journey overview cards
    st.subheader("🗺️ Journey Overview")
    
    for i, dest in enumerate(destinations):
        with st.container():
            st.markdown(f"""
            <div class="edit-section">
                <h4>📍 Segment {i+1}: {dest['name']}, {dest['country']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**Duration:** {dest.get('duration_days', 'N/A')} days")
                st.write(f"**Dates:** {dest.get('arrival_date', 'N/A')} to {dest.get('departure_date', 'N/A')}")
                if dest.get('description'):
                    st.caption(dest['description'][:100] + "..." if len(dest.get('description', '')) > 100 else dest.get('description', ''))
            
            with col2:
                st.metric("Budget", f"${dest.get('budget', 0):,.0f}")
            
            with col3:
                dest_activities = [a for a in activities if a.get('destination_id') == dest['id']]
                completed = len([a for a in dest_activities if a.get('status') == 'completed'])
                total = len(dest_activities)
                st.metric("Activities", f"{completed}/{total}")
            
            with col4:
                if st.button("✏️ Edit Dates", key=f"edit_dates_{dest['id']}"):
                    st.session_state[f"edit_dates_{dest['id']}"] = True
            
            # Edit dates form
            if st.session_state.get(f"edit_dates_{dest['id']}", False):
                with st.form(f"edit_dates_form_{dest['id']}"):
                    st.subheader(f"Edit Dates for {dest['name']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_arrival = st.date_input(
                            "Arrival Date",
                            value=datetime.strptime(dest.get('arrival_date', '2024-11-08'), '%Y-%m-%d').date() if dest.get('arrival_date') else date.today()
                        )
                    
                    with col2:
                        new_departure = st.date_input(
                            "Departure Date",
                            value=datetime.strptime(dest.get('departure_date', '2024-11-11'), '%Y-%m-%d').date() if dest.get('departure_date') else date.today()
                        )
                    
                    with col3:
                        new_duration = (new_departure - new_arrival).days + 1
                        st.metric("Duration", f"{new_duration} days")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            db_manager.update_destination(
                                dest['id'],
                                arrival_date=new_arrival,
                                departure_date=new_departure,
                                duration_days=new_duration
                            )
                            st.success("Dates updated!")
                            st.session_state[f"edit_dates_{dest['id']}"] = False
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state[f"edit_dates_{dest['id']}"] = False
                            st.rerun()
            
            st.divider()

def render_daily_schedule(db_manager, trip_id, destinations, activities):
    """Render daily schedule view"""
    
    st.subheader("📋 Daily Schedule")
    
    if not destinations:
        st.info("Add destinations to see daily schedules.")
        return
    
    # Date selector
    if destinations:
        start_date = min(datetime.strptime(dest.get('arrival_date', '2024-11-08'), '%Y-%m-%d').date() for dest in destinations if dest.get('arrival_date'))
        end_date = max(datetime.strptime(dest.get('departure_date', '2024-12-28'), '%Y-%m-%d').date() for dest in destinations if dest.get('departure_date'))
        
        selected_date = st.date_input(
            "Select Date",
            value=start_date,
            min_value=start_date,
            max_value=end_date
        )
        
        # Find destination for selected date
        current_destination = None
        for dest in destinations:
            if dest.get('arrival_date') and dest.get('departure_date'):
                arrival = datetime.strptime(dest['arrival_date'], '%Y-%m-%d').date()
                departure = datetime.strptime(dest['departure_date'], '%Y-%m-%d').date()
                if arrival <= selected_date <= departure:
                    current_destination = dest
                    break
        
        if current_destination:
            st.markdown(f"""
            <div class="edit-section">
                <h4>📍 {selected_date.strftime('%A, %B %d, %Y')} - {current_destination['name']}, {current_destination['country']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Get activities for this date and destination
            date_activities = [
                a for a in activities 
                if a.get('destination_id') == current_destination['id'] and 
                a.get('planned_date') == selected_date.strftime('%Y-%m-%d')
            ]
            
            # Sort activities by time
            date_activities.sort(key=lambda x: x.get('planned_time', '00:00:00'))
            
            # Add new activity for this date
            with st.expander("➕ Add Activity for This Date"):
                with st.form(f"add_activity_date_{selected_date}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        activity_title = st.text_input("Activity Title")
                        activity_time = st.time_input("Time", value=time(9, 0))
                        duration = st.number_input("Duration (minutes)", value=120, min_value=0)
                    
                    with col2:
                        activity_location = st.text_input("Location")
                        activity_cost = st.number_input("Cost ($)", value=0.0, min_value=0.0)
                        priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: ["Low", "Medium", "High"][x-1])
                    
                    description = st.text_area("Description")
                    
                    if st.form_submit_button("➕ Add Activity"):
                        if activity_title:
                            db_manager.add_activity(
                                trip_id=trip_id,
                                destination_id=current_destination['id'],
                                title=activity_title,
                                description=description,
                                planned_date=selected_date,
                                planned_time=activity_time,
                                duration_minutes=duration,
                                cost=activity_cost,
                                priority=priority,
                                location=activity_location
                            )
                            st.success("Activity added!")
                            st.rerun()
            
            # Display activities for this date
            if date_activities:
                st.subheader(f"📅 Schedule for {selected_date.strftime('%B %d')}")
                
                for activity in date_activities:
                    start_time = datetime.strptime(activity.get('planned_time', '09:00:00'), '%H:%M:%S').time()
                    duration_min = activity.get('duration_minutes', 60)
                    end_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=duration_min)).time()
                    
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(activity.get('status', 'pending'), '⚪')
                        st.write(f"{status_icon} **{activity['title']}**")
                        if activity.get('location'):
                            st.caption(f"📍 {activity['location']}")
                        if activity.get('description'):
                            st.caption(activity['description'][:80] + "..." if len(activity.get('description', '')) > 80 else activity.get('description', ''))
                    
                    with col2:
                        st.write(f"🕐 {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                        st.caption(f"{duration_min} minutes")
                    
                    with col3:
                        if activity.get('cost', 0) > 0:
                            st.write(f"💰 ${activity['cost']:,.0f}")
                        priority_colors = {1: "🟢", 2: "🟡", 3: "🔴"}
                        st.caption(f"{priority_colors.get(activity.get('priority', 1), '⚪')} Priority")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_schedule_{activity['id']}"):
                            st.session_state[f"edit_schedule_{activity['id']}"] = True
                    
                    # Quick edit form
                    if st.session_state.get(f"edit_schedule_{activity['id']}", False):
                        with st.form(f"edit_schedule_form_{activity['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_time = st.time_input("Time", value=start_time)
                                new_duration = st.number_input("Duration (min)", value=duration_min, min_value=0)
                            
                            with col2:
                                new_status = st.selectbox("Status", ["pending", "in_progress", "completed", "cancelled"], value=activity.get('status', 'pending'))
                                new_cost = st.number_input("Cost ($)", value=float(activity.get('cost', 0)), min_value=0.0)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("💾 Update"):
                                    db_manager.update_activity(
                                        activity['id'],
                                        planned_time=new_time,
                                        duration_minutes=new_duration,
                                        status=new_status,
                                        cost=new_cost
                                    )
                                    st.success("Activity updated!")
                                    st.session_state[f"edit_schedule_{activity['id']}"] = False
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"edit_schedule_{activity['id']}"] = False
                                    st.rerun()
                    
                    st.divider()
            else:
                st.info(f"No activities scheduled for {selected_date.strftime('%B %d, %Y')}. Add some activities above!")
        else:
            st.info(f"No destination scheduled for {selected_date.strftime('%B %d, %Y')}.")

def render_time_management(db_manager, trip_id, destinations, activities, transportation):
    """Render time management and scheduling tools"""
    
    st.subheader("⏰ Time Management")
    
    # Time zone information
    st.subheader("🌍 Time Zones")
    
    time_zones = {
        "Calgary": "MST (UTC-7)",
        "Tokyo": "JST (UTC+9)",
        "Hong Kong": "HKT (UTC+8)",
        "Shenzhen": "CST (UTC+8)",
        "Zhongshan": "CST (UTC+8)",
        "Jinan": "CST (UTC+8)",
        "Beijing": "CST (UTC+8)"
    }
    
    cols = st.columns(len(time_zones))
    for i, (city, tz) in enumerate(time_zones.items()):
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div class="metric-card">
                <h5>{city}</h5>
                <p>{tz}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Schedule conflicts detection
    st.subheader("⚠️ Schedule Analysis")
    
    conflicts = []
    
    # Check for overlapping activities
    for dest in destinations:
        dest_activities = [a for a in activities if a.get('destination_id') == dest['id'] and a.get('planned_date') and a.get('planned_time')]
        
        for i, activity1 in enumerate(dest_activities):
            for activity2 in dest_activities[i+1:]:
                if activity1.get('planned_date') == activity2.get('planned_date'):
                    time1 = datetime.strptime(activity1['planned_time'], '%H:%M:%S').time()
                    time2 = datetime.strptime(activity2['planned_time'], '%H:%M:%S').time()
                    
                    duration1 = activity1.get('duration_minutes', 60)
                    end_time1 = (datetime.combine(date.today(), time1) + timedelta(minutes=duration1)).time()
                    
                    if time1 <= time2 <= end_time1:
                        conflicts.append({
                            'date': activity1['planned_date'],
                            'activity1': activity1['title'],
                            'activity2': activity2['title'],
                            'destination': dest['name']
                        })
    
    if conflicts:
        st.warning(f"⚠️ {len(conflicts)} schedule conflicts detected:")
        for conflict in conflicts:
            st.write(f"• **{conflict['date']}** in {conflict['destination']}: '{conflict['activity1']}' overlaps with '{conflict['activity2']}'")
    else:
        st.success("✅ No schedule conflicts detected!")
    
    # Travel time calculator
    st.subheader("🚗 Travel Time Calculator")
    
    if transportation:
        st.write("**Transportation Schedule:**")
        
        for transport in transportation:
            if transport.get('departure_datetime') and transport.get('arrival_datetime'):
                dep_dt = datetime.strptime(transport['departure_datetime'], '%Y-%m-%d %H:%M:%S')
                arr_dt = datetime.strptime(transport['arrival_datetime'], '%Y-%m-%d %H:%M:%S')
                duration = arr_dt - dep_dt
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**{transport.get('transport_type', 'Transport').title()}**")
                    st.caption(f"{transport.get('from_destination_name', 'Unknown')} → {transport.get('to_destination_name', 'Unknown')}")
                
                with col2:
                    st.write(f"🕐 {dep_dt.strftime('%Y-%m-%d %H:%M')}")
                    st.caption(f"to {arr_dt.strftime('%Y-%m-%d %H:%M')}")
                
                with col3:
                    hours = duration.total_seconds() / 3600
                    st.write(f"⏱️ {hours:.1f} hours")
                    if transport.get('cost'):
                        st.caption(f"💰 ${transport['cost']:,.0f}")
    
    # Daily schedule summary
    st.subheader("📊 Schedule Summary")
    
    if activities:
        # Group activities by date
        activities_by_date = {}
        for activity in activities:
            if activity.get('planned_date'):
                date_key = activity['planned_date']
                if date_key not in activities_by_date:
                    activities_by_date[date_key] = []
                activities_by_date[date_key].append(activity)
        
        # Create summary chart
        dates = []
        activity_counts = []
        total_durations = []
        
        for date_str, date_activities in sorted(activities_by_date.items()):
            dates.append(date_str)
            activity_counts.append(len(date_activities))
            total_duration = sum(a.get('duration_minutes', 60) for a in date_activities)
            total_durations.append(total_duration / 60)  # Convert to hours
        
        if dates:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=dates,
                y=activity_counts,
                name='Number of Activities',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=total_durations,
                mode='lines+markers',
                name='Total Hours',
                yaxis='y2',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title='Daily Activity Schedule',
                xaxis_title='Date',
                yaxis=dict(title='Number of Activities', side='left'),
                yaxis2=dict(title='Total Hours', side='right', overlaying='y'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Export schedule
    st.subheader("📤 Export Schedule")
    
    if st.button("📅 Export Complete Schedule"):
        schedule_data = []
        
        for activity in activities:
            if activity.get('planned_date'):
                dest_name = "Unknown"
                for dest in destinations:
                    if dest['id'] == activity.get('destination_id'):
                        dest_name = dest['name']
                        break
                
                schedule_data.append({
                    'Date': activity['planned_date'],
                    'Time': activity.get('planned_time', ''),
                    'Activity': activity['title'],
                    'Destination': dest_name,
                    'Duration (min)': activity.get('duration_minutes', 0),
                    'Cost ($)': activity.get('cost', 0),
                    'Status': activity.get('status', 'pending'),
                    'Location': activity.get('location', ''),
                    'Notes': activity.get('description', '')
                })
        
        if schedule_data:
            df = pd.DataFrame(schedule_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Schedule CSV",
                data=csv,
                file_name=f"complete_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No scheduled activities to export.")


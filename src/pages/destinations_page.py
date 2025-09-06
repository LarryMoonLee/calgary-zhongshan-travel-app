"""
Destinations Page - Comprehensive Note-Taking and Todo Management
Allows full editing of notes, activities, and todo lists for each destination
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import json

def render(db_manager, trip_id):
    """Render the destinations page with note-taking and todo functionality"""
    
    st.header("📍 Destinations & Activities")
    st.markdown("Manage your notes, activities, and todo lists for each destination")
    
    # Get destinations
    destinations = db_manager.get_destinations(trip_id)
    
    if not destinations:
        st.info("No destinations added yet. Add destinations in the Journey tab first.")
        return
    
    # Destination selector
    dest_names = [f"{dest['name']}, {dest['country']}" for dest in destinations]
    selected_dest_idx = st.selectbox(
        "Select Destination",
        range(len(destinations)),
        format_func=lambda x: dest_names[x]
    )
    
    selected_dest = destinations[selected_dest_idx]
    
    # Create tabs for different functionality
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Notes & Information", 
        "✅ Todo List & Activities", 
        "📋 Activity Manager", 
        "📊 Progress Overview"
    ])
    
    with tab1:
        render_notes_section(db_manager, selected_dest)
    
    with tab2:
        render_todo_list(db_manager, trip_id, selected_dest)
    
    with tab3:
        render_activity_manager(db_manager, trip_id, selected_dest)
    
    with tab4:
        render_progress_overview(db_manager, trip_id, selected_dest)

def render_notes_section(db_manager, destination):
    """Render the notes and information section"""
    
    st.subheader(f"📝 Notes for {destination['name']}")
    
    # Destination overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="edit-section">
            <h4>🏙️ {destination['name']}, {destination['country']}</h4>
            <p><strong>Duration:</strong> {destination.get('duration_days', 'N/A')} days</p>
            <p><strong>Dates:</strong> {destination.get('arrival_date', 'N/A')} to {destination.get('departure_date', 'N/A')}</p>
            <p><strong>Budget:</strong> ${destination.get('budget', 0):,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Quick edit destination info
        if st.button("✏️ Edit Destination Info"):
            st.session_state[f"edit_dest_{destination['id']}"] = True
    
    # Edit destination form
    if st.session_state.get(f"edit_dest_{destination['id']}", False):
        with st.form(f"edit_destination_{destination['id']}"):
            st.subheader("Edit Destination Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Destination Name", value=destination.get('name', ''))
                new_country = st.text_input("Country", value=destination.get('country', ''))
                new_arrival = st.date_input(
                    "Arrival Date", 
                    value=datetime.strptime(destination.get('arrival_date', '2024-11-08'), '%Y-%m-%d').date() if destination.get('arrival_date') else date.today()
                )
                new_departure = st.date_input(
                    "Departure Date", 
                    value=datetime.strptime(destination.get('departure_date', '2024-11-11'), '%Y-%m-%d').date() if destination.get('departure_date') else date.today()
                )
            
            with col2:
                new_budget = st.number_input("Budget ($)", value=float(destination.get('budget', 0)), min_value=0.0)
                new_duration = st.number_input("Duration (days)", value=int(destination.get('duration_days', 1)), min_value=1)
                new_weather = st.text_input("Weather Info", value=destination.get('weather', ''))
                new_accommodation = st.text_input("Accommodation", value=destination.get('accommodation', ''))
            
            new_description = st.text_area("Description", value=destination.get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    db_manager.update_destination(
                        destination['id'],
                        name=new_name,
                        country=new_country,
                        arrival_date=new_arrival,
                        departure_date=new_departure,
                        duration_days=new_duration,
                        budget=new_budget,
                        weather=new_weather,
                        accommodation=new_accommodation,
                        description=new_description
                    )
                    st.success("Destination updated successfully!")
                    st.session_state[f"edit_dest_{destination['id']}"] = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state[f"edit_dest_{destination['id']}"] = False
                    st.rerun()
    
    # Personal Notes Section
    st.subheader("📖 Personal Notes")
    
    # Get or create notes (stored in description field for now, could be separate table)
    current_notes = destination.get('description', '')
    
    # Notes editor
    notes = st.text_area(
        "Write your personal notes about this destination...",
        value=current_notes,
        height=200,
        help="Add your thoughts, observations, tips, or any other notes about this destination"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Notes"):
            db_manager.update_destination(destination['id'], description=notes)
            st.success("Notes saved!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Notes"):
            db_manager.update_destination(destination['id'], description='')
            st.success("Notes cleared!")
            st.rerun()
    
    # Highlights and Tips
    st.subheader("⭐ Highlights & Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Must-See Highlights**")
        highlights = destination.get('highlights', '[]')
        try:
            highlights_list = json.loads(highlights) if highlights else []
        except:
            highlights_list = []
        
        # Edit highlights
        new_highlight = st.text_input("Add new highlight", key=f"highlight_{destination['id']}")
        if st.button("➕ Add Highlight", key=f"add_highlight_{destination['id']}"):
            if new_highlight:
                highlights_list.append(new_highlight)
                db_manager.update_destination(destination['id'], highlights=json.dumps(highlights_list))
                st.rerun()
        
        # Display and manage highlights
        for i, highlight in enumerate(highlights_list):
            col_text, col_delete = st.columns([4, 1])
            with col_text:
                st.write(f"• {highlight}")
            with col_delete:
                if st.button("🗑️", key=f"del_highlight_{destination['id']}_{i}"):
                    highlights_list.pop(i)
                    db_manager.update_destination(destination['id'], highlights=json.dumps(highlights_list))
                    st.rerun()
    
    with col2:
        st.write("**Travel Tips**")
        tips = destination.get('tips', '[]')
        try:
            tips_list = json.loads(tips) if tips else []
        except:
            tips_list = []
        
        # Edit tips
        new_tip = st.text_input("Add new tip", key=f"tip_{destination['id']}")
        if st.button("➕ Add Tip", key=f"add_tip_{destination['id']}"):
            if new_tip:
                tips_list.append(new_tip)
                db_manager.update_destination(destination['id'], tips=json.dumps(tips_list))
                st.rerun()
        
        # Display and manage tips
        for i, tip in enumerate(tips_list):
            col_text, col_delete = st.columns([4, 1])
            with col_text:
                st.write(f"💡 {tip}")
            with col_delete:
                if st.button("🗑️", key=f"del_tip_{destination['id']}_{i}"):
                    tips_list.pop(i)
                    db_manager.update_destination(destination['id'], tips=json.dumps(tips_list))
                    st.rerun()

def render_todo_list(db_manager, trip_id, destination):
    """Render the todo list and activities section"""
    
    st.subheader(f"✅ Todo List for {destination['name']}")
    
    # Get activities for this destination
    activities = db_manager.get_activities(trip_id, destination['id'])
    
    # Quick add activity
    with st.form(f"quick_add_{destination['id']}"):
        st.write("**Quick Add Activity**")
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            quick_title = st.text_input("Activity", placeholder="e.g., Visit Tokyo Skytree")
        
        with col2:
            quick_priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: ["Low", "Medium", "High"][x-1])
        
        with col3:
            if st.form_submit_button("➕ Add"):
                if quick_title:
                    db_manager.add_activity(
                        trip_id=trip_id,
                        destination_id=destination['id'],
                        title=quick_title,
                        priority=quick_priority,
                        status='pending'
                    )
                    st.success("Activity added!")
                    st.rerun()
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "in_progress", "completed", "cancelled"]
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "High (3)", "Medium (2)", "Low (1)"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Priority", "Date", "Status", "Title"]
        )
    
    # Filter activities
    filtered_activities = activities.copy()
    
    if status_filter != "All":
        filtered_activities = [a for a in filtered_activities if a.get('status') == status_filter]
    
    if priority_filter != "All":
        priority_num = int(priority_filter.split('(')[1].split(')')[0])
        filtered_activities = [a for a in filtered_activities if a.get('priority') == priority_num]
    
    # Sort activities
    if sort_by == "Priority":
        filtered_activities.sort(key=lambda x: x.get('priority', 1), reverse=True)
    elif sort_by == "Date":
        filtered_activities.sort(key=lambda x: x.get('planned_date', '9999-12-31'))
    elif sort_by == "Status":
        filtered_activities.sort(key=lambda x: x.get('status', 'pending'))
    elif sort_by == "Title":
        filtered_activities.sort(key=lambda x: x.get('title', ''))
    
    # Display activities
    if filtered_activities:
        st.write(f"**{len(filtered_activities)} activities found**")
        
        for activity in filtered_activities:
            with st.container():
                # Activity card
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # Checkbox for completion
                    is_completed = activity.get('status') == 'completed'
                    completed = st.checkbox(
                        activity.get('title', 'Untitled'),
                        value=is_completed,
                        key=f"complete_{activity['id']}"
                    )
                    
                    if completed != is_completed:
                        new_status = 'completed' if completed else 'pending'
                        db_manager.update_activity(activity['id'], status=new_status)
                        st.rerun()
                    
                    # Show description if available
                    if activity.get('description'):
                        st.caption(activity['description'])
                
                with col2:
                    # Priority indicator
                    priority = activity.get('priority', 1)
                    priority_colors = {1: "🟢", 2: "🟡", 3: "🔴"}
                    priority_labels = {1: "Low", 2: "Medium", 3: "High"}
                    st.write(f"{priority_colors.get(priority, '⚪')} {priority_labels.get(priority, 'Unknown')}")
                
                with col3:
                    # Status
                    status = activity.get('status', 'pending')
                    status_colors = {
                        'pending': '⏳',
                        'in_progress': '🔄',
                        'completed': '✅',
                        'cancelled': '❌'
                    }
                    st.write(f"{status_colors.get(status, '⚪')} {status.title()}")
                
                with col4:
                    # Edit button
                    if st.button("✏️", key=f"edit_activity_{activity['id']}"):
                        st.session_state[f"edit_activity_{activity['id']}"] = True
                
                # Edit form
                if st.session_state.get(f"edit_activity_{activity['id']}", False):
                    with st.form(f"edit_activity_form_{activity['id']}"):
                        st.subheader(f"Edit: {activity.get('title', 'Activity')}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_title = st.text_input("Title", value=activity.get('title', ''))
                            new_description = st.text_area("Description", value=activity.get('description', ''))
                            new_location = st.text_input("Location", value=activity.get('location', ''))
                            new_cost = st.number_input("Cost ($)", value=float(activity.get('cost', 0)), min_value=0.0)
                        
                        with col2:
                            new_planned_date = st.date_input(
                                "Planned Date",
                                value=datetime.strptime(activity.get('planned_date', '2024-11-08'), '%Y-%m-%d').date() if activity.get('planned_date') else None
                            )
                            new_planned_time = st.time_input(
                                "Planned Time",
                                value=datetime.strptime(activity.get('planned_time', '09:00:00'), '%H:%M:%S').time() if activity.get('planned_time') else None
                            )
                            new_duration = st.number_input("Duration (minutes)", value=int(activity.get('duration_minutes', 60)), min_value=0)
                            new_priority = st.selectbox("Priority", [1, 2, 3], value=activity.get('priority', 1), format_func=lambda x: ["Low", "Medium", "High"][x-1])
                        
                        new_status = st.selectbox("Status", ["pending", "in_progress", "completed", "cancelled"], value=activity.get('status', 'pending'))
                        new_category = st.text_input("Category", value=activity.get('category', ''))
                        new_notes = st.text_area("Notes", value=activity.get('notes', ''))
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                db_manager.update_activity(
                                    activity['id'],
                                    title=new_title,
                                    description=new_description,
                                    location=new_location,
                                    cost=new_cost,
                                    planned_date=new_planned_date,
                                    planned_time=new_planned_time,
                                    duration_minutes=new_duration,
                                    priority=new_priority,
                                    status=new_status,
                                    category=new_category,
                                    notes=new_notes
                                )
                                st.success("Activity updated!")
                                st.session_state[f"edit_activity_{activity['id']}"] = False
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete"):
                                db_manager.delete_activity(activity['id'])
                                st.success("Activity deleted!")
                                st.session_state[f"edit_activity_{activity['id']}"] = False
                                st.rerun()
                        
                        with col3:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_activity_{activity['id']}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No activities found. Add some activities to get started!")

def render_activity_manager(db_manager, trip_id, destination):
    """Render the comprehensive activity manager"""
    
    st.subheader(f"📋 Activity Manager for {destination['name']}")
    
    # Add new activity form
    with st.expander("➕ Add New Activity", expanded=False):
        with st.form(f"add_activity_{destination['id']}"):
            st.subheader("Add New Activity")
            
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Activity Title*", placeholder="e.g., Visit Meiji Shrine")
                description = st.text_area("Description", placeholder="Detailed description of the activity...")
                location = st.text_input("Location", placeholder="Specific location or address")
                category = st.selectbox("Category", [
                    "Sightseeing", "Dining", "Shopping", "Transportation", 
                    "Entertainment", "Cultural", "Nature", "Sports", "Other"
                ])
            
            with col2:
                planned_date = st.date_input("Planned Date")
                planned_time = st.time_input("Planned Time")
                duration = st.number_input("Duration (minutes)", value=120, min_value=0)
                cost = st.number_input("Estimated Cost ($)", value=0.0, min_value=0.0)
                priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: ["Low", "Medium", "High"][x-1])
            
            booking_required = st.checkbox("Booking Required")
            booking_reference = st.text_input("Booking Reference") if booking_required else ""
            contact_info = st.text_input("Contact Information")
            notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("➕ Add Activity"):
                if title:
                    activity_id = db_manager.add_activity(
                        trip_id=trip_id,
                        destination_id=destination['id'],
                        title=title,
                        description=description,
                        planned_date=planned_date,
                        planned_time=planned_time,
                        duration_minutes=duration,
                        cost=cost,
                        priority=priority,
                        category=category,
                        location=location,
                        contact_info=contact_info,
                        booking_required=booking_required,
                        booking_reference=booking_reference,
                        notes=notes
                    )
                    st.success(f"Activity added successfully! ID: {activity_id}")
                    st.rerun()
                else:
                    st.error("Please enter an activity title.")
    
    # Activity templates
    st.subheader("🎯 Quick Activity Templates")
    
    templates = {
        "Tokyo": [
            {"title": "Visit Senso-ji Temple", "category": "Cultural", "duration": 120, "cost": 0},
            {"title": "Explore Shibuya Crossing", "category": "Sightseeing", "duration": 60, "cost": 0},
            {"title": "Tokyo Skytree Observation", "category": "Sightseeing", "duration": 180, "cost": 25},
            {"title": "Traditional Sushi Experience", "category": "Dining", "duration": 90, "cost": 80},
        ],
        "Shenzhen": [
            {"title": "Visit Window of the World", "category": "Entertainment", "duration": 240, "cost": 30},
            {"title": "Explore Lianhuashan Park", "category": "Nature", "duration": 120, "cost": 0},
            {"title": "Shopping at Luohu Commercial City", "category": "Shopping", "duration": 180, "cost": 50},
        ],
        "Beijing": [
            {"title": "Great Wall of China (Mutianyu)", "category": "Sightseeing", "duration": 480, "cost": 60},
            {"title": "Forbidden City Tour", "category": "Cultural", "duration": 240, "cost": 20},
            {"title": "Authentic Peking Duck Dinner", "category": "Dining", "duration": 120, "cost": 45},
        ],
        "Jinan": [
            {"title": "Baotu Spring Park", "category": "Nature", "duration": 120, "cost": 5},
            {"title": "Daming Lake Scenic Area", "category": "Nature", "duration": 180, "cost": 8},
            {"title": "Thousand Buddha Mountain", "category": "Cultural", "duration": 240, "cost": 10},
        ],
        "Zhongshan": [
            {"title": "Sun Yat-sen Memorial Hall", "category": "Cultural", "duration": 120, "cost": 0},
            {"title": "Zhongshan Hot Springs", "category": "Entertainment", "duration": 240, "cost": 40},
            {"title": "Local Market Exploration", "category": "Cultural", "duration": 90, "cost": 20},
        ]
    }
    
    dest_name = destination['name']
    if dest_name in templates:
        st.write(f"**Suggested activities for {dest_name}:**")
        
        cols = st.columns(2)
        for i, template in enumerate(templates[dest_name]):
            with cols[i % 2]:
                if st.button(f"➕ {template['title']}", key=f"template_{dest_name}_{i}"):
                    db_manager.add_activity(
                        trip_id=trip_id,
                        destination_id=destination['id'],
                        title=template['title'],
                        category=template['category'],
                        duration_minutes=template['duration'],
                        cost=template['cost'],
                        priority=2,  # Medium priority
                        status='pending'
                    )
                    st.success(f"Added: {template['title']}")
                    st.rerun()

def render_progress_overview(db_manager, trip_id, destination):
    """Render progress overview and statistics"""
    
    st.subheader(f"📊 Progress Overview for {destination['name']}")
    
    # Get activities
    activities = db_manager.get_activities(trip_id, destination['id'])
    
    if not activities:
        st.info("No activities added yet.")
        return
    
    # Calculate statistics
    total_activities = len(activities)
    completed_activities = len([a for a in activities if a.get('status') == 'completed'])
    pending_activities = len([a for a in activities if a.get('status') == 'pending'])
    in_progress_activities = len([a for a in activities if a.get('status') == 'in_progress'])
    
    completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", total_activities)
    
    with col2:
        st.metric("Completed", completed_activities, delta=f"{completion_rate:.1f}%")
    
    with col3:
        st.metric("In Progress", in_progress_activities)
    
    with col4:
        st.metric("Pending", pending_activities)
    
    # Progress bar
    st.progress(completion_rate / 100, text=f"Overall Progress: {completion_rate:.1f}%")
    
    # Activity breakdown by category
    categories = {}
    for activity in activities:
        cat = activity.get('category', 'Other')
        if cat not in categories:
            categories[cat] = {'total': 0, 'completed': 0}
        categories[cat]['total'] += 1
        if activity.get('status') == 'completed':
            categories[cat]['completed'] += 1
    
    if categories:
        st.subheader("📈 Progress by Category")
        
        for category, stats in categories.items():
            completion = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.write(f"**{category}**: {stats['completed']}/{stats['total']} ({completion:.1f}%)")
            st.progress(completion / 100)
    
    # Export activities
    st.subheader("📤 Export Activities")
    
    if st.button("📄 Export Activities as CSV"):
        df = pd.DataFrame(activities)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Activities CSV",
            data=csv,
            file_name=f"{destination['name']}_activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


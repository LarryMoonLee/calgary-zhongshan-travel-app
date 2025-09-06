"""
Hotels Page - Accommodation Management
Manage hotel bookings, recommendations, and accommodation details
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

def render(db_manager, trip_id):
    """Render the hotels management page"""
    
    st.header("🏨 Hotels & Accommodation")
    st.markdown("Manage your accommodation bookings and find senior-friendly hotels")
    
    # Get destinations for hotel management
    destinations = db_manager.get_destinations(trip_id)
    
    if not destinations:
        st.info("Add destinations first to manage hotels for each location.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🏨 Hotel Bookings", 
        "💡 Recommendations", 
        "📊 Accommodation Overview"
    ])
    
    with tab1:
        render_hotel_bookings(db_manager, trip_id, destinations)
    
    with tab2:
        render_hotel_recommendations(db_manager, trip_id, destinations)
    
    with tab3:
        render_accommodation_overview(db_manager, trip_id, destinations)

def render_hotel_bookings(db_manager, trip_id, destinations):
    """Render hotel booking management"""
    
    st.subheader("🏨 Manage Hotel Bookings")
    
    # Add new hotel booking
    with st.expander("➕ Add New Hotel Booking", expanded=False):
        with st.form("add_hotel_booking"):
            st.subheader("Add Hotel Booking")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic hotel info
                destination_id = st.selectbox(
                    "Destination*",
                    [dest['id'] for dest in destinations],
                    format_func=lambda x: next((dest['name'] for dest in destinations if dest['id'] == x), "Unknown")
                )
                
                hotel_name = st.text_input("Hotel Name*", placeholder="e.g., Hotel Nikko Narita")
                address = st.text_input("Address", placeholder="Full hotel address")
                phone = st.text_input("Phone Number")
                email = st.text_input("Email")
                website = st.text_input("Website")
            
            with col2:
                # Booking details
                check_in_date = st.date_input("Check-in Date")
                check_out_date = st.date_input("Check-out Date")
                room_type = st.selectbox("Room Type", [
                    "Standard Room", "Deluxe Room", "Suite", "Twin Room", 
                    "Double Room", "Family Room", "Accessible Room"
                ])
                
                rate_per_night = st.number_input("Rate per Night ($)", min_value=0.0, value=0.0)
                
                # Calculate total cost
                if check_in_date and check_out_date and check_out_date > check_in_date:
                    nights = (check_out_date - check_in_date).days
                    total_cost = rate_per_night * nights
                    st.metric("Total Cost", f"${total_cost:,.2f}", delta=f"{nights} nights")
                else:
                    total_cost = 0
                    nights = 0
            
            # Additional details
            col1, col2 = st.columns(2)
            
            with col1:
                booking_reference = st.text_input("Booking Reference")
                confirmation_number = st.text_input("Confirmation Number")
                rating = st.slider("Hotel Rating", 1.0, 5.0, 3.0, 0.1)
            
            with col2:
                status = st.selectbox("Booking Status", [
                    "planned", "booked", "checked_in", "checked_out", "cancelled"
                ])
                distance_to_transport = st.text_input("Distance to Transportation", placeholder="e.g., 5 min walk to station")
            
            # Amenities
            amenities_options = [
                "Free WiFi", "Breakfast Included", "Airport Shuttle", "Fitness Center",
                "Swimming Pool", "Spa", "Restaurant", "Room Service", "Laundry Service",
                "Accessible Facilities", "Senior-Friendly", "English Speaking Staff",
                "Elevator", "Air Conditioning", "Parking"
            ]
            
            selected_amenities = st.multiselect("Amenities", amenities_options)
            notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("🏨 Add Hotel Booking"):
                if hotel_name and destination_id:
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute("""
                            INSERT INTO hotels (
                                trip_id, destination_id, name, address, phone, email, website,
                                check_in_date, check_out_date, room_type, rate_per_night, total_cost,
                                booking_reference, confirmation_number, amenities, rating,
                                distance_to_transport, notes, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            trip_id, destination_id, hotel_name, address, phone, email, website,
                            check_in_date, check_out_date, room_type, rate_per_night, total_cost,
                            booking_reference, confirmation_number, str(selected_amenities), rating,
                            distance_to_transport, notes, status
                        ))
                    
                    st.success(f"Hotel booking for '{hotel_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter hotel name and select destination.")
    
    # Display existing hotel bookings
    st.subheader("📋 Current Hotel Bookings")
    
    with db_manager.get_connection() as conn:
        hotels = [dict(row) for row in conn.execute("""
            SELECT h.*, d.name as destination_name, d.country
            FROM hotels h
            JOIN destinations d ON h.destination_id = d.id
            WHERE h.trip_id = ?
            ORDER BY h.check_in_date
        """, (trip_id,))]
    
    if hotels:
        for hotel in hotels:
            with st.container():
                st.markdown(f"""
                <div class="edit-section">
                    <h4>🏨 {hotel['name']} - {hotel['destination_name']}, {hotel['country']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**Address:** {hotel.get('address', 'Not specified')}")
                    st.write(f"**Room Type:** {hotel.get('room_type', 'Not specified')}")
                    if hotel.get('distance_to_transport'):
                        st.write(f"**Transport:** {hotel['distance_to_transport']}")
                    
                    # Status indicator
                    status_colors = {
                        'planned': '⏳',
                        'booked': '✅',
                        'checked_in': '🏨',
                        'checked_out': '✔️',
                        'cancelled': '❌'
                    }
                    status_icon = status_colors.get(hotel.get('status', 'planned'), '⚪')
                    st.write(f"**Status:** {status_icon} {hotel.get('status', 'planned').title()}")
                
                with col2:
                    st.write(f"**Check-in:** {hotel.get('check_in_date', 'N/A')}")
                    st.write(f"**Check-out:** {hotel.get('check_out_date', 'N/A')}")
                    if hotel.get('check_in_date') and hotel.get('check_out_date'):
                        nights = (datetime.strptime(hotel['check_out_date'], '%Y-%m-%d') - 
                                datetime.strptime(hotel['check_in_date'], '%Y-%m-%d')).days
                        st.write(f"**Nights:** {nights}")
                
                with col3:
                    st.write(f"**Rate/Night:** ${hotel.get('rate_per_night', 0):,.0f}")
                    st.write(f"**Total Cost:** ${hotel.get('total_cost', 0):,.0f}")
                    if hotel.get('rating'):
                        st.write(f"**Rating:** {'⭐' * int(hotel['rating'])} ({hotel['rating']}/5)")
                
                with col4:
                    if st.button("✏️ Edit", key=f"edit_hotel_{hotel['id']}"):
                        st.session_state[f"edit_hotel_{hotel['id']}"] = True
                    
                    if st.button("🗑️ Delete", key=f"delete_hotel_{hotel['id']}"):
                        with db_manager.get_connection() as conn:
                            conn.execute("DELETE FROM hotels WHERE id = ?", (hotel['id'],))
                        st.success("Hotel booking deleted!")
                        st.rerun()
                
                # Show amenities
                if hotel.get('amenities'):
                    try:
                        amenities = eval(hotel['amenities']) if hotel['amenities'].startswith('[') else [hotel['amenities']]
                        if amenities:
                            st.write(f"**Amenities:** {', '.join(amenities)}")
                    except:
                        st.write(f"**Amenities:** {hotel['amenities']}")
                
                # Contact info
                contact_info = []
                if hotel.get('phone'):
                    contact_info.append(f"📞 {hotel['phone']}")
                if hotel.get('email'):
                    contact_info.append(f"📧 {hotel['email']}")
                if hotel.get('website'):
                    contact_info.append(f"🌐 {hotel['website']}")
                
                if contact_info:
                    st.write(f"**Contact:** {' | '.join(contact_info)}")
                
                # Booking references
                if hotel.get('booking_reference') or hotel.get('confirmation_number'):
                    ref_info = []
                    if hotel.get('booking_reference'):
                        ref_info.append(f"Booking: {hotel['booking_reference']}")
                    if hotel.get('confirmation_number'):
                        ref_info.append(f"Confirmation: {hotel['confirmation_number']}")
                    st.write(f"**References:** {' | '.join(ref_info)}")
                
                if hotel.get('notes'):
                    st.write(f"**Notes:** {hotel['notes']}")
                
                # Edit form
                if st.session_state.get(f"edit_hotel_{hotel['id']}", False):
                    with st.form(f"edit_hotel_form_{hotel['id']}"):
                        st.subheader(f"Edit: {hotel['name']}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Hotel Name", value=hotel.get('name', ''))
                            new_address = st.text_input("Address", value=hotel.get('address', ''))
                            new_phone = st.text_input("Phone", value=hotel.get('phone', ''))
                            new_check_in = st.date_input(
                                "Check-in Date",
                                value=datetime.strptime(hotel.get('check_in_date', '2024-11-08'), '%Y-%m-%d').date() if hotel.get('check_in_date') else date.today()
                            )
                        
                        with col2:
                            new_room_type = st.text_input("Room Type", value=hotel.get('room_type', ''))
                            new_rate = st.number_input("Rate per Night ($)", value=float(hotel.get('rate_per_night', 0)), min_value=0.0)
                            new_rating = st.slider("Rating", 1.0, 5.0, float(hotel.get('rating', 3.0)), 0.1)
                            new_check_out = st.date_input(
                                "Check-out Date",
                                value=datetime.strptime(hotel.get('check_out_date', '2024-11-11'), '%Y-%m-%d').date() if hotel.get('check_out_date') else date.today()
                            )
                        
                        new_status = st.selectbox("Status", ["planned", "booked", "checked_in", "checked_out", "cancelled"], value=hotel.get('status', 'planned'))
                        new_notes = st.text_area("Notes", value=hotel.get('notes', ''))
                        
                        # Calculate new total cost
                        if new_check_in and new_check_out and new_check_out > new_check_in:
                            new_nights = (new_check_out - new_check_in).days
                            new_total_cost = new_rate * new_nights
                        else:
                            new_total_cost = 0
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Update Hotel"):
                                with db_manager.get_connection() as conn:
                                    conn.execute("""
                                        UPDATE hotels 
                                        SET name = ?, address = ?, phone = ?, room_type = ?, 
                                            rate_per_night = ?, total_cost = ?, rating = ?,
                                            check_in_date = ?, check_out_date = ?, status = ?, notes = ?
                                        WHERE id = ?
                                    """, (
                                        new_name, new_address, new_phone, new_room_type,
                                        new_rate, new_total_cost, new_rating,
                                        new_check_in, new_check_out, new_status, new_notes,
                                        hotel['id']
                                    ))
                                st.success("Hotel updated!")
                                st.session_state[f"edit_hotel_{hotel['id']}"] = False
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_hotel_{hotel['id']}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No hotel bookings added yet. Add your first hotel booking above!")

def render_hotel_recommendations(db_manager, trip_id, destinations):
    """Render hotel recommendations for each destination"""
    
    st.subheader("💡 Hotel Recommendations")
    st.markdown("Senior-friendly accommodations near transportation hubs")
    
    # Hotel recommendations by destination
    recommendations = {
        "Tokyo": [
            {
                "name": "Hotel Nikko Narita",
                "location": "Narita Airport Area",
                "distance": "5 min walk to Narita Airport",
                "price_range": "$120-180/night",
                "features": ["Airport shuttle", "English staff", "Accessible rooms", "Senior-friendly"],
                "rating": 4.2,
                "booking_tips": "Book directly for airport shuttle service"
            },
            {
                "name": "Keio Plaza Hotel Tokyo",
                "location": "Shinjuku",
                "distance": "2 min walk to Shinjuku Station",
                "price_range": "$150-220/night",
                "features": ["JR Station access", "Multiple restaurants", "Concierge service"],
                "rating": 4.0,
                "booking_tips": "Request higher floor for city views"
            }
        ],
        "Shenzhen": [
            {
                "name": "Vienna Hotel Shenzhen North",
                "location": "Shenzhen North Station",
                "distance": "3 min walk to HSR station",
                "price_range": "$60-90/night",
                "features": ["HSR station access", "Clean facilities", "Good value"],
                "rating": 4.1,
                "booking_tips": "Perfect for HSR connections to other cities"
            },
            {
                "name": "Shangri-La Hotel Shenzhen",
                "location": "Futian District",
                "distance": "10 min to metro station",
                "price_range": "$180-280/night",
                "features": ["Luxury amenities", "English staff", "Spa services"],
                "rating": 4.5,
                "booking_tips": "Premium option with excellent service"
            }
        ],
        "Jinan": [
            {
                "name": "Jinan Central Hotel",
                "location": "Near Jinan Railway Station",
                "distance": "5 min walk to railway station",
                "price_range": "$50-80/night",
                "features": ["Railway access", "Local cuisine", "Budget-friendly"],
                "rating": 3.8,
                "booking_tips": "Good location for exploring city springs"
            }
        ],
        "Beijing": [
            {
                "name": "Hampton by Hilton Beijing South",
                "location": "Beijing South Railway Station",
                "distance": "2 min walk to HSR station",
                "price_range": "$80-120/night",
                "features": ["HSR station access", "International brand", "Reliable service"],
                "rating": 4.3,
                "booking_tips": "Excellent for HSR travel, book early"
            },
            {
                "name": "Beijing Hotel",
                "location": "Wangfujing",
                "distance": "15 min to Forbidden City",
                "price_range": "$100-160/night",
                "features": ["Historic location", "Central Beijing", "Cultural sites nearby"],
                "rating": 4.0,
                "booking_tips": "Classic hotel in prime location"
            }
        ],
        "Zhongshan": [
            {
                "name": "Zhongshan International Hotel",
                "location": "City Center",
                "distance": "10 min to bus station",
                "price_range": "$40-70/night",
                "features": ["Local experience", "Good value", "Central location"],
                "rating": 3.9,
                "booking_tips": "Great base for exploring local culture"
            }
        ]
    }
    
    # Display recommendations for each destination
    for dest in destinations:
        dest_name = dest['name']
        if dest_name in recommendations:
            st.markdown(f"""
            <div class="edit-section">
                <h4>🏨 Recommended Hotels in {dest_name}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for hotel in recommendations[dest_name]:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{hotel['name']}**")
                    st.write(f"📍 {hotel['location']}")
                    st.write(f"🚶 {hotel['distance']}")
                    st.write(f"⭐ Rating: {hotel['rating']}/5")
                
                with col2:
                    st.write(f"**Price Range**")
                    st.write(hotel['price_range'])
                    st.write(f"**Features:**")
                    for feature in hotel['features'][:3]:  # Show first 3 features
                        st.write(f"• {feature}")
                
                with col3:
                    if st.button(f"➕ Add {hotel['name']}", key=f"add_rec_{dest['id']}_{hotel['name']}"):
                        # Pre-fill hotel booking form
                        st.session_state[f"prefill_hotel_{dest['id']}"] = {
                            'name': hotel['name'],
                            'destination_id': dest['id'],
                            'notes': f"Recommended hotel. {hotel['booking_tips']}"
                        }
                        st.success(f"Hotel '{hotel['name']}' details ready for booking!")
                
                if hotel.get('booking_tips'):
                    st.caption(f"💡 Tip: {hotel['booking_tips']}")
                
                st.divider()

def render_accommodation_overview(db_manager, trip_id, destinations):
    """Render accommodation overview and statistics"""
    
    st.subheader("📊 Accommodation Overview")
    
    # Get all hotels for the trip
    with db_manager.get_connection() as conn:
        hotels = [dict(row) for row in conn.execute("""
            SELECT h.*, d.name as destination_name
            FROM hotels h
            JOIN destinations d ON h.destination_id = d.id
            WHERE h.trip_id = ?
            ORDER BY h.check_in_date
        """, (trip_id,))]
    
    if not hotels:
        st.info("No hotel bookings to analyze. Add some hotel bookings first.")
        return
    
    # Calculate statistics
    total_cost = sum(float(hotel.get('total_cost', 0)) for hotel in hotels)
    total_nights = sum(
        (datetime.strptime(hotel['check_out_date'], '%Y-%m-%d') - 
         datetime.strptime(hotel['check_in_date'], '%Y-%m-%d')).days
        for hotel in hotels 
        if hotel.get('check_in_date') and hotel.get('check_out_date')
    )
    avg_rate = total_cost / total_nights if total_nights > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hotels", len(hotels))
    
    with col2:
        st.metric("Total Nights", total_nights)
    
    with col3:
        st.metric("Total Cost", f"${total_cost:,.0f}")
    
    with col4:
        st.metric("Avg Rate/Night", f"${avg_rate:,.0f}")
    
    # Cost breakdown by destination
    dest_costs = {}
    for hotel in hotels:
        dest = hotel['destination_name']
        cost = float(hotel.get('total_cost', 0))
        dest_costs[dest] = dest_costs.get(dest, 0) + cost
    
    if dest_costs:
        import plotly.express as px
        
        fig = px.pie(
            values=list(dest_costs.values()),
            names=list(dest_costs.keys()),
            title="Accommodation Costs by Destination"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Hotel timeline
    st.subheader("📅 Accommodation Timeline")
    
    timeline_data = []
    for hotel in hotels:
        if hotel.get('check_in_date') and hotel.get('check_out_date'):
            timeline_data.append({
                'Hotel': f"{hotel['name']} ({hotel['destination_name']})",
                'Start': hotel['check_in_date'],
                'Finish': hotel['check_out_date'],
                'Cost': f"${hotel.get('total_cost', 0):,.0f}"
            })
    
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True)
    
    # Export accommodation data
    st.subheader("📤 Export Accommodation Data")
    
    if st.button("📊 Export Hotel Bookings"):
        df = pd.DataFrame(hotels)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Hotels CSV",
            data=csv,
            file_name=f"hotel_bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


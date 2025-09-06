"""
Tools Page - Travel Utilities and Resources
Helpful tools, calculators, and resources for travel planning
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import json

def render(db_manager, trip_id):
    """Render the tools and utilities page"""
    
    st.header("🛠️ Travel Tools & Resources")
    st.markdown("Helpful utilities and resources for your journey")
    
    # Create tabs for different tools
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💱 Currency & Budget", 
        "🌍 Time Zones", 
        "📱 Travel Apps", 
        "📋 Checklists", 
        "🆘 Emergency Info"
    ])
    
    with tab1:
        render_currency_tools(db_manager, trip_id)
    
    with tab2:
        render_timezone_tools(db_manager, trip_id)
    
    with tab3:
        render_travel_apps(db_manager, trip_id)
    
    with tab4:
        render_checklists(db_manager, trip_id)
    
    with tab5:
        render_emergency_info(db_manager, trip_id)

def render_currency_tools(db_manager, trip_id):
    """Render currency conversion and budget tools"""
    
    st.subheader("💱 Currency Converter & Budget Tools")
    
    # Currency converter
    st.markdown("### 💰 Currency Converter")
    
    currencies = {
        "CAD": "Canadian Dollar",
        "USD": "US Dollar", 
        "JPY": "Japanese Yen",
        "CNY": "Chinese Yuan",
        "HKD": "Hong Kong Dollar",
        "EUR": "Euro",
        "GBP": "British Pound"
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from_currency = st.selectbox("From Currency", list(currencies.keys()), index=0)
        amount = st.number_input("Amount", min_value=0.0, value=100.0)
    
    with col2:
        to_currency = st.selectbox("To Currency", list(currencies.keys()), index=2)
    
    with col3:
        # Mock exchange rates (in real app, would use API)
        exchange_rates = {
            ("CAD", "USD"): 0.74,
            ("CAD", "JPY"): 110.0,
            ("CAD", "CNY"): 5.35,
            ("CAD", "HKD"): 5.78,
            ("USD", "CAD"): 1.35,
            ("USD", "JPY"): 149.0,
            ("USD", "CNY"): 7.25,
            ("JPY", "CAD"): 0.009,
            ("JPY", "USD"): 0.0067,
            ("JPY", "CNY"): 0.049,
            ("CNY", "CAD"): 0.187,
            ("CNY", "USD"): 0.138,
            ("CNY", "JPY"): 20.5,
            ("HKD", "CAD"): 0.173,
            ("HKD", "USD"): 0.128,
            ("HKD", "CNY"): 0.93
        }
        
        rate = exchange_rates.get((from_currency, to_currency), 1.0)
        converted_amount = amount * rate
        
        st.metric("Converted Amount", f"{converted_amount:,.2f} {to_currency}")
        st.caption(f"Rate: 1 {from_currency} = {rate} {to_currency}")
    
    st.info("💡 Exchange rates are approximate. Check current rates before traveling.")
    
    # Budget calculator
    st.markdown("### 📊 Daily Budget Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        daily_accommodation = st.number_input("Accommodation per day ($)", min_value=0.0, value=80.0)
        daily_food = st.number_input("Food per day ($)", min_value=0.0, value=50.0)
        daily_transport = st.number_input("Local transport per day ($)", min_value=0.0, value=20.0)
        daily_activities = st.number_input("Activities per day ($)", min_value=0.0, value=30.0)
        daily_misc = st.number_input("Miscellaneous per day ($)", min_value=0.0, value=20.0)
    
    with col2:
        total_daily = daily_accommodation + daily_food + daily_transport + daily_activities + daily_misc
        
        st.metric("Total Daily Budget", f"${total_daily:,.0f}")
        
        # Get trip duration
        trip = db_manager.get_trip(trip_id)
        if trip and trip.get('start_date') and trip.get('end_date'):
            start = datetime.strptime(trip['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(trip['end_date'], '%Y-%m-%d').date()
            trip_days = (end - start).days + 1
            
            total_trip_budget = total_daily * trip_days
            st.metric("Total Trip Budget", f"${total_trip_budget:,.0f}")
            st.metric("Trip Duration", f"{trip_days} days")
        
        # Budget breakdown chart
        budget_data = {
            'Category': ['Accommodation', 'Food', 'Transport', 'Activities', 'Miscellaneous'],
            'Amount': [daily_accommodation, daily_food, daily_transport, daily_activities, daily_misc]
        }
        
        import plotly.express as px
        fig = px.pie(
            values=budget_data['Amount'],
            names=budget_data['Category'],
            title="Daily Budget Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Expense tracker quick add
    st.markdown("### 💳 Quick Expense Entry")
    
    with st.form("quick_expense"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            expense_amount = st.number_input("Amount ($)", min_value=0.0, value=0.0)
            expense_category = st.selectbox("Category", [
                "Food", "Transport", "Accommodation", "Activities", "Shopping", "Other"
            ])
        
        with col2:
            expense_description = st.text_input("Description", placeholder="e.g., Lunch at station")
            expense_date = st.date_input("Date", value=date.today())
        
        with col3:
            payment_method = st.selectbox("Payment Method", [
                "Cash", "Credit Card", "Debit Card", "Mobile Payment"
            ])
            
            if st.form_submit_button("💾 Add Expense"):
                if expense_amount > 0 and expense_description:
                    # Add to expenses table
                    with db_manager.get_connection() as conn:
                        conn.execute("""
                            INSERT INTO expenses (trip_id, category, description, amount, expense_date, payment_method)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (trip_id, expense_category, expense_description, expense_amount, expense_date, payment_method))
                    
                    st.success(f"Expense of ${expense_amount:,.2f} added!")
                    st.rerun()

def render_timezone_tools(db_manager, trip_id):
    """Render timezone conversion tools"""
    
    st.subheader("🌍 Time Zone Converter")
    
    # Time zone information for journey cities
    timezones = {
        "Calgary": {"tz": "MST", "utc_offset": -7, "current_time": None},
        "Tokyo": {"tz": "JST", "utc_offset": 9, "current_time": None},
        "Hong Kong": {"tz": "HKT", "utc_offset": 8, "current_time": None},
        "Shenzhen": {"tz": "CST", "utc_offset": 8, "current_time": None},
        "Zhongshan": {"tz": "CST", "utc_offset": 8, "current_time": None},
        "Jinan": {"tz": "CST", "utc_offset": 8, "current_time": None},
        "Beijing": {"tz": "CST", "utc_offset": 8, "current_time": None}
    }
    
    # Calculate current times (mock calculation)
    base_time = datetime.now()
    
    st.markdown("### 🕐 Current Times in Journey Cities")
    
    cols = st.columns(len(timezones))
    
    for i, (city, info) in enumerate(timezones.items()):
        with cols[i % len(cols)]:
            # Mock time calculation (in real app, would use proper timezone library)
            city_time = base_time + timedelta(hours=info["utc_offset"] + 7)  # Assuming base is MST
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>{city}</h4>
                <p><strong>{city_time.strftime('%H:%M')}</strong></p>
                <p><small>{info['tz']} (UTC{info['utc_offset']:+d})</small></p>
                <p><small>{city_time.strftime('%Y-%m-%d')}</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Time converter
    st.markdown("### ⏰ Time Converter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from_city = st.selectbox("From City", list(timezones.keys()))
        input_time = st.time_input("Time", value=datetime.now().time())
        input_date = st.date_input("Date", value=date.today())
    
    with col2:
        to_city = st.selectbox("To City", list(timezones.keys()), index=1)
    
    with col3:
        # Calculate time difference
        from_offset = timezones[from_city]["utc_offset"]
        to_offset = timezones[to_city]["utc_offset"]
        time_diff = to_offset - from_offset
        
        # Convert time
        input_datetime = datetime.combine(input_date, input_time)
        converted_datetime = input_datetime + timedelta(hours=time_diff)
        
        st.metric("Converted Time", converted_datetime.strftime('%H:%M'))
        st.metric("Date", converted_datetime.strftime('%Y-%m-%d'))
        st.caption(f"Time difference: {time_diff:+d} hours")
    
    # Flight time calculator
    st.markdown("### ✈️ Flight Time Calculator")
    
    flight_times = {
        ("Calgary", "Tokyo"): {"duration": "10h 30m", "distance": "8,300 km"},
        ("Tokyo", "Hong Kong"): {"duration": "3h 45m", "distance": "2,900 km"},
        ("Hong Kong", "Shenzhen"): {"duration": "45m", "distance": "Ferry"},
        ("Shenzhen", "Zhongshan"): {"duration": "1h 30m", "distance": "Bus"},
        ("Zhongshan", "Jinan"): {"duration": "12h", "distance": "HSR"},
        ("Jinan", "Beijing"): {"duration": "2h", "distance": "HSR"},
        ("Beijing", "Zhongshan"): {"duration": "8h", "distance": "HSR"},
        ("Hong Kong", "Tokyo"): {"duration": "3h 30m", "distance": "2,900 km"},
        ("Tokyo", "Calgary"): {"duration": "9h 45m", "distance": "8,300 km"}
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        route_from = st.selectbox("From", list(timezones.keys()), key="flight_from")
        route_to = st.selectbox("To", list(timezones.keys()), key="flight_to", index=1)
    
    with col2:
        route_key = (route_from, route_to)
        if route_key in flight_times:
            info = flight_times[route_key]
            st.metric("Flight Duration", info["duration"])
            st.metric("Distance", info["distance"])
        else:
            st.info("Route information not available")

def render_travel_apps(db_manager, trip_id):
    """Render recommended travel apps and resources"""
    
    st.subheader("📱 Recommended Travel Apps & Resources")
    
    # Apps by category
    app_categories = {
        "🗺️ Navigation & Maps": [
            {"name": "Google Maps", "description": "Essential for navigation in all cities", "platform": "iOS/Android"},
            {"name": "Baidu Maps", "description": "Better for China (Chinese language)", "platform": "iOS/Android"},
            {"name": "Hyperdia", "description": "Japan train schedules and routes", "platform": "iOS/Android"}
        ],
        "🗣️ Translation & Communication": [
            {"name": "Google Translate", "description": "Camera translation for signs and menus", "platform": "iOS/Android"},
            {"name": "Pleco", "description": "Comprehensive Chinese dictionary", "platform": "iOS/Android"},
            {"name": "iTranslate Voice", "description": "Real-time voice translation", "platform": "iOS/Android"}
        ],
        "💰 Payment & Money": [
            {"name": "Alipay", "description": "Essential for payments in China", "platform": "iOS/Android"},
            {"name": "WeChat Pay", "description": "Alternative payment method in China", "platform": "iOS/Android"},
            {"name": "XE Currency", "description": "Real-time exchange rates", "platform": "iOS/Android"}
        ],
        "🚇 Transportation": [
            {"name": "Citymapper", "description": "Public transport in major cities", "platform": "iOS/Android"},
            {"name": "12306", "description": "Official China railway booking", "platform": "iOS/Android"},
            {"name": "JR East", "description": "Japan railway information", "platform": "iOS/Android"}
        ],
        "🏨 Accommodation & Dining": [
            {"name": "Booking.com", "description": "Hotel bookings worldwide", "platform": "iOS/Android"},
            {"name": "Dianping", "description": "Restaurant reviews in China", "platform": "iOS/Android"},
            {"name": "Tabelog", "description": "Restaurant reviews in Japan", "platform": "iOS/Android"}
        ]
    }
    
    for category, apps in app_categories.items():
        st.markdown(f"### {category}")
        
        for app in apps:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{app['name']}**")
            
            with col2:
                st.write(app['description'])
            
            with col3:
                st.caption(app['platform'])
        
        st.divider()
    
    # Useful websites
    st.markdown("### 🌐 Useful Websites")
    
    websites = [
        {"name": "Japan National Tourism Organization", "url": "https://www.jnto.go.jp/", "description": "Official Japan travel info"},
        {"name": "China Travel Guide", "url": "https://www.travelchinaguide.com/", "description": "Comprehensive China travel resource"},
        {"name": "Seat61", "url": "https://www.seat61.com/", "description": "Train travel information worldwide"},
        {"name": "Rome2Rio", "url": "https://www.rome2rio.com/", "description": "Multi-modal transport planning"},
        {"name": "TripAdvisor", "url": "https://www.tripadvisor.com/", "description": "Reviews and recommendations"}
    ]
    
    for website in websites:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write(f"**{website['name']}**")
        
        with col2:
            st.write(f"{website['description']} - {website['url']}")

def render_checklists(db_manager, trip_id):
    """Render travel checklists and preparation guides"""
    
    st.subheader("📋 Travel Checklists")
    
    # Pre-departure checklist
    st.markdown("### ✈️ Pre-Departure Checklist")
    
    predeparture_items = [
        "Valid passport (6+ months remaining)",
        "Visa for China (if required)",
        "Travel insurance policy",
        "Flight confirmations",
        "Hotel reservations",
        "Copies of important documents",
        "Emergency contact information",
        "Prescription medications",
        "Power adapters and converters",
        "Comfortable walking shoes",
        "Weather-appropriate clothing",
        "Mobile phone with international plan",
        "Download offline maps",
        "Install translation apps",
        "Notify banks of travel plans",
        "Arrange pet/house care",
        "Set up mail hold",
        "Charge all electronic devices"
    ]
    
    # Create interactive checklist
    if 'predeparture_checklist' not in st.session_state:
        st.session_state.predeparture_checklist = [False] * len(predeparture_items)
    
    completed_count = 0
    for i, item in enumerate(predeparture_items):
        checked = st.checkbox(item, value=st.session_state.predeparture_checklist[i], key=f"pre_{i}")
        st.session_state.predeparture_checklist[i] = checked
        if checked:
            completed_count += 1
    
    progress = completed_count / len(predeparture_items)
    st.progress(progress, text=f"Completed: {completed_count}/{len(predeparture_items)} ({progress*100:.0f}%)")
    
    st.divider()
    
    # Packing checklist
    st.markdown("### 🎒 Packing Checklist")
    
    packing_categories = {
        "📄 Documents": [
            "Passport", "Visa", "Travel insurance", "Flight tickets", 
            "Hotel confirmations", "Emergency contacts", "Medical information"
        ],
        "👕 Clothing": [
            "Comfortable walking shoes", "Warm jacket", "Rain jacket/umbrella",
            "Casual clothes", "Formal outfit", "Sleepwear", "Undergarments", "Socks"
        ],
        "🧴 Toiletries & Health": [
            "Toothbrush & toothpaste", "Shampoo & soap", "Prescription medications",
            "First aid kit", "Sunscreen", "Hand sanitizer", "Tissues"
        ],
        "📱 Electronics": [
            "Phone & charger", "Camera & charger", "Power bank", "Power adapters",
            "Headphones", "Tablet/e-reader", "Cables"
        ],
        "💰 Money & Cards": [
            "Credit cards", "Debit cards", "Cash (local currency)", "Money belt",
            "Backup cards", "Emergency cash"
        ]
    }
    
    for category, items in packing_categories.items():
        st.markdown(f"#### {category}")
        
        category_key = category.replace(" ", "_").replace("📄", "").replace("👕", "").replace("🧴", "").replace("📱", "").replace("💰", "")
        
        if f'packing_{category_key}' not in st.session_state:
            st.session_state[f'packing_{category_key}'] = [False] * len(items)
        
        for i, item in enumerate(items):
            checked = st.checkbox(item, value=st.session_state[f'packing_{category_key}'][i], key=f"pack_{category_key}_{i}")
            st.session_state[f'packing_{category_key}'][i] = checked
    
    # Emergency checklist
    st.markdown("### 🆘 Emergency Preparedness")
    
    emergency_items = [
        "Emergency contact numbers saved in phone",
        "Embassy contact information",
        "Travel insurance claim procedures",
        "Backup copies of documents (cloud storage)",
        "Emergency cash in multiple locations",
        "Medical alert information (if applicable)",
        "List of medications and allergies",
        "Emergency phrases in local languages"
    ]
    
    if 'emergency_checklist' not in st.session_state:
        st.session_state.emergency_checklist = [False] * len(emergency_items)
    
    for i, item in enumerate(emergency_items):
        checked = st.checkbox(item, value=st.session_state.emergency_checklist[i], key=f"emergency_{i}")
        st.session_state.emergency_checklist[i] = checked

def render_emergency_info(db_manager, trip_id):
    """Render emergency information and contacts"""
    
    st.subheader("🆘 Emergency Information")
    
    # Emergency numbers by country
    st.markdown("### 📞 Emergency Numbers")
    
    emergency_numbers = {
        "Canada": {
            "Emergency Services": "911",
            "Police": "911",
            "Fire": "911",
            "Medical": "911"
        },
        "Japan": {
            "Emergency Services": "110 (Police), 119 (Fire/Medical)",
            "Police": "110",
            "Fire": "119",
            "Medical": "119",
            "Tourist Hotline": "050-3816-2787"
        },
        "China": {
            "Emergency Services": "110 (Police), 120 (Medical), 119 (Fire)",
            "Police": "110",
            "Fire": "119",
            "Medical": "120",
            "Tourist Hotline": "12301"
        }
    }
    
    for country, numbers in emergency_numbers.items():
        st.markdown(f"#### 🏳️ {country}")
        
        for service, number in numbers.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{service}:**")
            with col2:
                st.write(number)
        
        st.divider()
    
    # Embassy information
    st.markdown("### 🏛️ Canadian Embassy/Consulate Information")
    
    embassies = {
        "Japan": {
            "name": "Embassy of Canada to Japan",
            "address": "7-3-38 Akasaka, Minato-ku, Tokyo 107-8503",
            "phone": "+81-3-5412-6200",
            "emergency": "+81-3-5412-6200",
            "email": "tokyo.consular@international.gc.ca"
        },
        "China": {
            "name": "Embassy of Canada to China",
            "address": "19 Dongzhimenwai Dajie, Chaoyang District, Beijing 100600",
            "phone": "+86-10-5139-4000",
            "emergency": "+86-10-5139-4000",
            "email": "beijing.consular@international.gc.ca"
        }
    }
    
    for country, embassy in embassies.items():
        st.markdown(f"#### 🏛️ {country}")
        
        st.write(f"**{embassy['name']}**")
        st.write(f"📍 Address: {embassy['address']}")
        st.write(f"📞 Phone: {embassy['phone']}")
        st.write(f"🆘 Emergency: {embassy['emergency']}")
        st.write(f"📧 Email: {embassy['email']}")
        
        st.divider()
    
    # Medical information
    st.markdown("### 🏥 Medical Information")
    
    medical_info = {
        "Japan": {
            "system": "Excellent healthcare system",
            "insurance": "Travel insurance recommended",
            "language": "Limited English in hospitals",
            "tips": "Bring prescription medications with documentation"
        },
        "China": {
            "system": "Good healthcare in major cities",
            "insurance": "Travel insurance essential",
            "language": "Limited English outside major hospitals",
            "tips": "International hospitals available in Beijing/Shanghai"
        }
    }
    
    for country, info in medical_info.items():
        st.markdown(f"#### 🏥 {country}")
        
        for key, value in info.items():
            st.write(f"**{key.title()}:** {value}")
        
        st.divider()
    
    # Personal emergency contacts
    st.markdown("### 👥 Personal Emergency Contacts")
    
    with st.form("emergency_contacts"):
        st.write("Add your personal emergency contacts:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            contact_name = st.text_input("Contact Name")
            contact_relationship = st.text_input("Relationship")
            contact_phone = st.text_input("Phone Number")
        
        with col2:
            contact_email = st.text_input("Email")
            contact_address = st.text_area("Address")
        
        if st.form_submit_button("💾 Save Emergency Contact"):
            if contact_name and contact_phone:
                # Save to database
                with db_manager.get_connection() as conn:
                    conn.execute("""
                        INSERT INTO emergency_contacts (trip_id, name, relationship, phone, email, address)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (trip_id, contact_name, contact_relationship, contact_phone, contact_email, contact_address))
                
                st.success("Emergency contact saved!")
                st.rerun()
    
    # Display saved emergency contacts
    with db_manager.get_connection() as conn:
        contacts = [dict(row) for row in conn.execute("""
            SELECT * FROM emergency_contacts WHERE trip_id = ?
        """, (trip_id,))]
    
    if contacts:
        st.markdown("#### 📋 Saved Emergency Contacts")
        
        for contact in contacts:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{contact['name']}**")
                st.write(f"Relationship: {contact.get('relationship', 'N/A')}")
            
            with col2:
                st.write(f"📞 {contact['phone']}")
                if contact.get('email'):
                    st.write(f"📧 {contact['email']}")
            
            with col3:
                if st.button("🗑️", key=f"delete_contact_{contact['id']}"):
                    with db_manager.get_connection() as conn:
                        conn.execute("DELETE FROM emergency_contacts WHERE id = ?", (contact['id'],))
                    st.rerun()
    
    # Important phrases
    st.markdown("### 🗣️ Important Phrases")
    
    phrases = {
        "Japanese": {
            "Help": "Tasukete (助けて)",
            "Emergency": "Kyūkyū (救急)",
            "Hospital": "Byōin (病院)",
            "Police": "Keisatsu (警察)",
            "I don't speak Japanese": "Nihongo ga wakarimasen (日本語がわかりません)",
            "Do you speak English?": "Eigo ga dekimasu ka? (英語ができますか？)"
        },
        "Chinese": {
            "Help": "Bāngzhù (帮助)",
            "Emergency": "Jǐnjí (紧急)",
            "Hospital": "Yīyuàn (医院)",
            "Police": "Jǐngchá (警察)",
            "I don't speak Chinese": "Wǒ bù huì shuō zhōngwén (我不会说中文)",
            "Do you speak English?": "Nǐ huì shuō yīngyǔ ma? (你会说英语吗？)"
        }
    }
    
    for language, phrase_dict in phrases.items():
        st.markdown(f"#### 🗣️ {language}")
        
        for english, local in phrase_dict.items():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**{english}:**")
            with col2:
                st.write(local)


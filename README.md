# 🌏 Calgary to Zhongshan Travel Planner

A comprehensive Streamlit web application for planning and managing your 50-day journey from Calgary, Alberta, Canada to Zhongshan, China, with stops in Tokyo, Shenzhen, Jinan, and Beijing.

## 🚀 Live Demo

**[View Live Application](https://your-app-name.streamlit.app)** *(URL will be available after deployment)*

## ✨ Features

### 🎯 **Comprehensive Travel Management**
- **Multiple Trip Support**: Create and manage different travel plans
- **Interactive Todo Lists**: Plan activities for each destination
- **Editable Transportation**: Modify flights, trains, buses with full details
- **Budget Tracking**: Monitor expenses and budget allocation
- **Hotel Management**: Senior-friendly accommodations near transport hubs
- **Visual Timeline**: Interactive itinerary with date/time editing

### 📍 **Destination Coverage**
- **Calgary, Canada** - Starting point
- **Tokyo, Japan** - 3-day cultural immersion
- **Shenzhen, China** - 3-day modern city experience
- **Zhongshan, China** - Extended stay (main destination)
- **Jinan, China** - 5-day northern exploration
- **Beijing, China** - 3-day capital highlights

### 🛠️ **Travel Tools**
- **Currency Converter** - Real-time exchange rates
- **Time Zone Calculator** - Multi-city time management
- **Travel Checklists** - Pre-departure and packing lists
- **Emergency Information** - Contacts and important phrases
- **Export/Import** - JSON, CSV, Excel data portability

## 🌐 Demo Mode Notice

**⚠️ Important**: This online version runs in demo mode on Streamlit Community Cloud.

- **Data Persistence**: Trip data resets when the app restarts
- **Backup Recommended**: Use Export/Import features to save your plans
- **Full Functionality**: All features work normally, just data isn't permanently stored

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Database**: SQLite (local storage)
- **Visualization**: Plotly (interactive charts)
- **Data Processing**: Pandas (data manipulation)
- **Export Formats**: JSON, CSV, Excel

### **Project Structure**
```
calgary_zhongshan_travel_app/
├── main.py                    # Main Streamlit application
├── requirements.txt           # Python dependencies
├── src/
│   ├── database.py           # SQLite database management
│   ├── pages/                # Application pages
│   │   ├── journey_page.py   # Trip overview
│   │   ├── route_page.py     # Transportation management
│   │   ├── destinations_page.py # Notes & activities
│   │   ├── budget_page.py    # Budget tracking
│   │   ├── itinerary_page.py # Timeline visualization
│   │   ├── hotels_page.py    # Accommodation management
│   │   └── tools_page.py     # Travel utilities
│   └── utils/                # Import/export utilities
└── README.md                 # This file
```

## 🚀 Local Installation

### **System Requirements**
- Python 3.10.10
- Windows 11 (optimized for)
- 4GB RAM minimum

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/yourusername/calgary-zhongshan-travel-app.git
cd calgary-zhongshan-travel-app

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run main.py
```

### **Access Application**
- Open browser to `http://localhost:8501`
- Full functionality with persistent data storage

## 📊 Sample Data

The application comes pre-loaded with a complete Calgary to Zhongshan journey:

- **Duration**: 50 days (November 8 - December 28)
- **Budget**: $10,000 USD
- **Transportation**: WestJet standby flights, high-speed rail, ferry connections
- **Accommodations**: Senior-friendly hotels near transport hubs
- **Activities**: Curated suggestions for each destination

## 🎯 Key Features Showcase

### **Interactive Route Planning**
- Visual journey map with clickable segments
- Detailed transportation information
- Real-time editing of flight/train details
- Cost tracking and booking references

### **Smart Activity Management**
- City-specific todo lists
- Priority setting and progress tracking
- Custom activity creation
- Template suggestions for each destination

### **Budget Intelligence**
- Category-wise budget allocation
- Expense tracking with receipt management
- Visual spending analysis
- Currency conversion tools

### **Senior-Friendly Design**
- Large, clear interface elements
- Accessibility considerations
- Budget-conscious recommendations
- Practical travel tips

## 🔧 Technical Details

### **Database Schema**
- **Trips**: Main trip information
- **Destinations**: City details and logistics
- **Activities**: Todo lists and planned activities
- **Transportation**: Flights, trains, buses, ferries
- **Hotels**: Accommodation bookings
- **Budget**: Categories and expense tracking
- **Emergency Contacts**: Safety information

### **Data Export/Import**
- **JSON**: Complete data structure preservation
- **CSV**: Spreadsheet-compatible format (multiple files)
- **Excel**: Multi-sheet workbook with summary

## 🌟 Use Cases

### **Personal Travel Planning**
- Plan complex multi-city journeys
- Track expenses and budget allocation
- Manage bookings and confirmations
- Create detailed itineraries

### **Travel Agencies**
- Demonstrate comprehensive trip planning
- Show client itineraries visually
- Export trip details for clients
- Manage multiple client trips

### **Educational**
- Learn about travel planning
- Understand budget management
- Explore destination information
- Practice itinerary creation

## 🤝 Contributing

This is a personal travel planning application, but suggestions and improvements are welcome!

### **Feedback Areas**
- User interface improvements
- Additional destination features
- Enhanced budget tracking
- Mobile responsiveness

## 📝 License

This project is created for personal travel planning purposes.

## 🙏 Acknowledgments

- **Streamlit Community** - Amazing web framework
- **Travel Planning Community** - Inspiration and best practices
- **Senior Travel Resources** - Accessibility and comfort considerations

## 📞 Support

For questions about the application or travel planning features, please refer to the built-in help sections and travel tools within the app.

---

**Happy Travels! 🌏✈️**

*Plan your Calgary to Zhongshan journey with confidence and style.*


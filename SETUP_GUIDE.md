# Calgary to Zhongshan Travel Planner - Setup Guide

## 📋 System Requirements

- **Operating System**: Windows 11
- **Python Version**: 3.10.10 (exactly)
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: At least 500MB free space
- **Internet Connection**: Required for initial setup and package installation

## 🚀 Installation Instructions

### Step 1: Verify Python Installation

1. Open Command Prompt (cmd) or PowerShell
2. Check Python version:
   ```bash
   python --version
   ```
   Should display: `Python 3.10.10`

3. If Python 3.10.10 is not installed:
   - Download from [python.org](https://www.python.org/downloads/release/python-31010/)
   - During installation, check "Add Python to PATH"
   - Restart your computer after installation

### Step 2: Extract Application Files

1. Extract the `calgary_zhongshan_travel_app.zip` file to your desired location
2. Recommended location: `C:\Users\[YourUsername]\Documents\TravelPlanner\`
3. The extracted folder should contain:
   ```
   calgary_zhongshan_travel_app/
   ├── main.py
   ├── requirements.txt
   ├── SETUP_GUIDE.md
   ├── setup_check.bat
   ├── run_app.bat
   ├── src/
   │   ├── database.py
   │   ├── pages/
   │   └── utils/
   └── data/ (will be created automatically)
   ```

### Step 3: Install Dependencies

1. Open Command Prompt as Administrator
2. Navigate to the application folder:
   ```bash
   cd "C:\Users\[YourUsername]\Documents\TravelPlanner\calgary_zhongshan_travel_app"
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Wait for installation to complete (may take 5-10 minutes)

### Step 4: Verify Installation

1. Run the setup check batch file:
   ```bash
   setup_check.bat
   ```

2. This will:
   - Check Python version
   - Verify all required packages are installed
   - Test database creation
   - Display system information

3. If all checks pass, you'll see: ✅ **All checks passed! Ready to run the application.**

### Step 5: Run the Application

1. Double-click `run_app.bat` or run from command prompt:
   ```bash
   run_app.bat
   ```

2. The application will start and automatically open in your default web browser
3. Default URL: `http://localhost:8501`

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "Python is not recognized as an internal or external command"
**Solution**: 
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH in System Environment Variables

#### Issue: "pip is not recognized as an internal or external command"
**Solution**:
- pip should come with Python 3.10.10
- Try using `python -m pip` instead of `pip`
- Reinstall Python if necessary

#### Issue: Package installation fails
**Solution**:
- Run Command Prompt as Administrator
- Update pip: `python -m pip install --upgrade pip`
- Try installing packages individually:
  ```bash
  pip install streamlit
  pip install pandas
  pip install plotly
  pip install openpyxl
  ```

#### Issue: Application won't start
**Solution**:
- Check if port 8501 is already in use
- Try running with different port:
  ```bash
  streamlit run main.py --server.port 8502
  ```
- Check firewall settings

#### Issue: Database errors
**Solution**:
- Delete the `data` folder and restart the application
- The database will be recreated automatically
- Ensure you have write permissions in the application folder

#### Issue: Browser doesn't open automatically
**Solution**:
- Manually open your browser and go to `http://localhost:8501`
- Try different browsers (Chrome, Firefox, Edge)

## 📁 File Structure Explanation

```
calgary_zhongshan_travel_app/
├── main.py                    # Main application entry point
├── requirements.txt           # Python package dependencies
├── SETUP_GUIDE.md            # This setup guide
├── setup_check.bat           # Installation verification script
├── run_app.bat               # Application launcher script
├── src/                      # Source code directory
│   ├── database.py           # Database management
│   ├── pages/                # Application pages
│   │   ├── __init__.py
│   │   ├── journey_page.py   # Trip overview page
│   │   ├── route_page.py     # Transportation management
│   │   ├── destinations_page.py # Destinations and activities
│   │   ├── budget_page.py    # Budget management
│   │   ├── itinerary_page.py # Timeline and scheduling
│   │   ├── hotels_page.py    # Hotel management
│   │   └── tools_page.py     # Travel tools and utilities
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── export_data.py    # Data export functions
│       └── import_data.py    # Data import functions
└── data/                     # Database and user data (created automatically)
    └── travel_planner.db     # SQLite database file
```

## 🎯 First Time Usage

### Creating Your First Trip

1. **Start the Application**: Run `run_app.bat`
2. **Default Trip**: A sample "Calgary to Zhongshan Journey" trip is created automatically
3. **Create New Trip**: Use the sidebar "➕ Create New Trip" section
4. **Switch Trips**: Select different trips from the sidebar list

### Key Features Overview

- **🏠 Journey**: Trip overview and management
- **🗺️ Route**: Transportation details with editing capabilities
- **📍 Destinations**: Notes, todo lists, and activity management
- **💰 Budget**: Expense tracking and budget management
- **📅 Itinerary**: Visual timeline with date/time editing
- **🏨 Hotels**: Accommodation booking management
- **🛠️ Tools**: Travel utilities and resources

### Data Management

- **Export**: Use sidebar to export trip data in JSON, CSV, or Excel format
- **Import**: Upload previously exported files to restore trip data
- **Backup**: Regular exports recommended for data backup

## 🔒 Security and Privacy

- **Local Storage**: All data is stored locally on your computer
- **No Cloud Sync**: Data is not transmitted to external servers
- **Database**: SQLite database file stored in `data/travel_planner.db`
- **Backups**: Create regular exports for data safety

## 🆘 Support and Help

### Getting Help

1. **Check this guide** for common solutions
2. **Run setup_check.bat** to diagnose issues
3. **Check application logs** in the command prompt window
4. **Restart the application** if experiencing issues

### System Information

- **Application Version**: 1.0.0
- **Python Requirement**: 3.10.10
- **Platform**: Windows 11
- **Database**: SQLite 3
- **Web Framework**: Streamlit

### Performance Tips

- **Close unused browser tabs** to free memory
- **Restart application** if it becomes slow
- **Regular exports** to prevent data loss
- **Keep Python updated** within the 3.10.x series

## 📝 Usage Notes

### Best Practices

1. **Regular Backups**: Export your trip data regularly
2. **Multiple Trips**: Create separate trips for different journeys
3. **Detailed Notes**: Use the notes features extensively for better planning
4. **Budget Tracking**: Record expenses as you travel
5. **Itinerary Updates**: Keep your schedule updated with actual times

### Data Limits

- **Trips**: No limit on number of trips
- **Destinations**: No limit per trip
- **Activities**: No limit per destination
- **File Size**: Export files typically under 10MB
- **Performance**: Optimal with under 1000 activities per trip

## 🔄 Updates and Maintenance

### Keeping the Application Updated

- **Python Packages**: Occasionally run `pip install --upgrade -r requirements.txt`
- **Application Files**: Replace files when new versions are available
- **Database**: Backup before any major updates

### Maintenance Tasks

- **Weekly**: Export trip data as backup
- **Monthly**: Check for Python package updates
- **Before Travel**: Verify all data is current and backed up

---

**Enjoy planning your Calgary to Zhongshan journey and future travels! 🌏✈️**


"""
Database Manager for Calgary to Zhongshan Travel Planner
Handles all SQLite database operations with full CRUD functionality
"""

import sqlite3
import json
from datetime import datetime, date, time
from pathlib import Path
import logging

class DatabaseManager:
    def __init__(self, db_path="data/travel_planner.db"):
        """Initialize database manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Create all necessary tables"""
        try:
            with self.get_connection() as conn:
                # Trips table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        total_budget REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Destinations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS destinations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        country TEXT NOT NULL,
                        arrival_date DATE,
                        departure_date DATE,
                        duration_days INTEGER,
                        budget REAL DEFAULT 0,
                        description TEXT,
                        highlights TEXT,
                        weather TEXT,
                        accommodation TEXT,
                        tips TEXT,
                        latitude REAL,
                        longitude REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
                    )
                """)
                
                # Transportation table - EDITABLE
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS transportation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        from_destination_id INTEGER,
                        to_destination_id INTEGER,
                        transport_type TEXT NOT NULL,
                        provider TEXT,
                        route_number TEXT,
                        departure_datetime DATETIME,
                        arrival_datetime DATETIME,
                        departure_location TEXT,
                        arrival_location TEXT,
                        duration_minutes INTEGER,
                        cost REAL DEFAULT 0,
                        currency TEXT DEFAULT 'USD',
                        booking_reference TEXT,
                        seat_number TEXT,
                        class_type TEXT,
                        status TEXT DEFAULT 'planned',
                        notes TEXT,
                        is_standby BOOLEAN DEFAULT FALSE,
                        confirmation_number TEXT,
                        check_in_time DATETIME,
                        gate_terminal TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
                        FOREIGN KEY (from_destination_id) REFERENCES destinations (id),
                        FOREIGN KEY (to_destination_id) REFERENCES destinations (id)
                    )
                """)
                
                # Activities/Todo table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        destination_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        planned_date DATE,
                        planned_time TIME,
                        duration_minutes INTEGER,
                        cost REAL DEFAULT 0,
                        priority INTEGER DEFAULT 1,
                        status TEXT DEFAULT 'pending',
                        category TEXT,
                        location TEXT,
                        contact_info TEXT,
                        booking_required BOOLEAN DEFAULT FALSE,
                        booking_reference TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
                        FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
                    )
                """)
                
                # Budget categories table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS budget_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        category_name TEXT NOT NULL,
                        allocated_amount REAL DEFAULT 0,
                        spent_amount REAL DEFAULT 0,
                        currency TEXT DEFAULT 'USD',
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
                    )
                """)
                
                # Hotels table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS hotels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        destination_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        address TEXT,
                        phone TEXT,
                        email TEXT,
                        website TEXT,
                        check_in_date DATE,
                        check_out_date DATE,
                        room_type TEXT,
                        rate_per_night REAL DEFAULT 0,
                        total_cost REAL DEFAULT 0,
                        currency TEXT DEFAULT 'USD',
                        booking_reference TEXT,
                        confirmation_number TEXT,
                        amenities TEXT,
                        rating REAL,
                        distance_to_transport TEXT,
                        notes TEXT,
                        status TEXT DEFAULT 'planned',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
                        FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
                    )
                """)
                
                # Emergency contacts table - MISSING IN ORIGINAL
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS emergency_contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        relationship TEXT,
                        phone TEXT NOT NULL,
                        email TEXT,
                        address TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
                    )
                """)
                
                # Expenses table for tracking actual spending
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL,
                        destination_id INTEGER,
                        activity_id INTEGER,
                        transportation_id INTEGER,
                        hotel_id INTEGER,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT DEFAULT 'USD',
                        expense_date DATE NOT NULL,
                        payment_method TEXT,
                        receipt_path TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
                        FOREIGN KEY (destination_id) REFERENCES destinations (id),
                        FOREIGN KEY (activity_id) REFERENCES activities (id),
                        FOREIGN KEY (transportation_id) REFERENCES transportation (id),
                        FOREIGN KEY (hotel_id) REFERENCES hotels (id)
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                return True
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    # TRIP MANAGEMENT
    def create_trip(self, name, description, start_date, end_date, total_budget):
        """Create a new trip"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO trips (name, description, start_date, end_date, total_budget)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, start_date, end_date, total_budget))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to create trip: {e}")
            return None
    
    def get_all_trips(self):
        """Get all trips"""
        try:
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute("SELECT * FROM trips ORDER BY created_at DESC")]
        except Exception as e:
            self.logger.error(f"Failed to get trips: {e}")
            return []
    
    def get_trip(self, trip_id):
        """Get specific trip"""
        try:
            with self.get_connection() as conn:
                row = conn.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get trip {trip_id}: {e}")
            return None
    
    def update_trip(self, trip_id, **kwargs):
        """Update trip details"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [trip_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE trips 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update trip {trip_id}: {e}")
            return False
    
    def delete_trip(self, trip_id):
        """Delete trip and all related data"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete trip {trip_id}: {e}")
            return False
    
    # DESTINATION MANAGEMENT
    def add_destination(self, trip_id, **kwargs):
        """Add new destination"""
        try:
            kwargs['trip_id'] = trip_id
            
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    INSERT INTO destinations ({field_names})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add destination: {e}")
            return None
    
    def get_destinations(self, trip_id):
        """Get all destinations for a trip"""
        try:
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute("""
                    SELECT * FROM destinations 
                    WHERE trip_id = ? 
                    ORDER BY arrival_date
                """, (trip_id,))]
        except Exception as e:
            self.logger.error(f"Failed to get destinations for trip {trip_id}: {e}")
            return []
    
    def update_destination(self, destination_id, **kwargs):
        """Update destination details"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [destination_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE destinations 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update destination {destination_id}: {e}")
            return False
    
    # TRANSPORTATION MANAGEMENT - FULLY EDITABLE
    def add_transportation(self, trip_id, **kwargs):
        """Add new transportation segment"""
        try:
            kwargs['trip_id'] = trip_id
            
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    INSERT INTO transportation ({field_names})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add transportation: {e}")
            return None
    
    def get_transportation(self, trip_id):
        """Get all transportation for a trip"""
        try:
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute("""
                    SELECT t.*, 
                           d1.name as from_destination_name,
                           d2.name as to_destination_name
                    FROM transportation t
                    LEFT JOIN destinations d1 ON t.from_destination_id = d1.id
                    LEFT JOIN destinations d2 ON t.to_destination_id = d2.id
                    WHERE t.trip_id = ?
                    ORDER BY t.departure_datetime
                """, (trip_id,))]
        except Exception as e:
            self.logger.error(f"Failed to get transportation for trip {trip_id}: {e}")
            return []
    
    def update_transportation(self, transport_id, **kwargs):
        """Update transportation details"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [transport_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE transportation 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update transportation {transport_id}: {e}")
            return False
    
    def delete_transportation(self, transport_id):
        """Delete transportation segment"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM transportation WHERE id = ?", (transport_id,))
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete transportation {transport_id}: {e}")
            return False
    
    # ACTIVITY MANAGEMENT
    def add_activity(self, trip_id, destination_id, **kwargs):
        """Add new activity"""
        try:
            kwargs['trip_id'] = trip_id
            kwargs['destination_id'] = destination_id
            
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    INSERT INTO activities ({field_names})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add activity: {e}")
            return None
    
    def get_activities(self, trip_id, destination_id=None):
        """Get activities for a trip or specific destination"""
        try:
            query = "SELECT * FROM activities WHERE trip_id = ?"
            params = [trip_id]
            
            if destination_id:
                query += " AND destination_id = ?"
                params.append(destination_id)
            
            query += " ORDER BY planned_date, planned_time"
            
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute(query, params)]
        except Exception as e:
            self.logger.error(f"Failed to get activities: {e}")
            return []
    
    def update_activity(self, activity_id, **kwargs):
        """Update activity details"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [activity_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE activities 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update activity {activity_id}: {e}")
            return False
    
    def delete_activity(self, activity_id):
        """Delete activity"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete activity {activity_id}: {e}")
            return False
    
    # BUDGET MANAGEMENT
    def add_budget_category(self, trip_id, **kwargs):
        """Add budget category"""
        try:
            kwargs['trip_id'] = trip_id
            
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    INSERT INTO budget_categories ({field_names})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add budget category: {e}")
            return None
    
    def get_budget_categories(self, trip_id):
        """Get budget categories for a trip"""
        try:
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute("""
                    SELECT * FROM budget_categories 
                    WHERE trip_id = ? 
                    ORDER BY category_name
                """, (trip_id,))]
        except Exception as e:
            self.logger.error(f"Failed to get budget categories: {e}")
            return []
    
    def update_budget_category(self, category_id, **kwargs):
        """Update budget category"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [category_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE budget_categories 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update budget category {category_id}: {e}")
            return False
    
    # HOTEL MANAGEMENT
    def add_hotel(self, trip_id, destination_id, **kwargs):
        """Add hotel booking"""
        try:
            kwargs['trip_id'] = trip_id
            kwargs['destination_id'] = destination_id
            
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    INSERT INTO hotels ({field_names})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add hotel: {e}")
            return None
    
    def get_hotels(self, trip_id, destination_id=None):
        """Get hotels for a trip or destination"""
        try:
            query = "SELECT * FROM hotels WHERE trip_id = ?"
            params = [trip_id]
            
            if destination_id:
                query += " AND destination_id = ?"
                params.append(destination_id)
            
            query += " ORDER BY check_in_date"
            
            with self.get_connection() as conn:
                return [dict(row) for row in conn.execute(query, params)]
        except Exception as e:
            self.logger.error(f"Failed to get hotels: {e}")
            return []
    
    def update_hotel(self, hotel_id, **kwargs):
        """Update hotel details"""
        if not kwargs:
            return False
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [hotel_id]
            
            with self.get_connection() as conn:
                conn.execute(f"""
                    UPDATE hotels 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, values)
                return True
        except Exception as e:
            self.logger.error(f"Failed to update hotel {hotel_id}: {e}")
            return False
    
    # SAMPLE DATA CREATION
    def create_sample_trip(self):
        """Create sample Calgary to Zhongshan trip"""
        try:
            # Create main trip
            trip_id = self.create_trip(
                name="Calgary to Zhongshan Journey",
                description="50-day adventure from Calgary, Alberta to Zhongshan, China with stops in Tokyo, Shenzhen, Jinan, and Beijing",
                start_date="2024-11-08",
                end_date="2024-12-28",
                total_budget=10000.0
            )
            
            if not trip_id:
                return None
            
            # Add destinations
            destinations = [
                {
                    'name': 'Calgary', 'country': 'Canada',
                    'arrival_date': '2024-11-08', 'departure_date': '2024-11-08',
                    'duration_days': 0, 'budget': 0,
                    'description': 'Starting point - Calgary, Alberta',
                    'weather': 'Cold autumn weather, -5 to 5°C',
                    'accommodation': 'Home base'
                },
                {
                    'name': 'Tokyo', 'country': 'Japan',
                    'arrival_date': '2024-11-09', 'departure_date': '2024-11-12',
                    'duration_days': 3, 'budget': 1200,
                    'description': 'First stop - Tokyo exploration',
                    'weather': 'Cool autumn, 10-18°C',
                    'accommodation': 'Hotel near Narita Airport'
                },
                {
                    'name': 'Shenzhen', 'country': 'China',
                    'arrival_date': '2024-11-12', 'departure_date': '2024-11-15',
                    'duration_days': 3, 'budget': 600,
                    'description': 'Modern Chinese city experience',
                    'weather': 'Mild autumn, 18-25°C',
                    'accommodation': 'Vienna Hotel Shenzhen North'
                },
                {
                    'name': 'Zhongshan', 'country': 'China',
                    'arrival_date': '2024-11-15', 'departure_date': '2024-11-18',
                    'duration_days': 3, 'budget': 400,
                    'description': 'Main destination - extended stay',
                    'weather': 'Pleasant autumn, 20-28°C',
                    'accommodation': 'Local guesthouse'
                },
                {
                    'name': 'Jinan', 'country': 'China',
                    'arrival_date': '2024-11-18', 'departure_date': '2024-11-23',
                    'duration_days': 5, 'budget': 800,
                    'description': 'Northern China exploration',
                    'weather': 'Cool autumn, 5-15°C',
                    'accommodation': 'Hotel near HSR station'
                },
                {
                    'name': 'Beijing', 'country': 'China',
                    'arrival_date': '2024-11-23', 'departure_date': '2024-11-26',
                    'duration_days': 3, 'budget': 900,
                    'description': 'Capital city highlights',
                    'weather': 'Cold autumn, 0-10°C',
                    'accommodation': 'Hampton by Hilton Beijing South'
                }
            ]
            
            dest_ids = {}
            for dest in destinations:
                dest_id = self.add_destination(trip_id, **dest)
                dest_ids[dest['name']] = dest_id
            
            # Add sample transportation
            transportation_segments = [
                {
                    'from_destination_id': dest_ids['Calgary'],
                    'to_destination_id': dest_ids['Tokyo'],
                    'transport_type': 'flight',
                    'provider': 'WestJet',
                    'departure_datetime': '2024-11-08 14:00:00',
                    'arrival_datetime': '2024-11-09 16:30:00',
                    'departure_location': 'Calgary International Airport (YYC)',
                    'arrival_location': 'Tokyo Narita Airport (NRT)',
                    'cost': 800.0,
                    'is_standby': True,
                    'status': 'planned',
                    'notes': 'Standby flight - arrive early at airport'
                },
                {
                    'from_destination_id': dest_ids['Tokyo'],
                    'to_destination_id': dest_ids['Shenzhen'],
                    'transport_type': 'flight',
                    'provider': 'Various Airlines',
                    'departure_datetime': '2024-11-12 10:00:00',
                    'arrival_datetime': '2024-11-12 14:00:00',
                    'departure_location': 'Tokyo Narita Airport (NRT)',
                    'arrival_location': 'Hong Kong International Airport (HKG)',
                    'cost': 400.0,
                    'status': 'planned',
                    'notes': 'Flight to Hong Kong, then ferry to Shenzhen'
                }
            ]
            
            for transport in transportation_segments:
                self.add_transportation(trip_id, **transport)
            
            # Add sample budget categories
            budget_categories = [
                {'category_name': 'Transportation', 'allocated_amount': 2000.0, 'description': 'Flights, trains, buses, ferries'},
                {'category_name': 'Accommodation', 'allocated_amount': 3000.0, 'description': 'Hotels and lodging'},
                {'category_name': 'Food & Dining', 'allocated_amount': 2500.0, 'description': 'Meals and dining experiences'},
                {'category_name': 'Activities & Sightseeing', 'allocated_amount': 1500.0, 'description': 'Tours, attractions, entertainment'},
                {'category_name': 'Shopping & Souvenirs', 'allocated_amount': 800.0, 'description': 'Gifts and personal purchases'},
                {'category_name': 'Emergency Fund', 'allocated_amount': 200.0, 'description': 'Unexpected expenses'}
            ]
            
            for category in budget_categories:
                self.add_budget_category(trip_id, **category)
            
            return trip_id
            
        except Exception as e:
            self.logger.error(f"Failed to create sample trip: {e}")
            return None
    
    def get_trip_statistics(self, trip_id):
        """Get comprehensive statistics for a trip"""
        try:
            with self.get_connection() as conn:
                # Get basic trip info
                trip_row = conn.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
                trip = dict(trip_row) if trip_row else {}
                
                # Calculate total days
                if trip.get('start_date') and trip.get('end_date'):
                    from datetime import datetime
                    start = datetime.strptime(trip['start_date'], '%Y-%m-%d')
                    end = datetime.strptime(trip['end_date'], '%Y-%m-%d')
                    total_days = (end - start).days + 1
                else:
                    total_days = 0
                
                # Count destinations
                total_cities = conn.execute("SELECT COUNT(*) FROM destinations WHERE trip_id = ?", (trip_id,)).fetchone()[0]
                
                # Count activities
                total_activities = conn.execute("SELECT COUNT(*) FROM activities WHERE trip_id = ?", (trip_id,)).fetchone()[0]
                
                # Get budget
                total_budget = trip.get('total_budget', 0)
                
                # Count transportation segments
                total_transport = conn.execute("SELECT COUNT(*) FROM transportation WHERE trip_id = ?", (trip_id,)).fetchone()[0]
                
                # Count hotels
                total_hotels = conn.execute("SELECT COUNT(*) FROM hotels WHERE trip_id = ?", (trip_id,)).fetchone()[0]
                
                # Calculate spent amounts
                total_expenses = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE trip_id = ?", (trip_id,)).fetchone()[0]
                
                return {
                    'total_days': total_days,
                    'total_cities': total_cities,
                    'total_activities': total_activities,
                    'total_budget': total_budget,
                    'total_transport': total_transport,
                    'total_hotels': total_hotels,
                    'total_expenses': total_expenses
                }
        except Exception as e:
            self.logger.error(f"Failed to get trip statistics: {e}")
            return {
                'total_days': 0,
                'total_cities': 0,
                'total_activities': 0,
                'total_budget': 0,
                'total_transport': 0,
                'total_hotels': 0,
                'total_expenses': 0
            }


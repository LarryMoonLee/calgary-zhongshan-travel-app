"""
Budget Page - Comprehensive Budget Management
Track expenses, manage budget categories, and monitor spending
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

def render(db_manager, trip_id):
    """Render the budget management page"""
    
    st.header("💰 Budget Management")
    st.markdown("Track your expenses and manage your travel budget")
    
    # Get trip and budget data
    trip = db_manager.get_trip(trip_id)
    budget_categories = db_manager.get_budget_categories(trip_id)
    
    # Initialize default budget categories if none exist
    if not budget_categories:
        initialize_default_budget_categories(db_manager, trip_id, trip.get('total_budget', 10000))
        budget_categories = db_manager.get_budget_categories(trip_id)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Budget Overview", 
        "📊 Budget Categories", 
        "💳 Expense Tracking", 
        "📈 Budget Analysis"
    ])
    
    with tab1:
        render_budget_overview(db_manager, trip_id, trip, budget_categories)
    
    with tab2:
        render_budget_categories(db_manager, trip_id, budget_categories)
    
    with tab3:
        render_expense_tracking(db_manager, trip_id)
    
    with tab4:
        render_budget_analysis(db_manager, trip_id, budget_categories)

def initialize_default_budget_categories(db_manager, trip_id, total_budget):
    """Initialize default budget categories"""
    
    default_categories = [
        {"name": "Transportation", "percentage": 25, "description": "Flights, trains, buses, local transport"},
        {"name": "Accommodation", "percentage": 30, "description": "Hotels, hostels, lodging"},
        {"name": "Food & Dining", "percentage": 20, "description": "Meals, snacks, beverages"},
        {"name": "Activities & Sightseeing", "percentage": 15, "description": "Tours, attractions, entertainment"},
        {"name": "Shopping & Souvenirs", "percentage": 5, "description": "Gifts, souvenirs, personal items"},
        {"name": "Emergency Fund", "percentage": 5, "description": "Unexpected expenses, medical, etc."}
    ]
    
    with db_manager.get_connection() as conn:
        for category in default_categories:
            allocated_amount = total_budget * (category["percentage"] / 100)
            conn.execute("""
                INSERT INTO budget_categories (trip_id, category_name, allocated_amount, description)
                VALUES (?, ?, ?, ?)
            """, (trip_id, category["name"], allocated_amount, category["description"]))

def render_budget_overview(db_manager, trip_id, trip, budget_categories):
    """Render budget overview section"""
    
    st.subheader("💰 Budget Overview")
    
    total_budget = float(trip.get('total_budget', 0))
    total_allocated = sum(float(cat.get('allocated_amount', 0)) for cat in budget_categories)
    total_spent = sum(float(cat.get('spent_amount', 0)) for cat in budget_categories)
    remaining_budget = total_budget - total_spent
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Budget", f"${total_budget:,.0f}")
    
    with col2:
        st.metric("Total Spent", f"${total_spent:,.0f}", delta=f"-${total_spent:,.0f}")
    
    with col3:
        st.metric("Remaining", f"${remaining_budget:,.0f}")
    
    with col4:
        spent_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        st.metric("Spent %", f"{spent_percentage:.1f}%")
    
    # Budget progress bar
    progress = min(total_spent / total_budget, 1.0) if total_budget > 0 else 0
    st.progress(progress, text=f"Budget Used: {spent_percentage:.1f}%")
    
    # Budget allocation pie chart
    if budget_categories:
        st.subheader("📊 Budget Allocation")
        
        category_names = [cat['category_name'] for cat in budget_categories]
        allocated_amounts = [float(cat.get('allocated_amount', 0)) for cat in budget_categories]
        
        fig = px.pie(
            values=allocated_amounts,
            names=category_names,
            title="Budget Allocation by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick budget adjustment
    st.subheader("⚙️ Quick Budget Adjustment")
    
    with st.form("adjust_total_budget"):
        new_total_budget = st.number_input(
            "Total Trip Budget ($)",
            value=total_budget,
            min_value=0.0,
            step=100.0
        )
        
        if st.form_submit_button("💾 Update Total Budget"):
            db_manager.update_trip(trip_id, total_budget=new_total_budget)
            
            # Proportionally adjust category allocations
            if total_allocated > 0:
                adjustment_factor = new_total_budget / total_allocated
                for category in budget_categories:
                    new_allocation = float(category.get('allocated_amount', 0)) * adjustment_factor
                    db_manager.update_budget_category(category['id'], allocated_amount=new_allocation)
            
            st.success("Budget updated successfully!")
            st.rerun()

def render_budget_categories(db_manager, trip_id, budget_categories):
    """Render budget categories management"""
    
    st.subheader("📊 Budget Categories")
    
    # Add new category
    with st.expander("➕ Add New Budget Category"):
        with st.form("add_budget_category"):
            col1, col2 = st.columns(2)
            
            with col1:
                category_name = st.text_input("Category Name")
                allocated_amount = st.number_input("Allocated Amount ($)", min_value=0.0, value=0.0)
            
            with col2:
                currency = st.selectbox("Currency", ["USD", "CAD", "JPY", "CNY"], index=0)
                description = st.text_input("Description")
            
            if st.form_submit_button("➕ Add Category"):
                if category_name:
                    with db_manager.get_connection() as conn:
                        conn.execute("""
                            INSERT INTO budget_categories (trip_id, category_name, allocated_amount, currency, description)
                            VALUES (?, ?, ?, ?, ?)
                        """, (trip_id, category_name, allocated_amount, currency, description))
                    st.success("Budget category added!")
                    st.rerun()
    
    # Display and edit existing categories
    if budget_categories:
        for category in budget_categories:
            with st.container():
                st.markdown(f"""
                <div class="edit-section">
                    <h4>💳 {category['category_name']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    # Category details
                    allocated = float(category.get('allocated_amount', 0))
                    spent = float(category.get('spent_amount', 0))
                    remaining = allocated - spent
                    spent_percentage = (spent / allocated * 100) if allocated > 0 else 0
                    
                    st.write(f"**Description:** {category.get('description', 'No description')}")
                    st.progress(min(spent / allocated, 1.0) if allocated > 0 else 0, 
                              text=f"Spent: ${spent:,.0f} / ${allocated:,.0f} ({spent_percentage:.1f}%)")
                
                with col2:
                    st.metric("Allocated", f"${allocated:,.0f}")
                
                with col3:
                    st.metric("Spent", f"${spent:,.0f}")
                
                with col4:
                    st.metric("Remaining", f"${remaining:,.0f}")
                
                # Edit category
                with st.expander(f"✏️ Edit {category['category_name']}"):
                    with st.form(f"edit_category_{category['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Category Name", value=category.get('category_name', ''))
                            new_allocated = st.number_input("Allocated Amount ($)", value=allocated, min_value=0.0)
                        
                        with col2:
                            new_spent = st.number_input("Spent Amount ($)", value=spent, min_value=0.0)
                            new_description = st.text_input("Description", value=category.get('description', ''))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Update"):
                                db_manager.update_budget_category(
                                    category['id'],
                                    category_name=new_name,
                                    allocated_amount=new_allocated,
                                    spent_amount=new_spent,
                                    description=new_description
                                )
                                st.success("Category updated!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete"):
                                with db_manager.get_connection() as conn:
                                    conn.execute("DELETE FROM budget_categories WHERE id = ?", (category['id'],))
                                st.success("Category deleted!")
                                st.rerun()
                
                st.divider()
    else:
        st.info("No budget categories found.")

def render_expense_tracking(db_manager, trip_id):
    """Render expense tracking section"""
    
    st.subheader("💳 Expense Tracking")
    
    # Add new expense
    with st.expander("➕ Add New Expense", expanded=False):
        with st.form("add_expense"):
            st.subheader("Record New Expense")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get destinations and categories for dropdowns
                destinations = db_manager.get_destinations(trip_id)
                budget_categories = db_manager.get_budget_categories(trip_id)
                
                expense_category = st.selectbox(
                    "Category",
                    [cat['category_name'] for cat in budget_categories] if budget_categories else ["Other"]
                )
                
                destination_id = st.selectbox(
                    "Destination",
                    [None] + [dest['id'] for dest in destinations],
                    format_func=lambda x: "General" if x is None else next((dest['name'] for dest in destinations if dest['id'] == x), "Unknown")
                ) if destinations else None
                
                description = st.text_input("Description*", placeholder="e.g., Lunch at Tokyo Station")
                amount = st.number_input("Amount ($)*", min_value=0.0, value=0.0)
            
            with col2:
                expense_date = st.date_input("Date", value=date.today())
                payment_method = st.selectbox("Payment Method", [
                    "Cash", "Credit Card", "Debit Card", "Mobile Payment", "Bank Transfer", "Other"
                ])
                currency = st.selectbox("Currency", ["USD", "CAD", "JPY", "CNY"], index=0)
                notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("💾 Add Expense"):
                if description and amount > 0:
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute("""
                            INSERT INTO expenses (trip_id, destination_id, category, description, amount, currency, expense_date, payment_method, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (trip_id, destination_id, expense_category, description, amount, currency, expense_date, payment_method, notes))
                        
                        # Update budget category spent amount
                        if budget_categories:
                            for cat in budget_categories:
                                if cat['category_name'] == expense_category:
                                    new_spent = float(cat.get('spent_amount', 0)) + amount
                                    db_manager.update_budget_category(cat['id'], spent_amount=new_spent)
                                    break
                    
                    st.success(f"Expense of ${amount:,.2f} added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter description and amount.")
    
    # Display recent expenses
    st.subheader("📋 Recent Expenses")
    
    with db_manager.get_connection() as conn:
        expenses = [dict(row) for row in conn.execute("""
            SELECT e.*, d.name as destination_name
            FROM expenses e
            LEFT JOIN destinations d ON e.destination_id = d.id
            WHERE e.trip_id = ?
            ORDER BY e.expense_date DESC, e.created_at DESC
            LIMIT 20
        """, (trip_id,))]
    
    if expenses:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = list(set(exp['category'] for exp in expenses))
            category_filter = st.selectbox("Filter by Category", ["All"] + categories)
        
        with col2:
            destinations = list(set(exp['destination_name'] for exp in expenses if exp['destination_name']))
            destination_filter = st.selectbox("Filter by Destination", ["All"] + destinations)
        
        with col3:
            date_range = st.date_input("Date Range", value=[])
        
        # Apply filters
        filtered_expenses = expenses.copy()
        
        if category_filter != "All":
            filtered_expenses = [exp for exp in filtered_expenses if exp['category'] == category_filter]
        
        if destination_filter != "All":
            filtered_expenses = [exp for exp in filtered_expenses if exp['destination_name'] == destination_filter]
        
        # Display expenses
        for expense in filtered_expenses[:10]:  # Show top 10
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{expense['description']}**")
                st.caption(f"{expense['category']} • {expense.get('destination_name', 'General')}")
            
            with col2:
                st.write(f"${expense['amount']:,.2f}")
                st.caption(expense.get('currency', 'USD'))
            
            with col3:
                st.write(expense['expense_date'])
                st.caption(expense.get('payment_method', 'Unknown'))
            
            with col4:
                if st.button("✏️", key=f"edit_expense_{expense['id']}"):
                    st.session_state[f"edit_expense_{expense['id']}"] = True
            
            # Edit expense form
            if st.session_state.get(f"edit_expense_{expense['id']}", False):
                with st.form(f"edit_expense_form_{expense['id']}"):
                    st.subheader(f"Edit: {expense['description']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_description = st.text_input("Description", value=expense['description'])
                        new_amount = st.number_input("Amount", value=float(expense['amount']), min_value=0.0)
                        new_category = st.text_input("Category", value=expense['category'])
                    
                    with col2:
                        new_date = st.date_input("Date", value=datetime.strptime(expense['expense_date'], '%Y-%m-%d').date())
                        new_payment_method = st.text_input("Payment Method", value=expense.get('payment_method', ''))
                        new_notes = st.text_area("Notes", value=expense.get('notes', ''))
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.form_submit_button("💾 Update"):
                            with db_manager.get_connection() as conn:
                                conn.execute("""
                                    UPDATE expenses 
                                    SET description = ?, amount = ?, category = ?, expense_date = ?, payment_method = ?, notes = ?
                                    WHERE id = ?
                                """, (new_description, new_amount, new_category, new_date, new_payment_method, new_notes, expense['id']))
                            st.success("Expense updated!")
                            st.session_state[f"edit_expense_{expense['id']}"] = False
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🗑️ Delete"):
                            with db_manager.get_connection() as conn:
                                conn.execute("DELETE FROM expenses WHERE id = ?", (expense['id'],))
                            st.success("Expense deleted!")
                            st.session_state[f"edit_expense_{expense['id']}"] = False
                            st.rerun()
                    
                    with col3:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state[f"edit_expense_{expense['id']}"] = False
                            st.rerun()
            
            st.divider()
    else:
        st.info("No expenses recorded yet.")

def render_budget_analysis(db_manager, trip_id, budget_categories):
    """Render budget analysis and charts"""
    
    st.subheader("📈 Budget Analysis")
    
    if not budget_categories:
        st.info("Add budget categories to see analysis.")
        return
    
    # Budget vs Actual spending
    categories = [cat['category_name'] for cat in budget_categories]
    allocated = [float(cat.get('allocated_amount', 0)) for cat in budget_categories]
    spent = [float(cat.get('spent_amount', 0)) for cat in budget_categories]
    
    # Create comparison chart
    fig = go.Figure(data=[
        go.Bar(name='Allocated', x=categories, y=allocated),
        go.Bar(name='Spent', x=categories, y=spent)
    ])
    
    fig.update_layout(
        title="Budget vs Actual Spending by Category",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Spending efficiency
    st.subheader("💡 Spending Insights")
    
    for category in budget_categories:
        allocated_amt = float(category.get('allocated_amount', 0))
        spent_amt = float(category.get('spent_amount', 0))
        
        if allocated_amt > 0:
            efficiency = (spent_amt / allocated_amt) * 100
            remaining = allocated_amt - spent_amt
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{category['category_name']}**")
                
                if efficiency > 100:
                    st.error(f"Over budget by ${spent_amt - allocated_amt:,.0f} ({efficiency - 100:.1f}%)")
                elif efficiency > 80:
                    st.warning(f"Using {efficiency:.1f}% of budget")
                else:
                    st.success(f"Using {efficiency:.1f}% of budget")
            
            with col2:
                st.metric("Remaining", f"${remaining:,.0f}")
            
            with col3:
                st.metric("Efficiency", f"{efficiency:.1f}%")
    
    # Export budget data
    st.subheader("📤 Export Budget Data")
    
    if st.button("📊 Export Budget Summary"):
        budget_df = pd.DataFrame(budget_categories)
        csv = budget_df.to_csv(index=False)
        st.download_button(
            label="Download Budget CSV",
            data=csv,
            file_name=f"budget_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


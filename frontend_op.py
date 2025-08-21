 frontend_fin.py

import streamlit as st
import pandas as pd
import backend_op
from datetime import date

# Set the page title and layout
st.set_page_config(layout="wide")
st.title("🚗 Vehicle Fleet Management")

# Initialize the database table
backend_op.create_table()

# --- Business Insights Section (Aggregation) ---
st.header("📈 Business Insights")
insights = backend_op.get_fleet_insights()

if insights:
    col1, col2, col3, col4 = st.columns(4)

    # COUNT: Total number of vehicles
    with col1:
        st.metric(label="Total Vehicles", value=insights.get("total_vehicles", 0))
    
    # AVG: Average current mileage
    with col2:
        avg_mileage = insights.get("avg_mileage")
        st.metric(label="Average Mileage", value=f"{avg_mileage:,.2f}" if avg_mileage else "N/A")

    # MAX: Vehicle with max mileage
    with col3:
        max_mileage_vehicle = insights.get("max_mileage_vehicle")
        if max_mileage_vehicle:
            st.metric(label="Max Mileage Vehicle", value=f"{max_mileage_vehicle[2]} ({max_mileage_vehicle[1]:,})")
        else:
            st.metric(label="Max Mileage Vehicle", value="N/A")

    # MIN: Vehicle with min mileage
    with col4:
        min_mileage_vehicle = insights.get("min_mileage_vehicle")
        if min_mileage_vehicle:
            st.metric(label="Min Mileage Vehicle", value=f"{min_mileage_vehicle[2]} ({min_mileage_vehicle[1]:,})")
        else:
            st.metric(label="Min Mileage Vehicle", value="N/A")

st.markdown("---")

# --- Vehicle CRUD Operations ---
st.header("🔧 Manage Fleet")

operation = st.selectbox("Select Operation", ["Add New Vehicle", "Update Vehicle", "Delete Vehicle"], key='crud_op')

# --- CREATE operation ---
if operation == "Add New Vehicle":
    st.subheader("Add a New Vehicle")
    with st.form("add_vehicle_form"):
        vehicle_id = st.text_input("Vehicle ID", help="e.g., VIN or unique identifier")
        make = st.text_input("Make")
        model = st.text_input("Model")
        status = st.selectbox("Status", ["In Use", "Maintenance", "Parked"])
        current_mileage = st.number_input("Current Mileage", min_value=0, step=1)
        last_service_date = st.date_input("Last Service Date", date.today())
        
        submitted = st.form_submit_button("Add Vehicle")
        if submitted:
            if vehicle_id and make:
                backend_fin.create_vehicle(vehicle_id, make, model, status, current_mileage, last_service_date)
                st.success(f"Vehicle {vehicle_id} added successfully!")
            else:
                st.error("Vehicle ID and Make are required.")

# --- UPDATE operation ---
if operation == "Update Vehicle":
    st.subheader("Update Vehicle Details")
    vehicle_ids = backend_op.get_unique_values("vehicle_id")
    if vehicle_ids:
        selected_id = st.selectbox("Select Vehicle ID to Update", vehicle_ids)
        with st.form("update_vehicle_form"):
            make = st.text_input("Make")
            model = st.text_input("Model")
            status = st.selectbox("Status", ["In Use", "Maintenance", "Parked"])
            current_mileage = st.number_input("Current Mileage", min_value=0, step=1)
            last_service_date = st.date_input("Last Service Date", date.today())
            
            submitted = st.form_submit_button("Update Vehicle")
            if submitted:
                backend_op.update_vehicle(selected_id, make, model, status, current_mileage, last_service_date)
                st.success(f"Vehicle {selected_id} updated successfully!")

# --- DELETE operation ---
if operation == "Delete Vehicle":
    st.subheader("Delete a Vehicle")
    vehicle_ids = backend_op.get_unique_values("vehicle_id")
    if vehicle_ids:
        selected_id = st.selectbox("Select Vehicle ID to Delete", vehicle_ids)
        if st.button("Delete Vehicle"):
            backend_fin.delete_vehicle(selected_id)
            st.success(f"Vehicle {selected_id} deleted successfully.")
    else:
        st.info("No vehicles to delete.")
    
st.markdown("---")

# --- READ & Filtering/Sorting ---
st.header("🔍 Fleet Overview")

# Filtering and Sorting Options
col_filter, col_sort = st.columns(2)

with col_filter:
    filter_by = st.selectbox("Filter by", ["None", "status", "make"])
    filter_value = None
    if filter_by == "status":
        unique_statuses = backend_op.get_unique_values("status")
        filter_value = st.selectbox("Select Status", unique_statuses)
    elif filter_by == "make":
        unique_makes = backend_op.get_unique_values("make")
        filter_value = st.selectbox("Select Make", unique_makes)

with col_sort:
    sort_by = st.selectbox("Sort by", ["None", "current_mileage", "last_service_date"])

# Fetch and display data
if filter_by == "None":
    filter_by = None
if sort_by == "None":
    sort_by = None

vehicles = backend_op.read_vehicles(filter_by=filter_by, filter_value=filter_value, sort_by=sort_by)

if vehicles:
    df = pd.DataFrame(vehicles, columns=["vehicle_id", "make", "model", "status", "current_mileage", "last_service_date"])
    st.dataframe(df.set_index("vehicle_id"))
else:
    st.info("No vehicles found in the fleet. Please add a new vehicle.")

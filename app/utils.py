import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .models import Store, StoreStatus, BusinessHours, Report
from .database import SessionLocal
from datetime import datetime, timedelta
import pytz

def generate_report(report_id: str):
    db = SessionLocal()
    
    # Fetch all necessary data
    stores = db.query(Store).all()
    status_records = db.query(StoreStatus).all()
    business_hours = db.query(BusinessHours).all()

    # Convert to pandas DataFrames for efficient processing
    stores_df = pd.DataFrame([(s.id, s.timezone_str) for s in stores], columns=['store_id', 'timezone_str'])
    status_df = pd.DataFrame([(s.store_id, s.timestamp_utc, s.status) for s in status_records], 
                             columns=['store_id', 'timestamp_utc', 'status'])
    hours_df = pd.DataFrame([(h.store_id, h.day_of_week, h.start_time_local, h.end_time_local) 
                             for h in business_hours],
                            columns=['store_id', 'day_of_week', 'start_time_local', 'end_time_local'])

    # Merge dataframes
    merged_df = pd.merge(status_df, stores_df, on='store_id', how='left')
    
    # Ensure 'timestamp_utc' is in datetime format
    merged_df['timestamp_utc'] = pd.to_datetime(merged_df['timestamp_utc'])
    
    # Drop rows with missing timezone or assign a default timezone
    merged_df['timezone_str'] = merged_df['timezone_str'].fillna('UTC')  # Replace 'UTC' with any default timezone you prefer

    # Convert timestamps to store's local time
    try:
        merged_df['local_time'] = merged_df.apply(
            lambda row: row['timestamp_utc'].replace(tzinfo=pytz.UTC).astimezone(
                pytz.timezone(row['timezone_str'])
            ) if pd.notna(row['timezone_str']) else row['timestamp_utc'],  # If timezone is NaN, keep it as UTC
            axis=1
        )
    except Exception as e:
        print(f"Error converting timezones: {e}")

    # Check if 'local_time' column exists
    if 'local_time' not in merged_df.columns:
        print("Failed to create 'local_time' for some rows")
        db.close()
        return  # Exit the function if 'local_time' is missing

    # Calculate uptime and downtime
    current_time = status_df['timestamp_utc'].max()
    report_data = []

    for store_id in merged_df['store_id'].unique():
        store_data = merged_df[merged_df['store_id'] == store_id]
        store_hours = hours_df[hours_df['store_id'] == store_id]
        
        # Calculate uptime and downtime for different time ranges
        for time_range, hours in [('last_hour', 1), ('last_day', 24), ('last_week', 168)]:
            start_time = current_time - timedelta(hours=hours)
            range_data = store_data[(store_data['timestamp_utc'] >= start_time) & (store_data['timestamp_utc'] <= current_time)]
            
            # Debugging: Check the columns and content of range_data
            print(f"\nProcessing store_id: {store_id}, time_range: {time_range}")
            # print("Columns in range_data:", range_data.columns)
            # print("Sample data in range_data:\n", range_data.head())

            # Filter data within business hours
            range_data = filter_business_hours(range_data, store_hours)
            
            if 'status' not in range_data.columns:
                print(f"Warning: 'status' column is missing in range_data for store_id: {store_id} and time_range: {time_range}")
                continue  # Skip further processing for this range

            total_minutes = hours * 60
            active_minutes = range_data[range_data['status'] == 'active']['timestamp_utc'].diff().dt.total_seconds().sum() / 60
            inactive_minutes = range_data[range_data['status'] == 'inactive']['timestamp_utc'].diff().dt.total_seconds().sum() / 60
            
            # Extrapolate for missing data
            extrapolation_factor = total_minutes / (active_minutes + inactive_minutes) if (active_minutes + inactive_minutes) > 0 else 1
            active_minutes *= extrapolation_factor
            inactive_minutes *= extrapolation_factor
            
            report_data.append({
                'store_id': store_id,
                f'uptime_{time_range}': active_minutes,
                f'downtime_{time_range}': inactive_minutes
            })

    # Create final report DataFrame
    report_df = pd.DataFrame(report_data)
    report_df = report_df.groupby('store_id').sum().reset_index()

    # Convert minutes to hours for day and week
    for time_range in ['last_day', 'last_week']:
        report_df[f'uptime_{time_range}'] /= 60
        report_df[f'downtime_{time_range}'] /= 60

    # Save report to CSV
    report_df.to_csv(f'reports/{report_id}.csv', index=False)

    # Update report status
    report = db.query(Report).filter(Report.id == report_id).first()
    report.status = "Complete"
    report.completed_at = datetime.utcnow()
    db.commit()
    db.close()

def filter_business_hours(data, business_hours):
    def is_within_business_hours(row):
        if pd.isna(row['local_time']):
            return False  # Exclude rows without local_time
        day = row['local_time'].weekday()
        time = row['local_time'].time()
        hours = business_hours[business_hours['day_of_week'] == day]
        if hours.empty:
            return True  # Assume 24/7 if no hours specified
        start = datetime.strptime(hours['start_time_local'].iloc[0], '%H:%M:%S').time()
        end = datetime.strptime(hours['end_time_local'].iloc[0], '%H:%M:%S').time()
        return start <= time <= end

    return data[data.apply(is_within_business_hours, axis=1)]

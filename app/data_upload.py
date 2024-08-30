import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Store, StoreStatus, BusinessHours
from .database import engine, SessionLocal
from datetime import datetime

def bulk_upload_data():
    db = SessionLocal()
    try:
        # Upload store status data
        status_df = pd.read_csv('data/store_status.csv')
        try:
            # Convert to datetime using mixed format to handle inconsistencies
            status_df['timestamp_utc'] = pd.to_datetime(status_df['timestamp_utc'], format='mixed', errors='coerce')
        except Exception as e:
            print(f"Error parsing 'timestamp_utc' in store status data: {str(e)}")
            return

        status_records = [
            StoreStatus(store_id=row['store_id'], timestamp_utc=row['timestamp_utc'], status=row['status'])
            for _, row in status_df.iterrows()
        ]
        db.bulk_save_objects(status_records)
        db.commit()
        print(f"Uploaded {len(status_records)} store status records")

        # Upload business hours data
        hours_df = pd.read_csv('data/business_hours.csv')
        hours_records = [
            BusinessHours(
                store_id=row['store_id'],
                day_of_week=row['day'],
                start_time_local=row['start_time_local'],
                end_time_local=row['end_time_local']
            )
            for _, row in hours_df.iterrows()
        ]
        db.bulk_save_objects(hours_records)
        db.commit()
        print(f"Uploaded {len(hours_records)} business hours records")

        # Upload timezone data
        timezone_df = pd.read_csv('data/timezones.csv')
        stores = [
            Store(id=row['store_id'], timezone_str=row['timezone_str'])
            for _, row in timezone_df.iterrows()
        ]
        db.bulk_save_objects(stores)
        db.commit()
        print(f"Uploaded {len(stores)} store records")

    except IntegrityError as e:
        db.rollback()
        print(f"Error during bulk upload: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    bulk_upload_data()

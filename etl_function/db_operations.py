import os
from datetime import datetime, UTC, timedelta

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor  # Import this for dictionary cursor

from secrets_manager import get_db_credentials

def get_db_connection():
    db_creds = get_db_credentials()
    return psycopg2.connect(
        dbname=db_creds['dbname'],
        user=db_creds['username'],
        password=db_creds['password'],
        host=db_creds['host'],
        options="-c search_path=public"
    )

def get_report_data():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Use RealDictCursor
            cur.execute("""
                SELECT stitch_report_id, accesswire_report_id, updated_at, accesswire_title, 
                       accesswire_release_type, pro_content_id, report_date
                FROM stg_accesswire_report
                ORDER BY report_date DESC
            """)
            return cur.fetchall()

def get_prev_day_reports():
    yesterday = (datetime.now(UTC) - timedelta(days=1)).date()
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT stitch_report_id, accesswire_report_id, updated_at, accesswire_title, 
                       accesswire_release_type, pro_content_id, report_date
                FROM stg_accesswire_report
                WHERE DATE(report_date) = %s
                ORDER BY report_date DESC
            """, (yesterday,))
            return cur.fetchall()

def get_most_recent_reports(last_processed_date = None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if last_processed_date is None: # get all
                return get_report_data()
            else:
                cur.execute("""
                    SELECT stitch_report_id, accesswire_report_id, updated_at, accesswire_title, 
                           accesswire_release_type, pro_content_id, report_date
                    FROM stg_accesswire_report
                    WHERE report_date > %s
                    ORDER BY report_date ASC
                """, (last_processed_date,))
                return cur.fetchall()


def get_distribution_data(stitch_report_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Use RealDictCursor
            cur.execute("""
                SELECT get_screenshot, stitch_report_id, distribution_category, 
                       article_url, distribution_point
                FROM stg_accesswire_distribution
                WHERE stitch_report_id = %s
            """, (stitch_report_id,))
            return cur.fetchall()
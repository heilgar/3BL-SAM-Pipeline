from secrets_manager import get_db_credentials
import psycopg2

def get_db_connection():
    db_creds = get_db_credentials()
    return psycopg2.connect(
        dbname=db_creds['dbname'],
        user=db_creds['username'],
        password=db_creds['password'],
        host=db_creds['host'],
        options="-c search_path=public"
    )
def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def handler(event, context):
    # Get DB credentials from Secrets Manager
    conn = get_db_connection()

    # Read SQL file
    sql_file_path = '/var/task/init.sql'
    sql_content = read_sql_file(sql_file_path)

    try:
        with conn.cursor() as cur:
            # Execute SQL commands
            cur.execute(sql_content)
        conn.commit()
        return {
            'StatusCode': 'SUCCESS',
            'PhysicalResourceId': context.log_stream_name
        }
    except Exception as e:
        print(f"Error executing SQL: {str(e)}")
        return {
            'StatusCode': 'FAILED',
            'Reason': str(e)
        }
    finally:
        conn.close()
import json
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
import db_operations
import urlbox_api
import json_transformer
from aws_operations import upload_file, upload_json, read_max_date, write_max_date
from multiprocessing import Pool
import uuid
import re
import unicodedata

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

def sanitize(name):
    """
    Convert to ASCII if 'allow_unicode' is False. Strip leading and trailing spaces,
    convert remaining spaces to underscores, and remove anything that is not an
    alphanumeric, dash, underscore, or dot.
    """
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'(?u)[^-\w.]', '_', name.strip().replace(' ', '_'))

def process_affiliate(affiliate, now):
    try:
        if affiliate['get_screenshot']:
            screenshot_content = urlbox_api.get_screenshot(affiliate['article_url'])
            unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of a UUID
            safe_name = sanitize(affiliate['affiliate_name'])
            screenshot_filename = f"{now.strftime('%Y%m%d%H%M%S')}_{unique_id}_{safe_name}.png"
            screenshot_key = f"screenshots/{screenshot_filename}"
            upload_file(screenshot_content, screenshot_key)
            affiliate['screenshot_filename'] = screenshot_filename
        return {'success': True, 'affiliate': affiliate}
    except Exception as e:
        print(f"Error processing affiliate: {affiliate['affiliate_name']}, Error: {str(e)}")
        return {'success': False, 'affiliate': affiliate, 'error': str(e)}

def upload_json_process(json_data, s3_key):
    try:
        upload_json(json_data, s3_key)
        return {'success': True, 'message': 'JSON uploaded successfully'}
    except Exception as e:
        print(f"Error uploading JSON: {str(e)}")
        return {'success': False, 'error': str(e)}

def handler(event, context):
    try:
        max_date = read_max_date()

        # Extract data from PostgreSQL
        all_report_data = db_operations.get_most_recent_reports(max_date)
        if not all_report_data:
            return {
                'statusCode': 200,
                'body': json.dumps('No report data found for the previous day')
            }

        all_responses = []

        for report_data in all_report_data:
            stitch_report_id = report_data['stitch_report_id']
            distribution_data = db_operations.get_distribution_data(stitch_report_id)

            max_date = report_data['report_date'] if max_date is None or report_data['report_date'] > max_date else max_date

            # Transform data into JSON
            json_data = json_transformer.transform_data(report_data, distribution_data)

            # Generate S3 key
            now = datetime.now(UTC)
            s3_key = f"bucket/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}/report_{stitch_report_id}_{now.strftime('%Y%m%d%H%M%S')}.json"

            # Use multiprocessing Pool to run tasks in parallel
            with Pool(processes=11) as pool:
                # Submit affiliate processing tasks
                affiliate_futures = pool.starmap_async(process_affiliate, [(affiliate, now) for affiliate in json_data['affiliates']])

                # Collect affiliate results
                affiliate_results = affiliate_futures.get()

            # Process affiliate results and update json_data
            successful_affiliates = []
            failed_affiliates = []
            for result in affiliate_results:
                if result['success']:
                    successful_affiliates.append(result['affiliate'])
                else:
                    failed_affiliates.append(result['affiliate'])

            # Update json_data with the processed affiliate information
            json_data['affiliates'] = successful_affiliates + failed_affiliates

            # Upload updated JSON
            json_result = upload_json_process(json_data, s3_key)

            response = {
                'stitch_report_id': stitch_report_id,
                'json_upload': 'successful' if json_result['success'] else 'failed',
                'successful_affiliates': len(successful_affiliates),
                'failed_affiliates': len(failed_affiliates),
            }

            if failed_affiliates:
                response['failed_affiliate_names'] = [aff['affiliate_name'] for aff in failed_affiliates]

            all_responses.append(response)


        write_max_date(max_date)

        return {
            'statusCode': 200,
            'body': json.dumps(all_responses)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Critical error: {str(e)}')
        }

# For local debugging
if __name__ == "__main__":
    print(lambda_handler(None, None))
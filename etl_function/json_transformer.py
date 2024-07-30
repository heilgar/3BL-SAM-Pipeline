from datetime import datetime

def transform_data(report_data, distribution_data):
    return {
        "report_id": str(report_data['accesswire_report_id']),
        "updated_at": report_data['updated_at'].isoformat(),
        "report_date": report_data['report_date'].isoformat(),
        "affiliates": [
            {
                "affiliate_name": dist['distribution_point'],
                "article_url": dist['article_url'],
                "description": "",
                "get_screenshot": dist['get_screenshot']
            }
            for dist in distribution_data
        ]
    }
# REQUIREMENTS
1. Using python for ETL and connecting to PostgreSQL
2. Understanding of AWS SAM and best practice for structuring Lambda functions written in python
3. Understanding of data transformations from database tables into JSON
4. Understanding of boto3 module and uploading files to S3
5. Ability to call API and store output
5. You must provide your own S3, lambda environment, Postgres connection, and urlbox account (they offer a free trial). DB schema and sample JSON output are attached in job details.



# THE GOAL
1. Use python to extract SQL data from a Postgres database, transform it into JSON, and output the result into an S3 bucket. Based on urls in the JSON output, request a viewport screenshot from https://urlbox.com/ and include the current timestamp on the screenshot.



# ACCEPTANCE CRITERIA
1. Correct SQL data is extracted from Postgres
2. Properly structured JSON outputted into S3 with dynamic date-based naming convention
3. Lambda function with SAM template, test case, and working python code
4. Sample screenshot loaded into S3 from urlbox.com



# DELIVERABLE
1. Packaged lambda function meeting acceptance criteria
2. Example of function output as JSON and urlbox screenshot link in S3.

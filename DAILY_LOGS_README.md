# Daily Logs Reporting System

This system automatically generates and uploads daily activity reports for employees to Amazon S3 with the following folder structure:

```
S3 Bucket: ddsfocustime
└── logs/
    └── 2025-09-10/                    (date folder)
        ├── employee1_at_company_com/   (employee folder)
        │   ├── daily_activity_report_2025-09-10_14-30-25.json
        │   └── daily_activity_report_2025-09-10_18-15-10.json
        └── employee2_at_company_com/
            └── daily_activity_report_2025-09-10_16-45-33.json
```

## Features

- **Automated Daily Reports**: Generate JSON reports containing employee daily activities
- **S3 Integration**: Upload reports to organized S3 folder structure
- **Batch Processing**: Process all employees at once or individually
- **Employee Summaries**: Get multi-day summaries for performance analysis
- **Web Interface**: Easy-to-use web dashboard for manual report generation
- **Automation Support**: Script for scheduled daily automation

## Files Added

### Core Modules
- `moduller/s3_uploader.py` - Enhanced with daily logs upload functions
- `moduller/daily_logs_reporter.py` - Main reporting logic and database integration
- `daily_logs_automation.py` - Automation script for scheduled runs
- `test_daily_logs.py` - Test script for functionality verification

### Web Interface
- `templates/daily_logs_manager.html` - Web dashboard for manual report generation

### API Endpoints Added to `app.py`
- `POST /generate_daily_logs_report` - Generate single employee report
- `POST /generate_all_daily_logs_reports` - Generate reports for all employees
- `POST /get_employee_logs_summary` - Get employee multi-day summary
- `GET /daily_logs_manager` - Access web dashboard

## Setup Requirements

### 1. AWS S3 Configuration
Ensure your S3 credentials are configured in your `config_manager.py` or environment variables:

```python
# In config_manager.py or environment variables
AWS_ACCESS_KEY_ID = "your_access_key"
AWS_SECRET_ACCESS_KEY = "your_secret_key"
S3_BUCKET_NAME = "ddsfocustime"
AWS_REGION = "us-east-1"
```

### 2. Database Connection
Make sure your database connection is working in `veritabani_yoneticisi.py`.

### 3. Required Python Packages
All required packages should already be installed if your main app is working:
- boto3
- datetime
- json
- pathlib

## Usage

### 1. Web Interface
1. Start your Flask app: `python app.py`
2. Navigate to: `http://localhost:5000/daily_logs_manager`
3. Use the web interface to:
   - Generate reports for individual employees
   - Generate reports for all employees
   - View employee summaries
   - Test S3 connection

### 2. API Usage

#### Generate Single Employee Report
```bash
curl -X POST http://localhost:5000/generate_daily_logs_report \
  -H "Content-Type: application/json" \
  -d '{
    "email": "employee@company.com",
    "date": "2025-09-10"
  }'
```

#### Generate All Employee Reports
```bash
curl -X POST http://localhost:5000/generate_all_daily_logs_reports \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-09-10"
  }'
```

#### Get Employee Summary
```bash
curl -X POST http://localhost:5000/get_employee_logs_summary \
  -H "Content-Type: application/json" \
  -d '{
    "email": "employee@company.com",
    "days_back": 7
  }'
```

### 3. Automation Script

#### Manual Execution
```bash
# Generate today's reports for all employees
python daily_logs_automation.py

# Generate yesterday's reports (useful for end-of-day automation)
python daily_logs_automation.py --yesterday

# Generate reports for specific date
python daily_logs_automation.py --date 2025-09-09

# Generate report for specific employee
python daily_logs_automation.py --email employee@company.com
```

#### Scheduled Automation

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily at desired time (e.g., 11:59 PM)
4. Set action to start program:
   - Program: `python`
   - Arguments: `"C:\path\to\daily_logs_automation.py" --yesterday`
   - Start in: `C:\path\to\project\folder`

**Linux/Mac Cron:**
```bash
# Add to crontab (crontab -e):
59 23 * * * cd /path/to/project && python daily_logs_automation.py --yesterday
```

## Report Structure

Each daily report JSON file contains:

```json
{
  "report_metadata": {
    "employee_email": "employee@company.com",
    "employee_name": "John Doe",
    "employee_id": 123,
    "report_date": "2025-09-10",
    "generated_at": "2025-09-10T18:30:45.123456",
    "total_tasks": 5
  },
  "daily_summary": {
    "total_working_hours": 8.5,
    "total_tasks_completed": 5,
    "first_task_start": "2025-09-10T09:00:00",
    "last_task_end": "2025-09-10T17:30:00", 
    "total_earnings": 255.0
  },
  "tasks": [
    {
      "task_id": 1,
      "task_reference_id": 101,
      "task_name": "Email Management",
      "start_time": "2025-09-10T09:00:00",
      "end_time": "2025-09-10T12:00:00",
      "duration_seconds": 10800,
      "duration_hours": 3.0,
      "note": "Handled customer emails",
      "hourly_rate": 30.0,
      "task_earnings": 90.0
    }
  ]
}
```

## Testing

Run the test script to verify functionality:

```bash
python test_daily_logs.py
```

This will test:
- S3 connection and upload functionality
- Database integration
- Batch upload capabilities
- API endpoint availability

## Troubleshooting

### Common Issues

1. **AWS Credentials Missing**
   - Ensure S3 credentials are properly configured
   - Check `config_manager.py` or environment variables

2. **Database Connection Failed**
   - Verify database connection in `veritabani_yoneticisi.py`
   - Check database credentials and network connectivity

3. **No Data Found**
   - Verify that timesheets data exists in the database
   - Check date format (YYYY-MM-DD)
   - Ensure employee email exists in staff table

4. **S3 Upload Failed**
   - Check S3 bucket permissions
   - Verify bucket name and region
   - Ensure AWS credentials have write permissions

### Debug Mode

Add logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Benefits

1. **Automated Reporting**: No manual intervention needed for daily reports
2. **Organized Storage**: Clean S3 folder structure for easy access
3. **Data Analytics**: JSON format allows easy data analysis
4. **Audit Trail**: Complete history of employee activities
5. **Performance Tracking**: Multi-day summaries for performance analysis
6. **Compliance**: Automatic record keeping for payroll and compliance

## Integration with Existing System

This system integrates seamlessly with your existing DDS Focus Pro application:

- Uses existing database tables (`timesheets`, `tasks`, `staff`)
- Uses existing S3 configuration from `config_manager.py`
- Follows existing logging patterns
- Compatible with current authentication system

The daily logs are stored separately from screenshots but use the same S3 bucket and credentials for consistency.

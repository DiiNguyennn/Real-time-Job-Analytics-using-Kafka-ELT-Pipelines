from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import json, logging
from linkedin_scraper import scrape_jobs
from kafka import KafkaProducer

# Cấu hình mặc định cho DAG
default_args = {
    'owner': 'dii',
    'start_date': datetime(2024, 3, 24, 8, 00)
}

# Hàm lấy dữ liệu công việc
def get_data():
    return scrape_jobs("Python","Ho Chi Minh",1)

# Hàm định dạng dữ liệu công việc
def format_job_data(job):
    return {
        'job_title': job.get('job_title'),
        'company_name': job.get('company_name'),
        'address': job.get('address'),
        'posted_time': job.get('posted_time'),
        'job_link': job.get('job_link'),
    }

# Hàm gửi dữ liệu đến Kafka
def stream_data():
    producer = KafkaProducer(bootstrap_servers=['broker:29092'])
    try:
        jobs = get_data()
        formatted_jobs = [format_job_data(job) for job in jobs]

        for job in formatted_jobs:
            producer.send('job_data', json.dumps(job).encode('utf-8'))

    except Exception as e:
        logging.error(f'An error occurred: {e}')

# Cấu hình DAG trong Airflow
with DAG('job_data_stream',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:
    
    streaming_task = PythonOperator(
        task_id='job_data_stream',
        python_callable=stream_data
    )

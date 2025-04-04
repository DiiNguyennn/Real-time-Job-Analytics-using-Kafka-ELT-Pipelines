import logging, uuid, re, shutil, os
from pyspark.sql.functions import udf, from_json, col
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from cassandra.cluster import Cluster
from datetime import datetime, timedelta

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cấu hình Cassandra
CASSANDRA_HOST = "cassandra" 
CASSANDRA_KEYSPACE = "career_opportunity"
CASSANDRA_TABLE = "job_data"

# Cấu hình Kafka
KAFKA_BROKER = "broker:29092"
KAFKA_TOPIC = "job_data"

def create_cassandra_connection():
    """Kết nối đến Cassandra và tạo keyspace nếu chưa có"""
    try:
        cluster = Cluster([CASSANDRA_HOST], protocol_version=5)
        session = cluster.connect()
        
        create_keyspace(session)
        session.set_keyspace(CASSANDRA_KEYSPACE)
        create_table(session)

        logging.info("Connected to Cassandra successfully!")
        return session
    except Exception as e:
        logging.error(f"Could not create Cassandra connection due to {e}")
        return None

def create_keyspace(session):
    """Tạo keyspace nếu chưa tồn tại"""
    try:
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}};
        """)
        logging.info("Keyspace created successfully!")
    except Exception as e:
        logging.error(f"Error creating keyspace: {e}")

def create_table(session):
    """Tạo bảng nếu chưa tồn tại"""
    try:
        session.execute(f"""
            CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
                id UUID PRIMARY KEY,
                job_title TEXT,
                company_name TEXT,
                address TEXT,
                posted_time TEXT,
                job_link TEXT
            );
        """)
        logging.info("Table created successfully!")
    except Exception as e:
        logging.error(f"Error creating table: {e}")

def insert_data(session, **kwargs):
    """Chèn dữ liệu vào Cassandra"""
    job_id = uuid.uuid4()
    try:
        session.execute(f"""
            INSERT INTO {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} 
            (id, job_title, company_name, address, posted_time, job_link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (job_id, kwargs.get("job_title"), kwargs.get("company_name"), kwargs.get("address"),
              kwargs.get("posted_time"), kwargs.get("job_link")))
        
        logging.info(f"Inserted job: {kwargs.get('job_title')} at {kwargs.get('company_name')}")
    except Exception as e:
        logging.error(f"Could not insert data due to {e}")

def create_spark_connection():
    """Tạo kết nối Spark"""
    try:
        spark = SparkSession.builder \
            .appName("CareerOpportunityDataStreaming") \
            .config("spark.jars", "/opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar,"
                    "/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar,"
                    "/opt/spark/jars/commons-pool2-2.11.1.jar,"
                    "/opt/spark/jars/kafka-clients-3.5.1.jar,"
                    "/opt/spark/jars/spark-unsafe_2.12-3.5.1.jar,"
                    "/opt/spark/jars/spark-streaming-kafka-0-10-assembly_2.12-3.5.1.jar") \
            .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
            .config("spark.cassandra.connection.port", "9042") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        logging.info("Spark session created successfully!")
        return spark
    except Exception as e:
        logging.error(f"Couldn't create the Spark session due to: {e}")
        return None

def connect_to_kafka(spark):
    try:
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()
        logging.info("Kafka DataFrame created successfully")
        return kafka_df
    except Exception as e:
        logging.warning(f"Kafka DataFrame could not be created: {e}")
        return None

def create_selection_df_from_kafka(kafka_df):
    """Xử lý dữ liệu Kafka, parse JSON"""
    uuid_udf = udf(lambda: str(uuid.uuid4()), StringType())

    schema = StructType([
        StructField("job_title", StringType(), True),
        StructField("company_name", StringType(), True),
        StructField("address", StringType(), True),
        StructField("posted_time", StringType(), True),
        StructField("job_link", StringType(), True)
    ])
    
    processed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("id", uuid_udf()) \
        .withColumn("posted_time", convert_relative_time_udf(col("posted_time"))) \
        .dropDuplicates(["job_link"])

    logging.info("Kafka data processed successfully!")
    return processed_df

def convert_relative_time(relative_time):
    """UDF chuyển đổi thời gian tương đối sang 'YYYY-MM-DD'"""
    if not isinstance(relative_time, str) or relative_time is None:
        return None

    today = datetime.today()
    match = re.match(r"(\d+)\s*(day|week|month|year)s?\s*ago", relative_time)
    
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit == "day":
            new_date = today - timedelta(days=value)
        elif unit == "week":
            new_date = today - timedelta(weeks=value)
        elif unit == "month":
            month = today.month - value
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            new_date = today.replace(year=year, month=month)
        elif unit == "year":
            new_date = today.replace(year=today.year - value)
        return new_date.strftime("%Y-%m-%d")
    return None

if __name__ == "__main__":
    # Xóa checkpoint cũ
    checkpoint_dir = "/tmp/checkpoint"
    if os.path.exists(checkpoint_dir):
        shutil.rmtree(checkpoint_dir)
        logging.info("Old checkpoint directory removed.")

    spark_conn = create_spark_connection()

    if spark_conn is not None:
        spark_df = connect_to_kafka(spark_conn)
        convert_relative_time_udf = udf(convert_relative_time, StringType())
        selection_df = create_selection_df_from_kafka(spark_df)
        session = create_cassandra_connection()
            
        if session is not None:
            create_keyspace(session)
            create_table(session)

            logging.info("Starting Spark Streaming to Cassandra...")
            streaming_query = (selection_df.writeStream
                .format("org.apache.spark.sql.cassandra")
                .option("checkpointLocation", "/tmp/checkpoint")
                .option("keyspace", CASSANDRA_KEYSPACE)
                .option("table", CASSANDRA_TABLE)
                .start()
            )
                        
            streaming_query.awaitTermination()
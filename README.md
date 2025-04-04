# 🏢 Real-time Job Analytics using Kafka ELT Pipelines

## 📌 Introduction

This project implements a **real-time job analytics system** using a **Kafka-based ELT pipeline**. The system collects, processes, and analyzes job market data in real time, enabling **insights into hiring trends, required skills, and job distributions**.

## 🔍 Research Scope

The project focuses on **real-time data ingestion, transformation, and storage** using:
- **Kafka**: Streaming job data in real time.
- **Apache Spark**: Transforming and analyzing job listings.
- **Apache Cassandra**: Storing large-scale job data efficiently.
- **Apache Airflow**: Automating the ELT workflow.

---

## 🛠 System Architecture

### 🔹 ELT Workflow
1. **Extract**
   - **Source**: Job APIs (LinkedIn, Indeed, VietnamWorks, TopCV, etc.).
   - **Format**: JSON data streamed into Kafka topics.

2. **Load**
   - **Storage**: Raw job data is **directly loaded into Cassandra**.

3. **Transform**
   - **Processing**: Using Apache Spark to clean and structure job data.
   - **Data Analysis**:
     - Job demand trends by industry and location.
     - Skill demand analysis across different job categories.
     - **Recruitment trends over the year**.

4. **Automation with Apache Airflow**
   - DAGs orchestrate job scheduling and pipeline execution.

---

## 🚀 Project Setup & Execution

### 1️⃣ Install Dependencies
- Install **Docker**: [Docker Installation Guide](https://docs.docker.com/get-docker/)
- Clone the repository:
  ```bash
  git clone https://github.com/DiiNguyennn/Real-time-Job-Analytics-using-Kafka-ELT-Pipelines.git
  cd Real-time-Job-Analytics-using-Kafka-ELT-Pipelines

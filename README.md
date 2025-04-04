# 🏢 Real-time Job Analytics using Kafka ELT Pipelines

## 📌 Introduction

This project implements a **real-time job analytics system** using a **Kafka-based ELT pipeline**. The system collects, processes, and analyzes job market data in real time, enabling **insights into hiring trends, required skills, and job distributions**.

## 🔍 Research Scope

The project focuses on **data ingestion, transformation, and analysis** using the following technologies:
- **Kafka**: Streaming job data in real time.
- **Apache Spark**: Transforming and analyzing job listings.
- **Apache Airflow**: Automating the ELT workflow.
- **SQL/NoSQL databases**: Storing processed data for analytics.

---

## 🛠 System Architecture

### 🔹 Data Flow Overview
1. **Data Extraction (Extract)**
   - **Source**: Job APIs (LinkedIn, Indeed, VietnamWorks, TopCV, etc.).
   - **Format**: JSON data streamed into Kafka topics.

2. **Data Transformation (Transform)**
   - **Data Cleaning**: Removing duplicates and missing values.
   - **Processing**: Parsing job details, normalizing text fields, and converting to structured format.

3. **Data Loading (Load)**
   - **Storage**: Processed data is saved into a database.
   - **Batch Queries**: Using Apache Spark for analytics.

4. **Data Analysis**
   - **Job demand trends** by industry and location.
   - **Skill demand analysis** across different job categories.
   - **Salary distribution** analysis.

5. **Automation with Apache Airflow**
   - DAGs orchestrate job scheduling and pipeline execution.

---

## 🚀 Project Setup & Execution

### 1️⃣ Install Dependencies
- Install **Docker**: [Docker Installation Guide](https://docs.docker.com/get-docker/)
- Clone the repository:
  ```bash
  git clone https://github.com/DiiNguyennn/Real-time-Job-Analytics-using-Kafka-ELT-Pipelines.git
  cd Real-time-Job-Analytics-using-Kafka-ELT-Pipelines

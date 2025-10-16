# RHO - Restaurant and Hospitality Operations Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Snowflake](https://img.shields.io/badge/snowflake-data%20warehouse-blue.svg)](https://snowflake.com)
[![Prefect](https://img.shields.io/badge/prefect-workflow%20orchestration-blue.svg)](https://prefect.io)

## Overview

RHO (Restaurant and Hospitality Operations) is a comprehensive data platform designed to streamline operations, analytics, and customer insights for restaurant and hospitality businesses. The platform integrates multiple data sources, provides real-time analytics, and enables data-driven decision making through automated ETL pipelines, advanced analytics, and interactive dashboards.

## 🏗️ Architecture

The RHO platform is built on a modern data stack with the following core components:

- **Data Warehouse**: Snowflake for scalable data storage and analytics
- **Workflow Orchestration**: Prefect for ETL pipeline management
- **Data Integration**: Custom Python pipelines for various data sources
- **Analytics**: Streamlit applications for interactive data exploration
- **Semantic Layer**: YAML-based data models for business intelligence

## 📁 Repository Structure

```
RHO/
├── DATABASE/                    # Snowflake database schemas and objects
│   ├── COSTAVIDA_DB_DEV/       # Development database
│   ├── COSTAVIDA_DB_PROD/      # Production database
│   └── ADMINDB/                # Administrative database
├── PYTHON/                     # ETL pipelines and data processing
│   ├── toast-orders-project/   # Toast POS order data integration
│   ├── toast-menus/            # Toast menu data processing
│   ├── qualtrics-import-project/ # Customer survey data
│   ├── medallia-import-project/  # Customer feedback platform
│   ├── google-analytics-project/ # Google Reviews integration
│   ├── fat-cats-project/       # Enhanced analytics and reporting
│   └── [additional projects]/  # Various data source integrations
├── STREAMLIT/                  # Interactive web applications
│   └── reviews_chatbot/        # AI-powered review analysis
├── UTILITIES/                  # Supporting tools and utilities
│   ├── Azure/                  # Azure cloud integrations
│   ├── Google/                 # Google services integration
│   └── DATA_POPULATION/        # Data seeding and testing tools
└── ddl_export/                 # Database schema exports
```

## 🗄️ Database Architecture

### Core Schemas

The platform uses a multi-schema approach in Snowflake:

- **ADMIN**: Configuration management and system administration
- **RAW**: Raw data ingestion from external sources
- **STAGE**: Data transformation and staging area
- **PUBLIC**: Business-ready data for analytics and reporting
- **LOAD**: Final processed data for consumption
- **QUALTRICS**: Customer survey and feedback data
- **RESTRICTED**: Sensitive data with restricted access
- **ALERTING**: System monitoring and alerting

### Key Features

- **Automated Deployment**: Master deployment scripts for consistent schema management
- **Stored Procedures**: Business logic encapsulated in Snowflake stored procedures
- **Data Lineage**: Clear data flow from RAW → STAGE → PUBLIC → LOAD
- **Security**: Role-based access control and data classification

## 🔄 ETL Pipelines

### Toast POS Integration

**Toast Orders Pipeline** (`toast-orders-project/`)
- Extracts order data from Toast POS API
- Handles multiple restaurant locations
- Implements automatic token refresh and retry logic
- Processes data through RAW → STAGE → LOAD pipeline

**Toast Menus Pipeline** (`toast-menus/`)
- Fetches menu data and pricing information
- Maintains product catalogs and menu hierarchies
- Supports menu versioning and change tracking

### Customer Feedback Integration

**Qualtrics Integration** (`qualtrics-import-project/`)
- Imports customer survey responses
- Processes guest satisfaction data
- Enables sentiment analysis and trend tracking

**Medallia Integration** (`medallia-import-project/`)
- Customer experience management platform integration
- Real-time feedback processing
- Automated alert generation for negative experiences

### External Data Sources

**Google Reviews** (`google-analytics-project/`)
- Automated review collection and analysis
- Sentiment analysis and rating trends
- Competitive benchmarking

**Weather Data** (from CONVX_Data_Platform)
- Historical weather patterns
- Forecast integration for business planning
- Impact analysis on customer behavior

## 🤖 AI and Analytics

### Semantic Layer

The platform includes a sophisticated semantic layer defined in YAML:

```yaml
# Example: Revenue Analytics Model
name: Revenue
tables:
  - name: daily_revenue
    measures:
      - name: daily_revenue
        expr: revenue
        default_aggregation: sum
      - name: daily_profit
        expr: revenue - cogs
    dimensions:
      - name: product_id
      - name: region_id
```

### Streamlit Applications

**Reviews Chatbot** (`STREAMLIT/reviews_chatbot/`)
- Natural language interface for review analysis
- AI-powered insights and recommendations
- Interactive data exploration

## 🛠️ Development and Deployment

### Prerequisites

- Python 3.11+
- Snowflake account with appropriate permissions
- Prefect server for workflow orchestration
- Docker for containerized deployments

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RHO
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Prefect blocks**:
   ```bash
   prefect block register -m prefect_snowflake
   ```

4. **Set up Snowflake credentials**:
   ```bash
   prefect block create snowflake-credentials
   ```

### Running Pipelines

**Local Development**:
```bash
python PYTHON/toast-orders-project/toast_orders_flow.py
```

**Prefect Deployment**:
```bash
python PYTHON/toast-orders-project/deploy_toast_orders_flow.py
prefect deployment run 'toast-orders-deployment'
```

**Docker Deployment**:
```bash
docker build -t rho-pipeline .
docker run rho-pipeline
```

## 📊 Key Features

### Data Integration
- **Multi-source ETL**: Toast POS, Qualtrics, Medallia, Google Reviews
- **Real-time Processing**: Near real-time data ingestion and processing
- **Error Handling**: Comprehensive retry logic and error recovery
- **Data Quality**: Validation and cleansing at each pipeline stage

### Analytics and Reporting
- **Interactive Dashboards**: Streamlit-based analytics applications
- **Semantic Layer**: Business-friendly data models and metrics
- **AI-Powered Insights**: Natural language querying and analysis
- **Automated Reporting**: Scheduled reports and alerts

### Operational Excellence
- **Monitoring**: Comprehensive logging and alerting
- **Scalability**: Cloud-native architecture with auto-scaling
- **Security**: Role-based access control and data encryption
- **Compliance**: Data governance and audit trails

## 🔧 Utilities and Tools

### Azure Integration (`UTILITIES/Azure/`)
- Azure Data Factory pipeline management
- Cloud storage integration
- Automated deployment scripts

### Google Services (`UTILITIES/Google/`)
- Google Places API integration
- Google Analytics data extraction
- OAuth authentication management

### Data Population (`UTILITIES/DATA_POPULATION/`)
- Test data generation
- Schema validation tools
- Performance testing utilities

## 📈 Monitoring and Observability

### Prefect Monitoring
- Flow execution tracking
- Task-level monitoring
- Performance metrics and alerts

### Snowflake Monitoring
- Query performance analysis
- Resource utilization tracking
- Data pipeline health checks

### Application Logging
- Structured logging across all components
- Error tracking and alerting
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Include comprehensive tests
- Update documentation for new features
- Use Prefect for all ETL workflows
- Implement proper error handling and logging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the documentation in individual project folders
2. Review Prefect flow logs for pipeline issues
3. Consult Snowflake query history for database problems
4. Open an issue in the repository

## 🚀 Roadmap

- [ ] Enhanced AI/ML capabilities for predictive analytics
- [ ] Real-time streaming data processing
- [ ] Advanced customer segmentation and personalization
- [ ] Mobile application for field operations
- [ ] Integration with additional POS systems
- [ ] Advanced data visualization and BI tools

---

**Built with ❤️ for the restaurant and hospitality industry**

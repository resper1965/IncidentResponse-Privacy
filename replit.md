# LGPD Compliance Dashboard

## Overview

This is a Python-based LGPD (Lei Geral de Proteção de Dados) compliance system that automatically scans documents for personal data, extracts and classifies the information, and provides a dashboard for analysis. The system uses regex patterns, spaCy NLP for named entity recognition, and provides OCR capabilities for scanned documents.

## System Architecture

The application follows a modular pipeline architecture with the following key components:

- **File Scanner**: Recursively scans directories for supported file formats
- **File Reader**: Extracts text from multiple document formats including OCR for PDFs
- **Data Extractor**: Uses regex patterns and spaCy NLP to identify personal data and data subjects
- **Database Layer**: SQLite database for storing extracted data with LGPD compliance focus
- **Dashboard**: Streamlit-based web interface for data visualization and analysis

## Key Components

### File Processing Pipeline
- **file_scanner.py**: Handles recursive directory traversal and file discovery
- **file_reader.py**: Multi-format document text extraction (TXT, PDF, DOCX, XLSX, CSV, MSG)
- **data_extractor.py**: Personal data identification using regex and NLP

### Data Management
- **database.py**: SQLite database operations with LGPD-specific schema
- **main.py**: Main orchestration pipeline that coordinates all components

### User Interface
- **web_interface.py**: Flask web application with modern dashboard for data visualization and compliance reporting
- **templates/dashboard.html**: HTML template with elegant design and real-time processing status

### Supported File Formats
- Plain text files (.txt)
- PDF documents (.pdf) with OCR support
- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- CSV files (.csv)
- Outlook emails (.msg)

## Data Flow

1. **Document Discovery**: File scanner recursively searches the `data/` directory
2. **Text Extraction**: File reader extracts text content from various document formats
3. **Data Identification**: Regex patterns identify Brazilian personal data (CPF, RG, email, phone, etc.)
4. **Context Analysis**: System captures 150-character context windows around identified data
5. **Subject Identification**: Uses keyword matching and spaCy NER to identify data subjects
6. **Classification**: Automatically classifies data priority (high priority for CPF, RG, email, phone)
7. **Storage**: Saves extracted data to SQLite database with metadata
8. **Visualization**: Dashboard provides compliance overview and detailed analysis

## External Dependencies

### Core Libraries
- **streamlit**: Web dashboard framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualization
- **sqlite3**: Database operations
- **spacy**: Natural language processing and NER
- **pdfplumber**: PDF text extraction
- **python-docx**: Word document processing
- **extract-msg**: Outlook email processing
- **pytesseract**: OCR capabilities
- **PIL**: Image processing

### NLP Models
- **pt_core_news_lg**: Large Portuguese spaCy model (primary)
- **pt_core_news_sm**: Small Portuguese spaCy model (fallback)

## Deployment Strategy

The application is designed for Replit deployment with the following considerations:

- **Database**: Uses SQLite for simplicity and no external database requirements
- **File Storage**: Local file system storage in `data/` directory
- **Dependencies**: All dependencies listed in requirements.txt for easy installation
- **Configuration**: Minimal configuration required, with fallback mechanisms for missing components

### Database Schema
```sql
dados_extraidos (
    id INTEGER PRIMARY KEY,
    arquivo TEXT NOT NULL,
    titular TEXT NOT NULL,
    campo TEXT NOT NULL,
    valor TEXT NOT NULL,
    contexto TEXT,
    prioridade TEXT,
    origem_identificacao TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Key Features
- **Automated Data Subject Identification**: Uses contextual keywords and NLP
- **Three-Tier Priority Classification**: Categorizes data as Alta, Média, or Baixa criticality per LGPD
- **Priority Company Search**: Configurable enterprise ranking system with domain filtering
- **Comprehensive Reporting**: Dashboard with statistics, Excel export, and detailed compliance views
- **Brazilian Compliance Focus**: Regex patterns optimized for Brazilian document formats
- **Multi-format Support**: Handles common business document formats
- **OCR Integration**: Processes scanned documents and images
- **Real-time Processing Monitoring**: Progress tracking with file-by-file status updates

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **June 27, 2025**: Initial LGPD compliance system setup
- **June 27, 2025**: Enhanced dashboard with elegant modern design using Inter font and gradient styling
- **June 27, 2025**: Added directory selection feature for document scanning with custom path support
- **June 27, 2025**: Implemented priority company classification system with predefined enterprise list including BRADESCO, PETROBRAS, ONS, EMBRAER, REDE DOR, ED GLOBO, GLOBO, ELETROBRAS, CREFISA, EQUINIX, COHESITY, NETAPP, HITACHI, LENOVO
- **June 27, 2025**: Added enterprise management interface with add/remove functionality and contact information tracking
- **June 27, 2025**: Replaced Streamlit with Flask web interface per user request
- **June 27, 2025**: Updated data pipeline to save results in Excel-compatible format with domain/company filtering
- **June 27, 2025**: Added real-time processing status monitoring with progress bars and file tracking
- **June 27, 2025**: Implemented custom directory selection for complete file tree processing
- **June 27, 2025**: Implemented three-tier criticality classification (Alta, Média, Baixa) based on LGPD guidelines
- **June 27, 2025**: Added criticality classification dashboard tab showing data sensitivity categorization
- **June 27, 2025**: Updated priority search management with BRADESCO as priority 1 (@bradesco.com.br)
- **June 27, 2025**: Enhanced regex patterns management interface with intelligent structure validation
- **June 27, 2025**: Implemented priority-based processing logic with enterprise pre-analysis
- **June 27, 2025**: Created advanced AI processor with intelligent document classification
- **June 27, 2025**: Added IA Avançada dashboard tab showcasing next evolution steps
- **June 27, 2025**: Integrated dual-criteria company identification (name + email domain)

## Priority Company Classification

The system now includes a sophisticated priority company classification feature that automatically identifies when personal data belongs to major enterprises. This enhances LGPD compliance monitoring for high-priority business relationships.

### Enterprise Database Schema
```sql
empresas_prioritarias (
    id INTEGER PRIMARY KEY,
    nome_empresa TEXT UNIQUE,
    observacoes TEXT,
    email_contato TEXT,
    ativa BOOLEAN,
    data_criacao TIMESTAMP
)
```

### Key Features
- **Automatic Detection**: System automatically flags data from priority companies during extraction
- **Enterprise Management**: Dashboard interface for adding, editing, and removing priority companies
- **Contact Tracking**: Email addresses and notes for each priority enterprise
- **Compliance Monitoring**: Enhanced reporting for high-priority business data
- **Predefined List**: Includes major Brazilian corporations and international technology companies

## Changelog

Changelog:
- June 27, 2025. Initial setup
- June 27, 2025. Added elegant dashboard design with modern UI components
- June 27, 2025. Implemented directory selection and priority company classification
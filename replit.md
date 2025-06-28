# n.crisisops - Privacy Module

## Overview

This is "n.crisisops - gestão de resposta a incidente" (privacy module), a comprehensive LGPD (Lei Geral de Proteção de Dados) compliance system that automatically scans documents for personal data, extracts sensitive information, and provides enterprise-grade analysis with AI-powered prioritization. The system is designed for organizations that need to identify and manage personal data across large document repositories while maintaining compliance with Brazilian data protection laws.

## System Architecture

The application follows a sophisticated multi-layer pipeline architecture with enterprise features:

### Core Architecture Pattern
- **Modular Pipeline Design**: Each processing stage is isolated and can be independently scaled
- **Dual Database Strategy**: PostgreSQL for enterprise deployments with SQLite fallback for development
- **AI-Enhanced Processing**: Three-layer AI processing (Regex → spaCy NER → LLM)
- **Priority-Based Processing**: Enterprise client prioritization with configurable search priorities
- **Async Processing Support**: Built for high-volume document processing with parallel execution

### Processing Layers
1. **Layer 1**: Regex-based pattern matching for structured data (CPF, RG, email, phone)
2. **Layer 2**: spaCy Named Entity Recognition for unstructured data and entity relationships
3. **Layer 3**: Large Language Model integration (OpenAI GPT) for semantic analysis and complex document understanding

## Key Components

### Document Processing Pipeline
- **file_scanner.py**: Recursive directory traversal with support for 18+ file formats
- **file_reader.py**: Multi-format text extraction with OCR capabilities (PDF, DOCX, XLSX, CSV, TXT, MSG, EML, RTF, etc.)
- **data_extractor.py**: Personal data identification using Brazilian-specific regex patterns and spaCy NLP
- **ai_processor_simplified.py**: Simplified AI processor for basic deployments
- **ai_super_processor.py**: Advanced AI processor with LangChain integration for enterprise deployments

### Data Management Layer
- **database.py**: SQLite operations for development and fallback scenarios
- **database_postgresql.py**: Enterprise PostgreSQL implementation with advanced AI priority management
- **Hybrid Database Strategy**: Automatic fallback from PostgreSQL to SQLite based on availability

### AI and Machine Learning
- **spaCy Integration**: Portuguese language model (pt_core_news_lg/sm) for named entity recognition
- **LangChain Framework**: Integration with OpenAI models for semantic document analysis
- **Priority Intelligence**: AI-driven dynamic priority adjustment based on document content and client importance

### Web Interface
- **web_interface.py**: Flask application with modern responsive design
- **templates/dashboard.html**: Professional dashboard with n.crisisops branding
- **Real-time Processing**: Async document processing with live status updates

### Enterprise Features
- **Client Priority Management**: Configurable priority table for enterprise clients (Bradesco, Petrobras, ONS, etc.)
- **Domain-based Identification**: Automatic client identification through email domain matching
- **Compliance Reporting**: LGPD-specific reporting and data classification
- **Export Capabilities**: Excel export for compliance documentation

## Data Flow

### Primary Processing Pipeline
1. **Discovery Phase**: File scanner identifies documents in target directories
2. **Text Extraction**: Multi-format readers extract text content with OCR support
3. **Pattern Recognition**: Regex patterns identify Brazilian personal data types
4. **Context Analysis**: 150-character context windows capture surrounding information
5. **Entity Recognition**: spaCy NER identifies data subjects and relationships
6. **AI Analysis**: LLM provides semantic understanding for complex documents
7. **Priority Classification**: Enterprise priority system determines processing order
8. **Data Storage**: Structured storage with metadata and compliance flags
9. **Reporting**: Dashboard provides real-time analysis and compliance status

### AI Enhancement Flow
- **Automatic Escalation**: Documents that can't be processed by regex/spaCy are escalated to LLM
- **Confidence Scoring**: Each extraction receives confidence scores from AI layers
- **Dynamic Priority**: AI adjusts processing priority based on content sensitivity and client importance

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for dashboard interface
- **SQLAlchemy**: Database ORM for PostgreSQL operations
- **pandas**: Data manipulation and analysis
- **spaCy**: Natural language processing and named entity recognition
- **pdfplumber**: PDF text extraction
- **python-docx**: Word document processing
- **openpyxl**: Excel file handling
- **pytesseract**: OCR for scanned documents

### AI and ML Dependencies
- **langchain**: LLM framework for advanced AI processing
- **langchain-openai**: OpenAI model integration
- **openai**: Direct OpenAI API access

### Enterprise Dependencies
- **psycopg2-binary**: PostgreSQL database connectivity
- **gunicorn**: Production WSGI server
- **asyncpg**: Async PostgreSQL operations

### File Processing Dependencies
- **extract-msg**: Outlook email file processing
- **beautifulsoup4**: HTML parsing and cleaning
- **pillow**: Image processing for OCR

## Deployment Strategy

### Production Environment
- **Target Platform**: Ubuntu/CentOS VPS with systemd service management
- **Web Server**: Nginx reverse proxy with SSL termination
- **Application Server**: Gunicorn with 4 workers
- **Database**: PostgreSQL for production, SQLite for development
- **Service User**: Dedicated 'privacy' system user
- **Installation Path**: `/opt/privacy`
- **Domain**: Configurable (example: monster.e-ness.com.br)

### Configuration Management
- **Environment Variables**: OpenAI API keys and database credentials via .env
- **Service Configuration**: Systemd service with automatic restart
- **SSL Support**: Certbot integration for HTTPS
- **Log Management**: Structured logging with rotation

### Scalability Considerations
- **Async Processing**: ThreadPoolExecutor for concurrent document processing
- **Database Optimization**: Indexed queries for large document sets
- **Memory Management**: Chunked processing for large files
- **AI Rate Limiting**: Configurable LLM usage to manage API costs

## Changelog

- June 27, 2025. Initial setup
- June 27, 2025. Repository organization - Created professional structure with scripts/ and docs/ folders, comprehensive README.md, and resolved production deployment dependencies
- June 27, 2025. Git repository optimization - Resolved 172MB pack history issue, removed large files, optimized .gitignore, maintained VPS link
- June 27, 2025. VPS dependency fixes - Updated production-requirements.txt to eml-parser==2.0.0, created comprehensive dependency installation scripts for VPS deployment, resolved PyMuPDF import issues
- June 28, 2025. Production deployment with SSL - Created complete deploy-production.sh with Let's Encrypt SSL automation, staging environment setup, PostgreSQL production credentials (privacy_user:Lgpd2025#Privacy), and comprehensive security headers
- June 28, 2025. Final production system - Resolved LangChain dependency conflicts, streamlined deployment to single script, cleaned repository structure, system ready for VPS deployment with automatic SSL
- June 28, 2025. LangChain dependency resolution - Fixed critical dependency conflicts by updating production-requirements.txt to use compatible version ranges (>=0.2.2,<0.3.0), resolved PyMuPDF import issues, system fully operational with web interface running on port 5000
- June 28, 2025. VPS deployment optimization - Updated LangChain dependencies to use precise version ranges (langchain-core>=0.2.43,<0.3.0, langchain>=0.2.17,<0.3.0) for VPS compatibility, added requirements.in for pip-tools management, enhanced deployment script with lockfile generation
- June 28, 2025. VPS dependency conflict resolution - Created fix-vps-dependencies.sh script to resolve langchain-text-splitters version conflict (0.2.17-0.3.0 range unavailable), updated to use available versions (>=0.2.4), provided fallback installation method for production deployment
- June 28, 2025. Definitive VPS deployment solution - Created deploy-vps-final.sh that installs LangChain dependencies in specific order to avoid pip resolution conflicts, uses tested compatible versions (langchain-core==0.2.43, langchain-text-splitters==0.2.4), bypasses pip-tools completely, includes complete SSL automation and production configuration
- June 28, 2025. Complete production deployment - Resolved missing asyncpg module causing Gunicorn worker failures, fixed Nginx port conflicts with other sites, created single deploy-complete.sh script that installs all dependencies (PyMuPDF, asyncpg, psycopg2-binary), configures services correctly, and establishes full HTTPS functionality at monster.e-ness.com.br

## User Preferences

Preferred communication style: Simple, everyday language.
# n.crisisops - Módulo de Privacidade

## Overview

This is "n.crisisops - gestão de resposta a incidente" (privacy module), a comprehensive LGPD (Lei Geral de Proteção de Dados) compliance system designed for enterprise-scale document processing and personal data identification. The system automatically scans documents across multiple formats, identifies personal data using advanced AI techniques, and provides compliance reporting through a modern web interface.

## System Architecture

The application follows a modular, multi-layer architecture designed for scalability and reliability:

### Frontend Architecture
- **Flask Web Application**: Modern responsive dashboard with tabbed interface
- **HTML Templates**: Bootstrap-based UI with n.crisisops branding
- **Real-time Processing**: AJAX-based document processing with progress indicators
- **Export Capabilities**: Excel export functionality for compliance reporting

### Backend Architecture
- **Pipeline Processing**: Orchestrated document processing pipeline with error handling
- **Multi-format File Reading**: Supports 18+ document formats including OCR for scanned PDFs
- **AI-Enhanced Analysis**: Three-layer AI processing (Regex → spaCy NLP → LLM)
- **Priority Management**: Enterprise client prioritization system

### Data Processing Pipeline
1. **File Discovery**: Recursive directory scanning with format filtering
2. **Text Extraction**: Multi-format document processing with fallback mechanisms
3. **Data Identification**: Pattern matching and named entity recognition
4. **Context Analysis**: Contextual window extraction around identified data
5. **Classification**: Automated LGPD criticality assessment
6. **Storage**: Dual database system with PostgreSQL and SQLite fallback

## Key Components

### Core Processing Modules
- **file_scanner.py**: Recursive directory traversal and file discovery engine
- **file_reader.py**: Multi-format text extraction with OCR support (PDF, DOCX, XLSX, CSV, MSG, TXT, etc.)
- **data_extractor.py**: Brazilian personal data identification using regex patterns and spaCy NLP
- **main.py**: Main orchestration pipeline coordinating all processing components

### AI Enhancement Layer
- **ai_enhanced_processor.py**: Advanced AI processor with enterprise prioritization
- **ai_processor_simplified.py**: Simplified AI processor for demonstration without external dependencies
- **ai_super_processor.py**: Multi-layer semantic analysis with LangChain integration and GPT models

### Database Layer
- **database.py**: SQLite database operations with LGPD-specific schema design
- **database_postgresql.py**: PostgreSQL integration for enterprise-scale deployment
- **Hybrid Database Strategy**: Automatic fallback from PostgreSQL to SQLite for reliability

### Web Interface
- **web_interface.py**: Flask application with modern dashboard and real-time processing
- **templates/dashboard.html**: Responsive HTML template with tabbed interface and data visualization

### Supported File Formats
- Plain text (.txt)
- PDF documents (.pdf) with OCR capability
- Microsoft Word (.docx)
- Excel spreadsheets (.xlsx)
- CSV files (.csv)
- Outlook emails (.msg)
- PowerPoint (.pptx)
- RTF documents (.rtf)
- HTML files (.html)
- XML files (.xml)
- JSON files (.json)

## Data Flow

1. **Document Discovery**: File scanner recursively searches target directories with format filtering
2. **Text Extraction**: Multi-format file reader extracts text content with OCR fallback for images
3. **Data Identification**: 
   - Layer 1: Regex pattern matching for Brazilian personal data (CPF, RG, email, phone, etc.)
   - Layer 2: spaCy NER for entity recognition and context analysis
   - Layer 3: LLM-based semantic analysis for complex data relationships
4. **Context Capture**: System extracts 150-character context windows around identified data points
5. **Subject Identification**: Keyword matching and NLP to identify data subjects/titulars
6. **Priority Classification**: Automatic LGPD criticality assessment (Alta, Média, Baixa)
7. **Enterprise Prioritization**: Client-based processing priority with configurable weightings
8. **Storage**: Dual database storage with metadata and compliance tracking
9. **Visualization**: Real-time dashboard with filtering, export, and compliance reporting

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for the dashboard interface
- **SQLite3**: Primary database for data storage and retrieval
- **PostgreSQL**: Enterprise database option with asyncpg driver
- **pandas**: Data manipulation and Excel export functionality
- **pdfplumber/PyMuPDF**: PDF text extraction and processing
- **python-docx**: Microsoft Word document processing
- **openpyxl**: Excel file reading and writing
- **Pillow/pytesseract**: OCR functionality for scanned documents

### AI/ML Dependencies
- **spaCy**: Natural language processing and named entity recognition
- **LangChain**: LLM integration framework with OpenAI GPT models
- **langchain-openai**: OpenAI integration for advanced AI analysis
- **langchain-community**: Community extensions for document processing
- **transformers**: Optional Hugging Face model support

### Additional Libraries
- **BeautifulSoup4**: HTML parsing and content extraction
- **extract-msg**: Outlook MSG file processing
- **eml-parser**: Email file format parsing
- **striprtf**: RTF document processing
- **python-dotenv**: Environment variable management

## Deployment Strategy

### Production Environment
- **Target Server**: VPS with Ubuntu/CentOS
- **Application Directory**: `/opt/privacy`
- **Service Management**: systemd service configuration
- **Web Server**: Nginx reverse proxy with SSL termination
- **WSGI Server**: Gunicorn with optimized worker configuration

### Configuration Management
- **Environment Variables**: OpenAI API keys and database credentials
- **SSL Certificate**: Let's Encrypt with automatic renewal
- **Database Initialization**: Automated schema creation and data population
- **Service Monitoring**: Health checks and log management

### Fallback Strategy
- **Database Fallback**: Automatic SQLite fallback if PostgreSQL unavailable
- **AI Processing Fallback**: Graceful degradation from full AI to regex-only processing
- **File Processing Resilience**: Multiple extraction methods with error recovery

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
- June 28, 2025. Database merge and priority system - Successfully applied database merge consolidating 10 enterprise search priorities in PostgreSQL, created setup_priorities.py and merge_database.py scripts for priority management, system now fully unified on PostgreSQL with automatic client prioritization for LGPD compliance processing
- June 28, 2025. Complete VPS navigation system - Resolved PostgreSQL connection issues with URL-encoded passwords, implemented full directory navigation API endpoints (/api/listar-diretorios, /api/validar-diretorio), added interactive file browser with JavaScript frontend, created comprehensive VPS configuration scripts (fix-postgresql-vps.sh, update-env-vps.sh, test-navigation-vps.sh), system ready for production with complete file tree navigation at monster.e-ness.com.br
- June 28, 2025. System status verification and repository cleanup - Fixed PostgreSQL status verification using psycopg2 synchronous connections instead of asyncpg for Flask compatibility, added python-dotenv for proper .env loading, cleaned repository by removing duplicate files, temporary scripts, and cached files, organized deployment scripts in scripts/ folder, system fully operational with clean codebase
- June 28, 2025. Production deployment scripts and import fixes - Resolved critical import error 'cannot import name encontrar_arquivos' by correcting function name to listar_arquivos_recursivos, created comprehensive VPS installation scripts (install-vps-complete.sh, install-vps-simples.sh), added detailed diagnostic logging for file processing, system ready for Git deployment with complete VPS automation

## User Preferences

Preferred communication style: Simple, everyday language.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL database management for enterprise-scale LGPD system
Implements advanced AI priority management and real-time processing
"""

import os
import asyncio
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
Base = declarative_base()

class SearchPriorityTable(Base):
    """Enhanced search priority table with AI capabilities"""
    __tablename__ = 'search_priority'
    
    id = Column(Integer, primary_key=True)
    priority = Column(Integer, nullable=False, unique=True)
    client_name = Column(String(255), nullable=False)
    email_domain = Column(String(255), nullable=False)
    ai_escalation_enabled = Column(Boolean, default=True)
    confidence_threshold = Column(Float, default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)

class DocumentProcessingQueue(Base):
    """Document processing queue with AI-enhanced priority management"""
    __tablename__ = 'document_queue'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    identified_client = Column(String(255))
    static_priority = Column(Integer)
    ai_adjusted_priority = Column(Integer)
    ai_confidence_score = Column(Float)
    processing_status = Column(String(50), default='pending')  # pending, processing, completed, error
    semantic_classification = Column(String(100))
    priority_source = Column(String(50))  # regex, spacy, llm, manual
    escalation_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    ai_metadata = Column(JSON)

class ExtractedDataEnhanced(Base):
    """Enhanced extracted data with AI analysis and provenance"""
    __tablename__ = 'extracted_data_enhanced'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    client_name = Column(String(255))
    email_domain = Column(String(255))
    data_type = Column(String(100), nullable=False)
    data_value = Column(Text, nullable=False)
    context_window = Column(Text)
    confidence_score = Column(Float)
    extraction_method = Column(String(50))  # regex, spacy, llm
    sensitivity_level = Column(String(20))  # alta, media, baixa
    ai_validation_score = Column(Float)
    semantic_tags = Column(JSON)
    compliance_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

class AIProcessingLog(Base):
    """Comprehensive AI processing audit log"""
    __tablename__ = 'ai_processing_log'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    processing_layer = Column(String(50))  # layer1_regex, layer2_spacy, layer3_llm
    operation_type = Column(String(100))
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    ai_model_version = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class RealTimeMetrics(Base):
    """Real-time system performance and processing metrics"""
    __tablename__ = 'realtime_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    metric_data = Column(JSON)
    client_name = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """PostgreSQL database manager for enterprise LGPD system"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.async_pool = None
    
    async def initialize_database(self):
        """Initialize PostgreSQL database with all tables"""
        try:
            # Create synchronous connection
            self.engine = create_engine(DATABASE_URL)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Create async connection pool
            self.async_pool = await asyncpg.create_pool(DATABASE_URL)
            
            print("✅ PostgreSQL database initialized successfully")
            await self._load_default_priorities()
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    async def _load_default_priorities(self):
        """Load default search priorities if table is empty"""
        session = self.Session()
        try:
            count = session.query(SearchPriorityTable).count()
            if count == 0:
                default_priorities = [
                    (1, "BRADESCO", "bradesco.com.br"),
                    (2, "PETROBRAS", "petrobras.com.br"),
                    (3, "ONS", "ons.org.br"),
                    (4, "EMBRAER", "embraer.com.br"),
                    (5, "REDE DOR", "rededorsaoluiz.com.br"),
                    (6, "GLOBO", "globo.com"),
                    (7, "ELETROBRAS", "eletrobras.com"),
                    (8, "CREFISA", "crefisa.com.br"),
                    (9, "EQUINIX", "equinix.com"),
                    (10, "COHESITY", "cohesity.com")
                ]
                
                for priority, name, domain in default_priorities:
                    entry = SearchPriorityTable(
                        priority=priority,
                        client_name=name,
                        email_domain=domain
                    )
                    session.add(entry)
                
                session.commit()
                print("✅ Default search priorities loaded")
        except Exception as e:
            print(f"❌ Error loading default priorities: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def get_search_priorities(self) -> List[Dict]:
        """Get all search priorities ordered by priority"""
        session = self.Session()
        try:
            priorities = session.query(SearchPriorityTable)\
                               .filter(SearchPriorityTable.active == True)\
                               .order_by(SearchPriorityTable.priority).all()
            
            return [{
                'id': p.id,
                'priority': p.priority,
                'client_name': p.client_name,
                'email_domain': p.email_domain,
                'ai_escalation_enabled': p.ai_escalation_enabled,
                'confidence_threshold': p.confidence_threshold
            } for p in priorities]
        finally:
            session.close()
    
    async def add_document_to_queue(self, file_path: str, file_name: str, 
                                   file_size: int = None) -> int:
        """Add document to processing queue"""
        session = self.Session()
        try:
            doc = DocumentProcessingQueue(
                file_path=file_path,
                file_name=file_name,
                file_size=file_size
            )
            session.add(doc)
            session.commit()
            return doc.id
        finally:
            session.close()
    
    async def update_document_priority(self, doc_id: int, client_name: str,
                                     static_priority: int, ai_priority: int = None,
                                     confidence: float = None, source: str = None,
                                     escalation_reason: str = None):
        """Update document priority with AI analysis"""
        session = self.Session()
        try:
            doc = session.query(DocumentProcessingQueue).filter_by(id=doc_id).first()
            if doc:
                doc.identified_client = client_name
                doc.static_priority = static_priority
                doc.ai_adjusted_priority = ai_priority or static_priority
                doc.ai_confidence_score = confidence
                doc.priority_source = source
                doc.escalation_reason = escalation_reason
                session.commit()
        finally:
            session.close()
    
    async def get_processing_queue(self, status: str = 'pending') -> List[Dict]:
        """Get documents from processing queue ordered by AI-adjusted priority"""
        session = self.Session()
        try:
            docs = session.query(DocumentProcessingQueue)\
                         .filter(DocumentProcessingQueue.processing_status == status)\
                         .order_by(DocumentProcessingQueue.ai_adjusted_priority).all()
            
            return [{
                'id': d.id,
                'file_path': d.file_path,
                'file_name': d.file_name,
                'identified_client': d.identified_client,
                'static_priority': d.static_priority,
                'ai_adjusted_priority': d.ai_adjusted_priority,
                'ai_confidence_score': d.ai_confidence_score,
                'priority_source': d.priority_source,
                'escalation_reason': d.escalation_reason
            } for d in docs]
        finally:
            session.close()
    
    async def log_ai_processing(self, doc_id: int, layer: str, operation: str,
                              input_data: Dict, output_data: Dict,
                              confidence: float = None, processing_time: int = None,
                              error: str = None):
        """Log AI processing operations for audit trail"""
        session = self.Session()
        try:
            log_entry = AIProcessingLog(
                document_id=doc_id,
                processing_layer=layer,
                operation_type=operation,
                input_data=input_data,
                output_data=output_data,
                confidence_score=confidence,
                processing_time_ms=processing_time,
                error_message=error
            )
            session.add(log_entry)
            session.commit()
        finally:
            session.close()
    
    async def save_extracted_data(self, doc_id: int, client_name: str,
                                email_domain: str, data_type: str, data_value: str,
                                context: str, confidence: float, method: str,
                                sensitivity: str, ai_validation: float = None,
                                semantic_tags: Dict = None):
        """Save extracted data with AI analysis"""
        session = self.Session()
        try:
            extracted = ExtractedDataEnhanced(
                document_id=doc_id,
                client_name=client_name,
                email_domain=email_domain,
                data_type=data_type,
                data_value=data_value,
                context_window=context,
                confidence_score=confidence,
                extraction_method=method,
                sensitivity_level=sensitivity,
                ai_validation_score=ai_validation,
                semantic_tags=semantic_tags
            )
            session.add(extracted)
            session.commit()
            return extracted.id
        finally:
            session.close()
    
    async def update_metrics(self, metric_name: str, value: float, 
                           data: Dict = None, client: str = None):
        """Update real-time metrics"""
        session = self.Session()
        try:
            metric = RealTimeMetrics(
                metric_name=metric_name,
                metric_value=value,
                metric_data=data,
                client_name=client
            )
            session.add(metric)
            session.commit()
        finally:
            session.close()
    
    async def get_dashboard_metrics(self) -> Dict:
        """Get real-time dashboard metrics"""
        session = self.Session()
        try:
            # Processing queue statistics
            total_pending = session.query(DocumentProcessingQueue)\
                                  .filter_by(processing_status='pending').count()
            
            total_processing = session.query(DocumentProcessingQueue)\
                                    .filter_by(processing_status='processing').count()
            
            total_completed = session.query(DocumentProcessingQueue)\
                                   .filter_by(processing_status='completed').count()
            
            # AI escalations
            ai_escalations = session.query(DocumentProcessingQueue)\
                                   .filter(DocumentProcessingQueue.ai_adjusted_priority < 
                                          DocumentProcessingQueue.static_priority).count()
            
            # Top clients by volume
            client_stats = session.query(DocumentProcessingQueue.identified_client,
                                        session.query(DocumentProcessingQueue)\
                                        .filter_by(identified_client=DocumentProcessingQueue.identified_client)\
                                        .count().label('count'))\
                                 .group_by(DocumentProcessingQueue.identified_client)\
                                 .order_by(text('count DESC')).limit(5).all()
            
            return {
                'queue_stats': {
                    'pending': total_pending,
                    'processing': total_processing,
                    'completed': total_completed
                },
                'ai_escalations': ai_escalations,
                'top_clients': [{'client': c[0], 'documents': c[1]} for c in client_stats if c[0]]
            }
        finally:
            session.close()
    
    async def close(self):
        """Close database connections"""
        if self.async_pool:
            await self.async_pool.close()
        if self.engine:
            self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()

# Helper functions for backward compatibility
async def initialize_postgresql():
    """Initialize PostgreSQL database"""
    return await db_manager.initialize_database()

async def get_search_priorities():
    """Get search priorities"""
    return await db_manager.get_search_priorities()

async def add_to_processing_queue(file_path: str, file_name: str):
    """Add document to processing queue"""
    return await db_manager.add_document_to_queue(file_path, file_name)

if __name__ == "__main__":
    async def test_database():
        """Test database functionality"""
        print("=== TESTING POSTGRESQL DATABASE ===")
        
        # Initialize database
        success = await initialize_postgresql()
        if success:
            print("✅ Database initialized")
            
            # Test search priorities
            priorities = await get_search_priorities()
            print(f"✅ Loaded {len(priorities)} search priorities")
            
            # Test queue operations
            doc_id = await add_to_processing_queue("/test/file.pdf", "test.pdf")
            print(f"✅ Added document to queue: ID {doc_id}")
            
            # Test metrics
            metrics = await db_manager.get_dashboard_metrics()
            print(f"✅ Dashboard metrics: {metrics}")
        
        await db_manager.close()
    
    asyncio.run(test_database())
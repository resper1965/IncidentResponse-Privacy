#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified AI processor for demonstration without external dependencies
"""

import os
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import re

# Local imports
from file_reader import extrair_texto
from data_extractor import REGEX_PATTERNS
from database_postgresql import db_manager

class SimpleAIProcessor:
    """Simplified AI processor for demonstration"""
    
    def __init__(self):
        self.patterns = REGEX_PATTERNS
        
    async def process_layer1_regex(self, text: str, doc_id: int) -> List[Dict]:
        """Layer 1: Regex-based personal data extraction"""
        start_time = time.time()
        results = []
        
        try:
            for data_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    value = match.group().strip()
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(text), match.end() + 100)
                    context = text[context_start:context_end]
                    
                    result = {
                        'data_type': data_type,
                        'value': value,
                        'context': context,
                        'confidence': 0.9,
                        'method': 'regex_simple',
                        'position': (match.start(), match.end())
                    }
                    results.append(result)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer1_regex",
                operation="data_extraction",
                input_data={"text_length": len(text)},
                output_data={"matches_found": len(results)},
                confidence=0.9,
                processing_time=processing_time
            )
            
            return results
            
        except Exception as e:
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer1_regex",
                operation="data_extraction",
                input_data={"text_length": len(text)},
                output_data={},
                error=str(e)
            )
            return []

    async def analyze_document_sensitivity(self, text: str) -> float:
        """Simple keyword-based sensitivity analysis"""
        sensitive_keywords = [
            'dados pessoais', 'cpf', 'rg', 'confidencial', 
            'sigilo', 'privacidade', 'lgpd', 'sensível',
            'documento interno', 'reservado', 'restrito'
        ]
        
        text_lower = text.lower()
        keyword_matches = sum(1 for kw in sensitive_keywords if kw in text_lower)
        
        # Calculate sensitivity score (0.0 to 1.0)
        sensitivity = min(keyword_matches * 0.15, 1.0)
        return sensitivity

class SimplePriorityManager:
    """Simplified priority management system"""
    
    def __init__(self):
        self.search_priorities = {}
        self.ai_processor = SimpleAIProcessor()
        
    async def initialize(self):
        """Initialize priority manager"""
        await self.load_search_priorities()
        
    async def load_search_priorities(self):
        """Load search priorities from database"""
        try:
            priorities = await db_manager.get_search_priorities()
            self.search_priorities = {
                p['client_name']: p for p in priorities
            }
            print(f"Loaded {len(self.search_priorities)} search priorities")
        except Exception as e:
            print(f"Error loading priorities: {e}")
            self.search_priorities = {}
    
    async def identify_client_in_document(self, text: str, doc_id: int) -> Tuple[str, int, float]:
        """Identify client using name and email domain detection"""
        best_client = "Unknown"
        best_priority = 999
        best_confidence = 0.0
        
        text_upper = text.upper()
        
        for client_name, priority_info in self.search_priorities.items():
            confidence = 0.0
            
            # Check client name presence
            if client_name.upper() in text_upper:
                confidence += 0.6
            
            # Check email domain presence
            email_domain = priority_info['email_domain']
            email_pattern = rf'\b[a-zA-Z0-9._%+-]+@{re.escape(email_domain)}\b'
            if re.search(email_pattern, text, re.IGNORECASE):
                confidence += 0.8
            
            # Partial name matching
            name_words = client_name.upper().split()
            word_matches = sum(1 for word in name_words if word in text_upper)
            if word_matches > 0:
                confidence += (word_matches / len(name_words)) * 0.4
            
            # Select best match
            if confidence > 0.3 and priority_info['priority'] < best_priority:
                best_client = client_name
                best_priority = priority_info['priority']
                best_confidence = confidence
        
        return best_client, best_priority, best_confidence
    
    async def process_document_simple(self, file_path: str, doc_id: int) -> Dict:
        """Process document through simplified AI system"""
        
        # Extract text
        text = extrair_texto(file_path)
        if not text:
            return {'error': 'Failed to extract text'}
        
        # Identify client
        client_name, static_priority, client_confidence = await self.identify_client_in_document(text, doc_id)
        
        # Layer 1: Regex extraction
        layer1_results = await self.ai_processor.process_layer1_regex(text, doc_id)
        
        # Simple sensitivity analysis
        sensitivity_score = await self.ai_processor.analyze_document_sensitivity(text)
        
        # Calculate priority adjustment
        priority_adjustment = 0
        if sensitivity_score > 0.8:
            priority_adjustment = -50  # High priority
        elif sensitivity_score > 0.6:
            priority_adjustment = -20  # Medium priority
        elif sensitivity_score > 0.4:
            priority_adjustment = -5   # Slight boost
        
        final_priority = static_priority + priority_adjustment
        
        # Escalation reason
        escalation_reason = ""
        if sensitivity_score > 0.8:
            escalation_reason = f"High sensitivity detected: {sensitivity_score:.2f}"
        elif priority_adjustment < 0:
            escalation_reason = f"Priority boost applied: {priority_adjustment}"
        
        # Update database
        await db_manager.update_document_priority(
            doc_id=doc_id,
            client_name=client_name,
            static_priority=static_priority,
            ai_priority=final_priority,
            confidence=max(client_confidence, sensitivity_score),
            source=f"simple_ai_{sensitivity_score:.2f}",
            escalation_reason=escalation_reason or "No escalation"
        )
        
        # Save extracted data
        for data in layer1_results:
            await db_manager.save_extracted_data(
                doc_id=doc_id,
                client_name=client_name,
                email_domain=self.search_priorities.get(client_name, {}).get('email_domain', ''),
                data_type=data['data_type'],
                data_value=data['value'],
                context=data['context'],
                confidence=data['confidence'],
                method=data['method'],
                sensitivity=self._classify_sensitivity(data['data_type']),
                ai_validation=client_confidence,
                semantic_tags=[]
            )
        
        return {
            'client_name': client_name,
            'static_priority': static_priority,
            'ai_adjusted_priority': final_priority,
            'escalation_reason': escalation_reason,
            'layer1_extractions': len(layer1_results),
            'sensitivity_score': sensitivity_score,
            'processing_complete': True
        }
    
    def _classify_sensitivity(self, data_type: str) -> str:
        """Classify data sensitivity level"""
        alta_sensitivity = ['cpf', 'rg', 'telefone', 'email', 'data_nascimento']
        media_sensitivity = ['cep', 'placa_veiculo', 'ip']
        
        if data_type in alta_sensitivity:
            return 'alta'
        elif data_type in media_sensitivity:
            return 'media'
        else:
            return 'baixa'

# Global instances
simple_priority_manager = SimplePriorityManager()

async def initialize_simple_ai_system():
    """Initialize the simplified AI system"""
    await db_manager.initialize_database()
    await simple_priority_manager.initialize()

async def process_document_simple_ai(file_path: str) -> Dict:
    """Process a single document with simplified AI"""
    # Add to queue
    doc_id = await db_manager.add_document_to_queue(file_path, os.path.basename(file_path))
    
    # Process with simplified AI
    result = await simple_priority_manager.process_document_simple(file_path, doc_id)
    
    return result

if __name__ == "__main__":
    async def test_simple_system():
        """Test the simplified AI system"""
        print("=== TESTING SIMPLIFIED AI SYSTEM ===")
        
        await initialize_simple_ai_system()
        
        # Get dashboard metrics
        metrics = await db_manager.get_dashboard_metrics()
        print(f"Dashboard metrics: {metrics}")
        
        await db_manager.close()
    
    asyncio.run(test_simple_system())
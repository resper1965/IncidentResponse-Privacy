#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Super Processor with LangChain integration
Multi-layer semantic analysis with dynamic priority adjustment
"""

import os
import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import re

# AI and ML imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
import spacy

# Local imports
from file_reader import extrair_texto
from data_extractor import REGEX_PATTERNS, inicializar_spacy
from database_postgresql import db_manager

class AILayerProcessor:
    """Multi-layer AI processing engine"""
    
    def __init__(self):
        self.layer1_patterns = REGEX_PATTERNS
        self.layer2_nlp = None
        self.layer3_llm = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        
    async def initialize(self):
        """Initialize all AI layers"""
        print("🔄 Initializing AI layers...")
        
        # Layer 2: spaCy NER
        try:
            self.layer2_nlp = spacy.load("pt_core_news_sm")
            print("✅ Layer 2 (spaCy NER) initialized")
        except:
            print("⚠️ spaCy model not available, using fallback")
            self.layer2_nlp = None
        
        # Layer 3: LLM (OpenAI)
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            try:
                self.layer3_llm = ChatOpenAI(
                    model="gpt-3.5-turbo-1106",  # User specified model
                    temperature=0.1,
                    openai_api_key=openai_key
                )
                print("✅ Layer 3 (LLM) initialized with GPT-3.5-turbo-1106")
            except Exception as e:
                print(f"⚠️ LLM initialization failed: {e}")
                self.layer3_llm = None
        else:
            print("⚠️ OPENAI_API_KEY not found, Layer 3 disabled")
    
    async def process_layer1_regex(self, text: str, doc_id: int) -> List[Dict]:
        """Layer 1: Regex-based personal data extraction"""
        start_time = time.time()
        results = []
        
        try:
            for data_type, pattern in self.layer1_patterns.items():
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
                        'confidence': 0.9,  # High confidence for regex
                        'method': 'layer1_regex',
                        'position': (match.start(), match.end())
                    }
                    results.append(result)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Log processing
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
    
    async def process_layer2_spacy(self, text: str, doc_id: int, 
                                 client_context: str = None) -> Dict:
        """Layer 2: spaCy NER for entity recognition and client validation"""
        start_time = time.time()
        
        if not self.layer2_nlp:
            return {'entities': [], 'client_confidence': 0.0}
        
        try:
            # Process text with spaCy
            doc = self.layer2_nlp(text[:1000000])  # Limit text size
            
            entities = []
            for ent in doc.ents:
                if ent.label_ in ['PER', 'ORG', 'MISC']:  # Person, Organization, Miscellaneous
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': 0.8
                    })
            
            # Client validation if context provided
            client_confidence = 0.0
            if client_context:
                client_mentions = sum(1 for ent in entities 
                                    if client_context.upper() in ent['text'].upper())
                client_confidence = min(client_mentions * 0.3, 1.0)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'entities': entities,
                'client_confidence': client_confidence,
                'processing_time': processing_time
            }
            
            # Log processing
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer2_spacy",
                operation="entity_recognition",
                input_data={"text_length": len(text), "client_context": client_context},
                output_data={"entities_found": len(entities), "client_confidence": client_confidence},
                confidence=client_confidence,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer2_spacy",
                operation="entity_recognition",
                input_data={"text_length": len(text)},
                output_data={},
                error=str(e)
            )
            return {'entities': [], 'client_confidence': 0.0}
    
    async def process_layer3_llm(self, text: str, doc_id: int,
                               client_context: str = None) -> Dict:
        """Layer 3: LLM semantic analysis for sensitive content detection"""
        start_time = time.time()
        
        if not self.layer3_llm:
            return {'sensitivity_score': 0.0, 'critical_clauses': [], 'priority_adjustment': 0}
        
        try:
            # Split text into manageable chunks
            chunks = self.text_splitter.split_text(text)
            
            all_critical_clauses = []
            max_sensitivity = 0.0
            
            for chunk in chunks[:3]:  # Limit to first 3 chunks for cost control
                
                system_prompt = """You are an AI specialized in LGPD (Brazilian Data Protection Law) compliance analysis. 
                Analyze the provided text for:
                1. Sensitive personal data clauses
                2. Critical compliance issues
                3. Data processing agreements
                4. Privacy policy violations
                5. High-risk data handling
                
                Respond with a JSON object containing:
                - sensitivity_score: float (0.0 to 1.0)
                - critical_clauses: list of sensitive text snippets
                - compliance_concerns: list of LGPD concerns
                - priority_recommendation: string (immediate, high, normal, low)
                """
                
                human_prompt = f"""
                Document context: {client_context or 'Unknown client'}
                
                Text to analyze:
                {chunk}
                
                Provide analysis in JSON format only.
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt)
                ]
                
                try:
                    response = await asyncio.to_thread(
                        self.layer3_llm.invoke, messages
                    )
                    
                    # Parse LLM response
                    response_text = response.content.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:-3]
                    elif response_text.startswith('```'):
                        response_text = response_text[3:-3]
                    
                    analysis = json.loads(response_text)
                    
                    sensitivity = analysis.get('sensitivity_score', 0.0)
                    if sensitivity > max_sensitivity:
                        max_sensitivity = sensitivity
                    
                    critical_clauses = analysis.get('critical_clauses', [])
                    all_critical_clauses.extend(critical_clauses)
                    
                except json.JSONDecodeError:
                    # Fallback: simple keyword analysis
                    sensitive_keywords = [
                        'dados pessoais', 'cpf', 'rg', 'confidencial', 
                        'sigilo', 'privacidade', 'lgpd', 'sensível'
                    ]
                    
                    chunk_lower = chunk.lower()
                    keyword_matches = sum(1 for kw in sensitive_keywords if kw in chunk_lower)
                    sensitivity = min(keyword_matches * 0.2, 1.0)
                    
                    if sensitivity > max_sensitivity:
                        max_sensitivity = sensitivity
            
            # Determine priority adjustment
            priority_adjustment = 0
            if max_sensitivity > 0.85:
                priority_adjustment = -50  # Immediate processing
            elif max_sensitivity > 0.7:
                priority_adjustment = -20  # High priority
            elif max_sensitivity > 0.5:
                priority_adjustment = -5   # Slight boost
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'sensitivity_score': max_sensitivity,
                'critical_clauses': all_critical_clauses[:5],  # Limit output
                'priority_adjustment': priority_adjustment,
                'processing_time': processing_time
            }
            
            # Log processing
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer3_llm",
                operation="semantic_analysis",
                input_data={"text_length": len(text), "chunks_processed": len(chunks)},
                output_data=result,
                confidence=max_sensitivity,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            await db_manager.log_ai_processing(
                doc_id=doc_id,
                layer="layer3_llm",
                operation="semantic_analysis",
                input_data={"text_length": len(text)},
                output_data={},
                error=str(e)
            )
            return {'sensitivity_score': 0.0, 'critical_clauses': [], 'priority_adjustment': 0}

class HybridPriorityManager:
    """Hybrid priority management system with AI escalation"""
    
    def __init__(self):
        self.search_priorities = {}
        self.ai_processor = AILayerProcessor()
        
    async def initialize(self):
        """Initialize priority manager and AI layers"""
        await self.ai_processor.initialize()
        await self.load_search_priorities()
        
    async def load_search_priorities(self):
        """Load search priorities from database"""
        priorities = await db_manager.get_search_priorities()
        self.search_priorities = {
            p['client_name']: p for p in priorities
        }
        print(f"✅ Loaded {len(self.search_priorities)} search priorities")
    
    async def identify_client_in_document(self, text: str, doc_id: int) -> Tuple[str, int, float]:
        """Identify client using name and email domain detection"""
        best_client = None
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
    
    async def process_document_with_ai(self, file_path: str, doc_id: int) -> Dict:
        """Process document through all AI layers with priority management"""
        
        # Extract text
        text = extrair_texto(file_path)
        if not text:
            return {'error': 'Failed to extract text'}
        
        # Identify client
        client_name, static_priority, client_confidence = await self.identify_client_in_document(text, doc_id)
        
        # Layer 1: Regex extraction
        layer1_results = await self.ai_processor.process_layer1_regex(text, doc_id)
        
        # Layer 2: spaCy NER
        layer2_results = await self.ai_processor.process_layer2_spacy(text, doc_id, client_name)
        
        # Layer 3: LLM semantic analysis
        layer3_results = await self.ai_processor.process_layer3_llm(text, doc_id, client_name)
        
        # Calculate final priority
        ai_priority_adjustment = layer3_results.get('priority_adjustment', 0)
        final_priority = static_priority + ai_priority_adjustment
        
        # Escalation logic
        escalation_reason = None
        if layer3_results.get('sensitivity_score', 0) > 0.85:
            escalation_reason = f"High sensitivity detected: {layer3_results.get('sensitivity_score'):.2f}"
        elif ai_priority_adjustment < -10:
            escalation_reason = f"AI recommended priority boost: {ai_priority_adjustment}"
        
        # Update database
        await db_manager.update_document_priority(
            doc_id=doc_id,
            client_name=client_name or "Unknown",
            static_priority=static_priority,
            ai_priority=final_priority,
            confidence=max(client_confidence, layer3_results.get('sensitivity_score', 0)),
            source=f"hybrid_ai_{layer3_results.get('sensitivity_score', 0):.2f}",
            escalation_reason=escalation_reason
        )
        
        # Save extracted data
        for data in layer1_results:
            await db_manager.save_extracted_data(
                doc_id=doc_id,
                client_name=client_name or "Unknown",
                email_domain=self.search_priorities.get(client_name, {}).get('email_domain', ''),
                data_type=data['data_type'],
                data_value=data['value'],
                context=data['context'],
                confidence=data['confidence'],
                method=data['method'],
                sensitivity=self._classify_sensitivity(data['data_type']),
                ai_validation=layer2_results.get('client_confidence', 0),
                semantic_tags=layer3_results.get('critical_clauses', [])
            )
        
        return {
            'client_name': client_name,
            'static_priority': static_priority,
            'ai_adjusted_priority': final_priority,
            'escalation_reason': escalation_reason,
            'layer1_extractions': len(layer1_results),
            'layer2_entities': len(layer2_results.get('entities', [])),
            'layer3_sensitivity': layer3_results.get('sensitivity_score', 0),
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
priority_manager = HybridPriorityManager()

async def initialize_ai_system():
    """Initialize the complete AI system"""
    await db_manager.initialize_database()
    await priority_manager.initialize()

async def process_document_with_hybrid_ai(file_path: str) -> Dict:
    """Process a single document with hybrid AI priority management"""
    # Add to queue
    doc_id = await db_manager.add_document_to_queue(file_path, os.path.basename(file_path))
    
    # Process with AI
    result = await priority_manager.process_document_with_ai(file_path, doc_id)
    
    return result

if __name__ == "__main__":
    async def test_ai_system():
        """Test the AI system"""
        print("=== TESTING HYBRID AI PRIORITY SYSTEM ===")
        
        await initialize_ai_system()
        
        # Test document processing
        test_files = ["data/exemplo_contrato.txt", "data/exemplo_email.txt"]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\n🔄 Processing: {file_path}")
                result = await process_document_with_hybrid_ai(file_path)
                print(f"✅ Result: {result}")
        
        # Get dashboard metrics
        metrics = await db_manager.get_dashboard_metrics()
        print(f"\n📊 Dashboard metrics: {metrics}")
        
        await db_manager.close()
    
    asyncio.run(test_ai_system())
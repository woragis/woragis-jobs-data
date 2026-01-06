"""
Kafka consumer for job application events
"""
import json
from typing import Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import structlog
from app.config import settings
from app.database.base import SessionLocal
from app.domains.analytics.service import AnalyticsService
from app.domains.recommendations.service import RecommendationService
from app.domains.company_dedup.service import CompanyDeduplicationService

logger = structlog.get_logger()


class JobApplicationConsumer:
    """Consumer for job application events from jobs service"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'job-applications.created',
            'job-applications.updated',
            'job-applications.status-changed',
            'interviews.added',
            'responses.received',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            group_id=settings.KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        self.db = SessionLocal()
    
    def start(self):
        """Start consuming messages"""
        logger.info("Starting Kafka consumer", group_id=settings.KAFKA_GROUP_ID)
        
        try:
            for message in self.consumer:
                try:
                    self.process_message(message.topic, message.value)
                except Exception as e:
                    logger.error(
                        "Error processing message",
                        topic=message.topic,
                        error=str(e),
                        exc_info=True
                    )
        except KafkaError as e:
            logger.error("Kafka error", error=str(e), exc_info=True)
        finally:
            self.consumer.close()
            self.db.close()
    
    def process_message(self, topic: str, data: Dict[str, Any]):
        """Process a single message"""
        logger.info("Processing message", topic=topic, application_id=data.get('application_id'))
        
        event_type = topic.replace('job-applications.', '').replace('.', '_')
        
        if event_type == 'created':
            self.handle_application_created(data)
        elif event_type == 'updated':
            self.handle_application_updated(data)
        elif event_type == 'status_changed':
            self.handle_status_changed(data)
        elif topic == 'interviews.added':
            self.handle_interview_added(data)
        elif topic == 'responses.received':
            self.handle_response_received(data)
    
    def handle_application_created(self, data: Dict[str, Any]):
        """Handle application created event"""
        from uuid import UUID
        
        # Deduplicate company
        dedup_service = CompanyDeduplicationService(self.db)
        company_id, is_new = dedup_service.find_or_create_company(
            data.get('company_name', ''),
            data.get('location', ''),
            data.get('company_size')
        )
        
        # Update company metrics (will be minimal for new company)
        analytics_service = AnalyticsService(self.db)
        # We'd need to fetch all applications for this company from jobs service
        # For now, we'll update when we have more data
        
        logger.info(
            "Application created processed",
            application_id=data.get('application_id'),
            company_id=str(company_id),
            is_new_company=is_new
        )
    
    def handle_application_updated(self, data: Dict[str, Any]):
        """Handle application updated event"""
        # Recalculate recommendations if needed
        logger.info("Application updated", application_id=data.get('application_id'))
    
    def handle_status_changed(self, data: Dict[str, Any]):
        """Handle status changed event"""
        # Update company and user metrics
        analytics_service = AnalyticsService(self.db)
        # Would need to fetch and update metrics
        logger.info("Status changed", application_id=data.get('application_id'))
    
    def handle_interview_added(self, data: Dict[str, Any]):
        """Handle interview added event"""
        # Update metrics and recommendations
        logger.info("Interview added", application_id=data.get('application_id'))
    
    def handle_response_received(self, data: Dict[str, Any]):
        """Handle response received event"""
        # Update response time metrics
        logger.info("Response received", application_id=data.get('application_id'))


def start_consumer():
    """Start the Kafka consumer (called from main or separate process)"""
    consumer = JobApplicationConsumer()
    consumer.start()


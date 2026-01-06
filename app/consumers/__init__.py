"""
Kafka Consumers
"""
from app.consumers.kafka_consumer import JobApplicationConsumer, start_consumer

__all__ = ['JobApplicationConsumer', 'start_consumer']

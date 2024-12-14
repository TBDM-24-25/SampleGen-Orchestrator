from orchestrator.services.config import SchemaRegistryConfig

from confluent_kafka.schema_registry import SchemaRegistryClient

class SchemaRegistryService():

    def __init__(self):
        schema_registry_config = SchemaRegistryConfig()
        self.sr_conf = {
            'url': schema_registry_config.schema_registry_url
            }
        # initialize as SchemaRegistryClient
        self.sr_client = SchemaRegistryClient(self.sr_conf)

    def get_client(self):
        return self.sr_client

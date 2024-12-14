from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

class AvroService:

    def __init__(self, schema_registry_client: SchemaRegistryClient, schema: str):
        self.avro_serializer = AvroSerializer(schema_registry_client,
                                              schema,
                                              lambda obj, ctx: obj)

        self.avro_deserializer = AvroDeserializer(schema_registry_client,
                                                  schema,
                                                  lambda obj, ctx: obj)

    def get_avro_serializer(self):
        return self.avro_serializer

    def get_avro_deserializer(self):
        return self.avro_deserializer

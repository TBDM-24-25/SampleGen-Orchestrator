from datetime import datetime
from pydantic import BaseModel, model_validator
from typing import List, Optional


class Job(BaseModel):
    id: int
    schema: str
    data_type: str
    topic: str
    user: str
    status: str
    created_at: datetime
    updated_at: datetime
    

# Schema models
class UserCredentials(BaseModel):
    token: Optional[str]
    username: Optional[str]
    password: Optional[str]

    @model_validator(mode='after')
    def check_username_password(self):
        if self.token and (self.username or self.password):
            raise ValueError('If token is provided, username and password must not be provided')
        if not self.token and (not self.username or not self.password):
            raise ValueError('username and password are required if token is not provided')
        return self

class ContainerRegistry(BaseModel):
    url: str
    type: str
    user_credentials: UserCredentials

class ResourceLimits(BaseModel):
    cpu: float
    memory: str

class RetryPolicy(BaseModel):
    retry_on_failure: bool
    number_of_retries: int
    backoff_period_in_ms: int

class Ports(BaseModel):
    host_port: int
    container_port: int

class EnvironmentVariable(BaseModel):
    name: str
    value: str

class Metadata(BaseModel):
    user: str
    job_id: str
    created_at: str
    requested_at: str
    run_at: str
    description: str

class SchemaData(BaseModel):
    data_type: str
    topic: str
    operation: str
    container_image_name: str
    container_registry: ContainerRegistry
    computation_duration_in_seconds: int
    resource_limits: ResourceLimits
    retry_policy: RetryPolicy
    ports: Ports
    environment_variables: List[EnvironmentVariable]
    metadata: Metadata
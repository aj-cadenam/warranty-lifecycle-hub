import uuid
from dataclasses import dataclass, field

@dataclass
class BaseEntity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

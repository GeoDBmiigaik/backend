from sqlalchemy.orm import registry

mapper_registry = registry()
mapped = mapper_registry.mapped
metadata = mapper_registry.metadata

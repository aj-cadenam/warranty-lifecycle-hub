import uuid
import pytest
from src.shared.domain.base import BaseEntity


def test_base_entity_tiene_id_unico():
    """BaseEntity debe generar un ID único para cada instancia"""
    entity1 = BaseEntity()
    entity2 = BaseEntity()
    assert entity1.id != entity2.id


def test_base_entity_acepta_id_existente():
    """BaseEntity debe aceptar un ID proporcionado"""
    custom_id = str(uuid.uuid4())
    entity = BaseEntity(id=custom_id)
    assert entity.id == custom_id


def test_base_entity_id_es_uuid_valido():
    """El ID de BaseEntity debe ser un UUID válido"""
    entity = BaseEntity()
    # Debe poder convertir el string a UUID sin errores
    uuid_obj = uuid.UUID(entity.id)
    assert str(uuid_obj) == entity.id

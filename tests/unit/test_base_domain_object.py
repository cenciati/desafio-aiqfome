import pytest
from uuid import UUID, uuid4

from app.__core__.domain.entity.base_domain_object import BaseDomainObject


@pytest.mark.unit
class TestBaseDomainObject:
    def test_should_return_uuid_string(self):
        obj_id = uuid4()
        obj = BaseDomainObject(id=obj_id)
        assert obj.str_id == str(obj_id)
        assert isinstance(obj.str_id, str)

    def test_should_generate_id_default(self):
        obj = BaseDomainObject()
        assert isinstance(obj.id, UUID)

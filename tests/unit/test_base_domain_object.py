from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from app.__core__.domain.entity.base_domain_object import BaseDomainObject


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseDomainObjectStub(BaseDomainObject):
    test_attr: str


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

    def test_should_replace_attributes(self):
        obj = BaseDomainObjectStub(test_attr="test")

        new_obj = obj._replace(test_attr="test2")

        assert obj.test_attr == "test"
        assert new_obj.test_attr == "test2"

import dataclasses
import datetime
import enum
import unittest
from typing import Annotated, Dict, List, Optional

from devsecops_engine_tools.engine_utilities.utils.alias import Alias
from devsecops_engine_tools.engine_utilities.utils.dataclass_classmethod import (
    FromDictMixin,
)


# ---------------------------------------------------------------------------
# Helper types used across multiple tests
# ---------------------------------------------------------------------------

class Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


@dataclasses.dataclass
class Child(FromDictMixin):
    name: str = ""
    value: int = 0


@dataclasses.dataclass
class Simple(FromDictMixin):
    label: str = ""
    count: int = 0


@dataclasses.dataclass
class WithAlias(FromDictMixin):
    branch_name: Annotated[str, Alias("branchName")] = ""
    other_field: str = ""


@dataclasses.dataclass
class WithPrivate(FromDictMixin):
    _skip_field: str = "skip"
    public_field: str = "visible"


@dataclasses.dataclass
class WithEnum(FromDictMixin):
    color: Color = Color.RED


@dataclasses.dataclass
class WithDatetime(FromDictMixin):
    created_at: datetime.datetime = None


@dataclasses.dataclass
class WithList(FromDictMixin):
    items: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class WithListObjects(FromDictMixin):
    children: List[Child] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class WithDictPrimitive(FromDictMixin):
    data: Dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class WithDictObjects(FromDictMixin):
    mapping: Dict[str, Child] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class WithNested(FromDictMixin):
    child: Child = dataclasses.field(default_factory=Child)


@dataclasses.dataclass
class WithExcludeNone(FromDictMixin):
    _exclude_none: bool = True
    optional_val: Optional[str] = None
    required_val: str = "present"


# A dict subclass for testing the `if self == {}:` early-return in to_dict
class MixinDict(FromDictMixin, dict):
    pass


# An object that exposes a to_dict method (for attribute_to_dict path)
class HasToDict:
    def to_dict(self):
        return {"custom": "value"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAttributeToDict(unittest.TestCase):

    def test_regular_attribute_returned_unchanged(self):
        result = FromDictMixin.attribute_to_dict("hello")
        self.assertEqual(result, "hello")

    def test_object_with_to_dict_is_called(self):
        """Covers line 18: return getattr(attribute, 'to_dict')()."""
        obj = HasToDict()
        result = FromDictMixin.attribute_to_dict(obj)
        self.assertEqual(result, {"custom": "value"})


class TestResolveKey(unittest.TestCase):

    def test_plain_field_snake_to_camel(self):
        hints = {}
        result = FromDictMixin._resolve_key("branch_name", hints)
        self.assertEqual(result, "branchName")

    def test_alias_metadata_used(self):
        """Covers lines 25-27: Alias found in __metadata__ → return alias name."""
        from typing import get_type_hints
        hints = get_type_hints(WithAlias, include_extras=True)
        result = FromDictMixin._resolve_key("branch_name", hints)
        self.assertEqual(result, "branchName")


class TestToDict(unittest.TestCase):

    def test_self_equals_empty_dict_returns_self(self):
        """Covers line 32: if self == {}: return self."""
        empty = MixinDict()
        result = empty.to_dict()
        self.assertEqual(result, {})

    def test_private_field_skipped(self):
        """Covers line 38: field_name.startswith('_') → continue."""
        obj = WithPrivate(public_field="visible")
        result = obj.to_dict()
        self.assertNotIn("_skipField", result)
        self.assertNotIn("skipField", result)
        self.assertIn("publicField", result)

    def test_exclude_none_skips_none_attributes(self):
        """Covers lines 40-41: _exclude_none=True and attribute is None → continue."""
        obj = WithExcludeNone(optional_val=None, required_val="here")
        result = obj.to_dict()
        self.assertNotIn("optionalVal", result)
        self.assertEqual(result["requiredVal"], "here")

    def test_list_field_serialized(self):
        """Covers lines 44-46: list branch of to_dict."""
        obj = WithList(items=["a", "b", "c"])
        result = obj.to_dict()
        self.assertEqual(result["items"], ["a", "b", "c"])

    def test_list_of_objects_with_to_dict(self):
        """Covers lines 44-46 with objects that have to_dict."""
        obj = WithListObjects(children=[Child(name="alice", value=1)])
        result = obj.to_dict()
        self.assertEqual(result["children"], [{"name": "alice", "value": 1}])

    def test_dict_field_serialized(self):
        """Covers lines 48-50: dict branch of to_dict."""
        obj = WithDictPrimitive(data={"key": "val"})
        result = obj.to_dict()
        self.assertEqual(result["data"], {"key": "val"})

    def test_dict_of_objects_with_to_dict(self):
        """Covers lines 48-50 with objects that have to_dict."""
        obj = WithDictObjects(mapping={"k": Child(name="bob", value=2)})
        result = obj.to_dict()
        self.assertEqual(result["mapping"], {"k": {"name": "bob", "value": 2}})

    def test_enum_field_serialized(self):
        """Covers line 52: enum.Enum → attribute.value."""
        obj = WithEnum(color=Color.BLUE)
        result = obj.to_dict()
        self.assertEqual(result["color"], "blue")

    def test_datetime_field_serialized(self):
        """Covers line 54: datetime → iso_from_datetime(attribute)."""
        dt = datetime.datetime(2025, 1, 15, 12, 0, 0)
        obj = WithDatetime(created_at=dt)
        result = obj.to_dict()
        self.assertIn("createdAt", result)
        self.assertIn("2025-01-15", result["createdAt"])

    def test_simple_scalar_fields(self):
        obj = Simple(label="hello", count=42)
        result = obj.to_dict()
        self.assertEqual(result, {"label": "hello", "count": 42})


class TestFromDict(unittest.TestCase):

    def test_built_in_str_type(self):
        """Covers line 69/70: built-in type branch (str)."""
        result = Simple.from_dict({"label": "world", "count": 10})
        self.assertEqual(result.label, "world")
        self.assertEqual(result.count, 10)

    def test_datetime_type(self):
        """Covers lines 71-72: datetime.datetime branch."""
        result = WithDatetime.from_dict({"createdAt": "2025-06-01T10:00:00"})
        self.assertIsInstance(result.created_at, datetime.datetime)
        self.assertEqual(result.created_at.year, 2025)

    def test_enum_type(self):
        """Covers lines 73-74: Enum branch."""
        result = WithStatus.from_dict({"status": "active"})
        self.assertEqual(result.status, Status.ACTIVE)

    def test_nested_from_dict(self):
        """Covers lines 75-76: from_dict-capable object."""
        result = WithNested.from_dict({"child": {"name": "charlie", "value": 3}})
        self.assertIsInstance(result.child, Child)
        self.assertEqual(result.child.name, "charlie")

    def test_list_of_primitives(self):
        """Covers lines 77-84: list of non-from_dict elements."""
        result = WithList.from_dict({"items": ["x", "y", "z"]})
        self.assertEqual(result.items, ["x", "y", "z"])

    def test_list_of_from_dict_objects(self):
        """Covers lines 81-82: list of from_dict objects."""
        result = WithListObjects.from_dict(
            {"children": [{"name": "child1", "value": 5}]}
        )
        self.assertEqual(len(result.children), 1)
        self.assertEqual(result.children[0].name, "child1")

    def test_dict_of_primitives(self):
        """Covers the dict-of-primitives else branch."""
        result = WithDictPrimitive.from_dict({"data": {"a": "b"}})
        self.assertEqual(result.data, {"a": "b"})

    def test_dict_of_from_dict_objects(self):
        """Covers the dict-of-from_dict branch."""
        result = WithDictObjects.from_dict(
            {"mapping": {"item1": {"name": "nested", "value": 7}}}
        )
        self.assertIn("item1", result.mapping)
        self.assertEqual(result.mapping["item1"].name, "nested")

    def test_unknown_type_results_in_none(self):
        """Covers the else branch → internal_value = None → not added to result."""
        result = WithAmbiguous.from_dict({"ambiguous": "some_value"})
        # The ambiguous field should default to its initializer since None is falsy
        self.assertIsNone(result.ambiguous)

    def test_key_not_in_fields_is_ignored(self):
        """Covers the case where internal_key not in available_fields → skipped."""
        result = Simple.from_dict({"label": "test", "unknownKey": "ignored"})
        self.assertEqual(result.label, "test")

    def test_value_falsy_is_skipped(self):
        """Covers the 'and value' check: value=None/empty skips the field."""
        result = Simple.from_dict({"label": None, "count": 0})
        # Both None and 0 are falsy → not transferred
        self.assertEqual(result.label, "")
        self.assertEqual(result.count, 0)


# ---------------------------------------------------------------------------
# Extra helpers for TestFromDict
# ---------------------------------------------------------------------------

class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclasses.dataclass
class WithStatus(FromDictMixin):
    status: Status = Status.INACTIVE


# A dataclass with an unknown (non-standard) type to hit the else branch
class MyCustomType:
    """Not a dataclass/enum/datetime/list/dict — hits the else → None branch."""
    pass


@dataclasses.dataclass
class WithAmbiguous(FromDictMixin):
    ambiguous: MyCustomType = None


if __name__ == "__main__":
    unittest.main()

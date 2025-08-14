import pytest

from app.__core__.domain.service.slugify import slugify


@pytest.mark.unit
class TestSlugify:
    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("foo", "foo"),
            ("foo-bar", "foo_bar"),
            (
                " foo  bar ",
                "foo__bar",
            ),
            ("foo@BAR!", "foobar"),
            ("fOo_3.10", "foo_310"),
        ],
    )
    def test_slugify(self, input_text, expected):
        assert slugify(input_text) == expected

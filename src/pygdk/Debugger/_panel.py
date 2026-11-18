from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any as _Any

from .. import GUI as _GUI
from .. import colors as _colors
from .. import profile as _profile
from ..base import Background, Border, Padding, TabProperty, TextAttributes, Vec2


@dataclass
class _TabSource:
    name: str
    get_items: Callable[[], Iterable[_Any]]
    format_item: Callable[[_Any], str]
    get_key: Callable[[_Any], object]


class _ValueLabel(_GUI.Label):
    def __init__(
        self,
        value: _Any,
        formatter: Callable[[_Any], str],
        wrap_width: int,
    ) -> None:
        self._value = value
        self._formatter = formatter
        text_attributes = TextAttributes(
            _profile.default_textAttributes.Font,
            13,
            _colors.WHITE,
        )
        super().__init__(
            0,
            0,
            formatter(value),
            text_attributes,
            padding=Padding(2),
            wrap_width=wrap_width,
            border=Border(0, _colors.WHITE),
        )

    def on_update(self) -> None:
        self.set_text(self._formatter(self._value))


class DebuggerPanel(_GUI.TabContainer):
    def __init__(self, sources: list[_TabSource]) -> None:
        self._sources = sources
        self._source_keys: list[tuple[object, ...]] = []
        tab_properties: list[TabProperty] = []

        width = max(1, min(500, _profile.width - 16))
        height = max(1, min(300, _profile.height - 16))
        self._wrap_width = max(1, width - 16)

        for source in sources:
            values = list(source.get_items())
            self._source_keys.append(
                tuple(source.get_key(value) for value in values)
            )
            items: list[_GUI.base.Element] = [
                self._make_label(source, value) for value in values
            ]
            tab_properties.append(TabProperty(source.name, items))

        super().__init__(
            0,
            0,
            width,
            height,
            Background((24, 24, 24)),
            Background((0, 90, 90)),
            Background((18, 18, 18)),
            tab_textAttributes=TextAttributes(
                _profile.default_textAttributes.Font,
                12,
                _colors.WHITE,
            ),
            tab_properties=tab_properties,
            padding=Padding(4),
            border=Border(1, (120, 120, 120)),
        )
        self.pos = Vec2(8, 8)

    def _make_label(self, source: _TabSource, value: _Any) -> _ValueLabel:
        return _ValueLabel(value, source.format_item, self._wrap_width)

    def refresh(self, tab_index: int | None = None) -> None:
        indices = (
            range(len(self._sources))
            if tab_index is None
            else (tab_index,)
        )
        for index in indices:
            source = self._sources[index]
            values = list(source.get_items())
            keys = tuple(source.get_key(value) for value in values)
            if keys == self._source_keys[index]:
                continue

            items: list[_GUI.base.Element] = [
                self._make_label(source, value) for value in values
            ]
            self.tab_properties[index].items = items
            self._source_keys[index] = keys
            if index == self.current_tabIndex:
                self.VC_TabItems.set_items(items)

    def update(self) -> None:
        if not self.should_update():
            return
        self.refresh(self.current_tabIndex)
        super().update()

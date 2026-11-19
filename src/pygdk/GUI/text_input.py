"""Experimental."""
from typing import (
    Optional as _Optional
)

from ..base import *
from .. import profile as _profile
from .label import Label as _Label
from .. import colors as _colors
from .base import GAnimator

class TextInput(_Label):
    def __init__(
            self, 
            u: float, 
            v: float, 
            text: str, 
            textAttributes=_profile.default_textAttributes, 
            padding=_profile.default_padding, 
            wrap_width: int = 0, 
            border: Border = Border(0, _colors.WHITE), 
            animator: GAnimator | None = None, 
            feedback_option: FeedbackOption | None = None, 
            anchor: Anchor = Anchor.CENTER) -> None:
        super().__init__(u, v, text, textAttributes, padding, wrap_width, border, animator, feedback_option, anchor)
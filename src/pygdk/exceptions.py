from typing import (
    Any as _Any
)

class AttachPermissionError(Exception):
    def __init__(self, component: _Any, attach_to: _Any):
        self.component = component
        self.attach_to = attach_to

    def __str__(self):
        return (
            f"{self.component} is not allowed to attach to {self.attach_to}."
        )
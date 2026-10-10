from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Events: for logging/replays now, triggered abilities later
# --------------------------------------------------------------------------
@dataclass
class Event:
    name: str
    data: dict = field(default_factory=dict)
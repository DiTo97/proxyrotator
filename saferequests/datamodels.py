import enum
from dataclasses import dataclass, field


class Anonymity(str, enum.Enum):
    """The enum for proxy anonimity"""

    high = "elite proxy"
    medium = "anonymous"
    weak = "transparent"
    unknown = "unknown"

    @classmethod
    def from_string(cls, value: str) -> "Anonymity":
        try:
            return cls(value)
        except ValueError:
            return Anonymity.unknown


@dataclass(frozen=True, slots=True)
class Proxy:
    """A proxy addres object"""

    address: str = field(hash=True)
    port: int = field(hash=True)
    country: str = field(hash=False)
    anonymity: Anonymity = field(hash=False)
    secure: bool = field(hash=False)

    def __str__(self) -> str:
        return f"{self.address}:{self.port}"

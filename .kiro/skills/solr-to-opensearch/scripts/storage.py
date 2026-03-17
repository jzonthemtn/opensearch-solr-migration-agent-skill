from abc import ABC, abstractmethod
from typing import Any, List, Optional

class StorageInterface(ABC):
    """Interface for pluggable storage backends."""
    
    @abstractmethod
    def save(self, session_id: str, data: Any) -> None:
        """Save session data."""
        pass

    @abstractmethod
    def load(self, session_id: str) -> Optional[Any]:
        """Load session data."""
        pass

    @abstractmethod
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        pass

class FileStorage(StorageInterface):
    """File-based storage implementation."""
    
    def __init__(self, base_path: str = "sessions"):
        import os
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def _get_path(self, session_id: str) -> str:
        import os
        return os.path.join(self.base_path, f"{session_id}.json")

    def save(self, session_id: str, data: Any) -> None:
        import json
        with open(self._get_path(session_id), "w") as f:
            json.dump(data, f)

    def load(self, session_id: str) -> Optional[Any]:
        import os
        import json
        path = self._get_path(session_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None

    def list_sessions(self) -> List[str]:
        import os
        if not os.path.exists(self.base_path):
            return []
        return [f[:-5] for f in os.listdir(self.base_path) if f.endswith(".json")]

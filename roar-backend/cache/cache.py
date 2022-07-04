from typing import Dict, Iterable, Tuple, Any
from hashlib import sha1
from datetime import datetime, timezone
from sortedcontainers import SortedSet


class CacheItem:
    def __init__(self, value: Any, frequency: int = 1):
        self.frequency: int = frequency
        self.last_time: datetime = CacheItem.get_time()
        self.value: Any = value

    @classmethod
    def get_time(cls) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()

    def __str__(self) -> str:
        return f"({self.value}, {self.frequency}, {self.last_time})"

    def __repr__(self):
        return self.__str__()


class Cache():

    def __init__(self, capacity: int = 512) -> None:
        self._memory: Dict[int, CacheItem] = {}
        self.capacity: int = capacity
        self._sorted_by_date: SortedSet = SortedSet(
            key=lambda hash_obj: self._memory[hash_obj].frequency / self._memory[hash_obj].last_time)

    def __iter__(self) -> Iterable[Tuple[int, str]]:
        return [(k, v.value) for k, v in self._memory.items()]
    
    def is_in(self,key:str)-> bool:
        return self._hash(key) in self._memory

    def add(self, key: str, value: Any) -> None:
        hash_obj = self._hash(key)
        if not hash_obj in self._memory.keys():
            while len(self._memory) >= self.capacity:
                self.remove()
            self._memory[hash_obj] = CacheItem(value)
            self._sorted_by_date.add(hash_obj)

    def _hash(self, key: str) -> int:
        return int(sha1(bytes(key, encoding="utf8")).hexdigest(), 16)

    def get(self, key: str) -> Any:
        hash_obj = self._hash(key)
        if hash_obj in self._memory:
            self._memory[hash_obj].frequency += 1
            self._memory[hash_obj].last_time = CacheItem.get_time()
            self._sorted_by_date.add(hash_obj)
            return self._memory[hash_obj].value

    def remove(self) -> None:
        if len(self._memory) > 0:
            removed = self._sorted_by_date[0]
            self._sorted_by_date.__delitem__(0)
            del self._memory[removed]


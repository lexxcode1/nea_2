from typing import Any, TypedDict

QueueItem = tuple[Any, int]

class PriorityQueue:
    def __init__(self, max_size: int = 1000):
        self.max_size: int = max_size
        self.queue: list[QueueItem] = []

    def push(self, item: Any, priority: int) -> list[QueueItem] | ValueError:
        # If the queue is not full, add the item
        if not self.full:
            # Add the item and sort the queue
            self.queue.append((item, priority))

            # Sort the queue by priority
            self.queue.sort(key=lambda x: x[1])

            return self.queue

        raise ValueError('Queue is full')

    def pop(self) -> Any | ValueError:
        # If the queue is not empty, pop the item
        if not self.empty:
            return self.queue.pop()[0]

        raise ValueError('Queue is empty')

    def remove(self, item: Any) -> list[QueueItem] | ValueError:
        # If the queue is not empty, remove the item
        if not self.empty:
            # Remove the item
            self.queue.remove([x for x in self.queue if x[0] == item][0])

            return self.queue

        raise ValueError('Queue is empty')

    def peek(self) -> Any | ValueError:
        # If the queue is not empty, return the first item
        if not self.empty:
            return self.queue[0]

        raise ValueError('Queue is empty')

    @property
    def empty(self) -> bool:
        return not bool(self.queue)

    @property
    def full(self) -> bool:
        return len(self.queue) == self.max_size

    def __len__(self):
        return len(self.queue)

    def __str__(self):
        return str(self.queue)

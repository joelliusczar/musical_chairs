from typing import (
	Iterable,
	Optional,
	Iterator,
	Sequence,
	Tuple,
	cast,
	TypeVar,
	Generic,
	Union
)
from collections import deque
from .sentinel import missing, Sentinel, found
from .errors import AlternateValueError


T = TypeVar("T")
TDefault = TypeVar("TDefault")

keyValueIteratorList = list[Optional[Iterator[Tuple[int,"AbsorbentTrie[T]"]]]]
storeValueType = Union[T, Sentinel]
extendIterable = Union[Iterable[str], Iterable[Tuple[str, T]]]

class LinkedListNode(Generic[T]):
	__slots__ = (
		"nextNode",
		"value"
	)

	def __init__(
		self,
		value: T,
		nextNode: Optional["LinkedListNode[T]"]=None
	) -> None:
		self.value = value
		self.nextNode = nextNode

	def __iter__(self) -> Iterator[T]:
		current = self
		while current:
			yield current.value
			current = current.nextNode

	def __repr__(self) -> str:
		return f"{self.value} - has next? {bool(self.nextNode)}"

	def __str__(self) -> str:
		return "".join(str(t) for t in self)

	def __reversed__(self) -> Iterator[T]:
		current = None

		for n in self:
			if not current:
				current = LinkedListNode(n)
			else:
				nextNode = LinkedListNode(n)
				nextNode.nextNode = current
				current = nextNode
		if not current:
			return
		for n in current:
			yield n




# if the added string is a substring of a string already
# in the trie, nothing is added
# conversely, if a string is added for which a substring
# exists in the trie, the substring is subsumed into the
# newly added string
class AbsorbentTrie(Generic[T]):
	__slots__ = (
		"__prefix_map__",
		"__node_count__",
		"key",
		"path_store"
	)

	path_store: storeValueType[T]

	def __init__(
		self,
		paths: Optional[extendIterable[T]]=None,
		key: str=""
	) -> None:
		self.__prefix_map__: dict[int, "AbsorbentTrie[T]"] = {}
		self.__node_count__ = 0
		self.key = key
		self.path_store = missing
		if paths:
			self.extend(paths)

	def __node_at_path__(
		self,
		path: str,
		createMissingNodes: bool=False
	) -> "AbsorbentTrie[T]":
		node = self
		pathIdx = 0
		if path:
			while pathIdx < len(path):
				prefix = path[pathIdx]
				key = ord(prefix)
				subTrie = node.__prefix_map__.get(key, None)
				pathIdx += 1

				if subTrie != None:
					node = subTrie
				else:
					if createMissingNodes:
						subTrie = AbsorbentTrie[T](key=prefix)
						node.__prefix_map__[key] = subTrie
						node = subTrie
					else:
						raise KeyError()
		return node

	def __nodes_along_path(self, path: str) -> Iterator["AbsorbentTrie[T]"]:
		node = self
		pathIdx = 0
		if path:
			while node != None and pathIdx < len(path):
				prefix = path[pathIdx]
				key = ord(prefix)
				subTrie = node.__prefix_map__.get(key, None)
				pathIdx += 1
				yield node
				node = subTrie
			if node != None:
				yield node

	def __update_counts__(self):
		stack: list["AbsorbentTrie[T]"] = [self]
		iterTracker: dict[int, Iterator["AbsorbentTrie[T]"]] = {}
		self.__node_count__ = 0
		leafCount = 0
		while stack:
			node = stack[-1]
			if node.isLeaf:
				leafCount += 1
				stack.pop()
			else:
				try:
					childIter = iterTracker.get(id(node), None)
					if not childIter:
						childIter = iter(node.__prefix_map__.values())
						iterTracker[id(node)] = childIter
					child = next(childIter)
					child.__node_count__ = 0
					node.__node_count__ += leafCount
					leafCount = 0
					stack.append(child)
				except StopIteration:
					del iterTracker[id(node)]
					stack.pop()
					if not node.isLeaf:
						node.__node_count__ += leafCount
						node.__node_count__ +=	sum(c.__node_count__ for c \
							in node.__prefix_map__.values()
						)
						leafCount = 0

	def add(self, path: str, value: storeValueType[T]=missing):
		node = self.__node_at_path__(path, True)
		node.path_store = value if value != missing else found
		self.__update_counts__()

	def extend(self, paths: extendIterable[T]):
		for path in paths:
			if type(path) == str:
				node = self.__node_at_path__(path, True)
				node.path_store = found
			else:
				node = self.__node_at_path__(path[0], True)
				value = cast(T, path[1])
				node.path_store = value if value != missing else found
		self.__update_counts__()

	def __contains__(self, path: str) -> bool:
		if path:
			try:
				self.__node_at_path__(path)
			except:
				return False
		return True

	def __value_at_path__(
		self,
		path: str
	) -> storeValueType[T]:
		if path:
			node = self.__node_at_path__(path)
			if node.path_store != missing:
				return node.path_store
			else:
				raise KeyError()
		else:
			if self.path_store:
				return self.path_store
			else:
				raise KeyError()

	def matches(self, path: str) -> bool:
		node = self
		pathIdx = 0
		if path:
			while pathIdx < len(path):
				if not len(node.__prefix_map__) or node.is_path_end:
					return True
				prefix = path[pathIdx]
				key = ord(prefix)
				subTrie = node.__prefix_map__.get(key, None)
				if subTrie is None:
					return False
				pathIdx += 1
				node = subTrie
		return True


	def has_prefix_for(self, path: str) -> bool:
		# nodes = [*self.__nodes_along_path(path)]
		return any(True for n in self.__nodes_along_path(path) \
			if n.path_store != missing
		)

	def __getitem__(self, key: str) -> T:
		value = self.__value_at_path__(key)
		if value == found:
			raise AlternateValueError()
		return cast(T, value)

	def __setitem__(self, key: str, value: T):
		self.add(key, value)

	def get(self, key: str, default: TDefault) -> Union[T, TDefault]:
		try:
			value = self[key]
			return value
		except (KeyError, AlternateValueError):
			return default

	def __len__(self) -> int:
		return self.__node_count__

	@property
	def isLeaf(self) -> bool:
		return len(self.__prefix_map__) == 0

	@property
	def child_keys(self) -> list[str]:
		return [chr(k) for k in self.__prefix_map__.keys()]

	@property
	def is_path_end(self) -> bool:
		return self.path_store != missing

	def all_paths(self) -> Iterator[str]:
		return self.__traverse_path_optimized__("")

	def __line_order_values__(self) -> Iterator[Tuple[str, Optional[T]]]:
		queue = deque[Tuple["AbsorbentTrie[T]", LinkedListNode[str]]]()
		queue.append((self, LinkedListNode(self.key)))
		while queue:
			node, llnode = queue.popleft()
			for child in node.__prefix_map__.values():
				llnode2 = LinkedListNode(child.key, llnode)
				queue.append((child, llnode2))
			if node.path_store != missing:
				path = "".join(c for c in reversed(llnode))

				if type(node.path_store) == Sentinel:
					yield (path, None)
				else:
					yield (path, cast(T, node.path_store))

	def values(self, path: Optional[str]=None) -> Iterator[Optional[T]]:
		if path:
			yield from (
				(n.path_store if not isinstance(n.path_store, Sentinel) else None) \
				for n in self.__nodes_along_path(path) \
				if n.path_store != missing
			)
			return
		yield from (pair[1] for pair in self.__line_order_values__())

	def values_map(self) -> dict[str, Optional[T]]:
		return {pair[0]:pair[1] for pair in self.__line_order_values__()}

	def __repr__(self) -> str:
		printValue = self.key or "<root>"
		return f"{printValue} - {self.path_store}"

	@property
	def depth(self) -> int:
		depth = 0
		stack: list["AbsorbentTrie[T]"] = [self]
		iterTracker: dict[int, Iterator["AbsorbentTrie[T]"]] = {}
		while stack:
			node = stack.pop()
			if node.isLeaf:
				depth = max(depth, len(stack))
			else:
				try:
					childIter = iterTracker.get(id(node), None)
					if not childIter:
						childIter = iter(node.__prefix_map__.values())
						iterTracker[id(node)] = childIter
					child = next(childIter)
					stack.append(node)
					stack.append(child)
				except StopIteration:
					del iterTracker[id(node)]
		return depth

	def __traverse_path_optimized__(
		self,
		path: str
	) -> Iterator[str]:

		pathEnd = self.__node_at_path__(path)

		if pathEnd:
			depth = pathEnd.depth
			resultSpace = [[""] * (depth) for _ in range(pathEnd.__node_count__)]
			pathEnd.__traverse_optimized_helper__(depth, resultSpace)

			for row in resultSpace:
				yield path + "".join(row)

	def __traverse_optimized_helper__(
		self,
		depth: int,
		resultSpace: Sequence[list[str]],
		useShortestPath: bool=False
	):
		#height stack and char stack should match length of suffix
		#heightsStack tracks offsets so that all of the strings are aligned
		heightsStack = [0] * depth
		#basically tracks the current word
		#we build the string from back to front so we need to track the front of
		# of the string using this stack
		charStack = [""] * depth

		#this is the core stack to track where we are in the algorithm
		# we need the root to figure out where to go next, we need that +1
		# to use a bigger stack
		stack = cast(list[AbsorbentTrie[T]],[None] * (depth + 1))
		iterStack: keyValueIteratorList[T] = [None] * (depth + 1)

		stackPtr = 0
		stack[stackPtr] = self
		colIdx = 0
		while stackPtr >= 0:
			node = stack[stackPtr]
			try:
				if useShortestPath and node.path_store != missing:
					raise StopIteration()
				childIter = iterStack[stackPtr]
				if not childIter:
					childIter = iter(node.__prefix_map__.items())

				#it will throw StopIteration here after we've vistited all the children
				key, child = next(childIter)

				iterStack[stackPtr] = childIter

				#if stack pointer is 0, then that means that we're working with the root
				# and we're not storing root in results table
				if stackPtr > 0:
					colIdx += 1
				charStack[stackPtr] = chr(key)
				stackPtr += 1
				stack[stackPtr] = child
			except StopIteration:
				#this is for when a node has no children (didn't store iterator
				# before raising) and the current path is not the longest
				# in the subtree. We add offsets for all the empty spaces
				# so that the chars get added to correct row
				if not iterStack[stackPtr]:
					for i in range(colIdx + 1, len(heightsStack)):
						heightsStack[i] += 1
				iterStack[stackPtr] = None
				stackPtr -= 1
				if stackPtr >= 0:
					if charStack[stackPtr]:
						fromIdx = heightsStack[stackPtr]
						allocation = node.__node_count__ if not useShortestPath \
							else sum(1 for _ in node.closest_value_nodes())
						for i in range(fromIdx, fromIdx + (allocation or 1)):
							resultSpace[i][colIdx] = charStack[stackPtr]
						heightsStack[colIdx] += (allocation or 1)
					if stackPtr > 0:
						colIdx -= 1
					charStack[stackPtr] = ""

	def paths_start_with(self, path: str) -> Iterable[str]:
		try:
			yield from self.__traverse_path_optimized__(path)
		except KeyError:
			return

	def closest_value_nodes(self) -> Iterator["AbsorbentTrie[T]"]:
		stack: list["AbsorbentTrie[T]"] = [self]
		iterTracker: dict[int, Iterator["AbsorbentTrie[T]"]] = {}
		while stack:
			node = stack[-1]
			if node.isLeaf or node.path_store != missing:
				yield node
				stack.pop()
			else:
				try:
					childIter = iterTracker.get(id(node), None)
					if not childIter:
						childIter = iter(node.__prefix_map__.values())
						iterTracker[id(node)] = childIter
					child = next(childIter)
					stack.append(child)
				except StopIteration:
					del iterTracker[id(node)]
					stack.pop()

	def shortest_paths(self) -> Iterator[str]:
		depth = self.depth
		if not depth:
			if self.path_store != missing:
				yield ""
			return
		resultSpace = [[""] * (depth)
			for _ in range(sum(1 for _ in self.closest_value_nodes()))]
		self.__traverse_optimized_helper__(depth, resultSpace, True)

		for row in resultSpace:
				yield "".join(row)


chainedStoreValueType = Union[Iterable[T], storeValueType[T]]

class ChainedAbsorbentTrie(Generic[T]):

		def __init__(
		self,
		paths: Optional[extendIterable[T]]=None,
		key: str=""
		) -> None:
			self.__absorbentTrie__ = AbsorbentTrie[list[T]](None,key)
			if paths:
				self.extend(paths)

		def add(
				self,
				path: str,
				value: chainedStoreValueType[T]=missing,
				shouldEmptyUpdateTree: bool=True
			):
			added = self.__absorbentTrie__.__node_at_path__(path, True)
			if isinstance(added.path_store, Sentinel):
				if isinstance(value, Iterable):
					collection = cast(list[T],[*value])
					if not shouldEmptyUpdateTree:
						if len(collection) == 0:
							return
					added.path_store = collection
				else:
					added.path_store = [value] if not isinstance(value, Sentinel) else []
			else:
				if not isinstance(value, Sentinel):
					if isinstance(value, Iterable):
						added.path_store.extend(cast(Iterable[T], value))
					else:
						added.path_store.append(value)
			self.__absorbentTrie__.__update_counts__()

		def extend(self, paths: extendIterable[T]):
			for path in paths:
				if type(path) == str:
					added = self.__absorbentTrie__.__node_at_path__(path, True)
					if added.path_store == missing:
						added.path_store = []
				else:
					added = self.__absorbentTrie__.__node_at_path__(path[0], True)
					value = cast(T, path[1])
					if isinstance(added.path_store ,Sentinel):
						added.path_store = [value] if not isinstance(value, Sentinel) \
							else []
					elif not isinstance(value, Sentinel):
						added.path_store.append(value)
			self.__absorbentTrie__.__update_counts__()

		def __contains__(self, path: str) -> bool:
			return path in self.__absorbentTrie__

		def has_prefix_for(self, path: str) -> bool:
			return self.__absorbentTrie__.has_prefix_for(path)

		def __getitem__(self, key: str) -> list[T]:
			return self.__absorbentTrie__[key]

		def get(self, key: str, default: TDefault) -> Union[list[T], TDefault]:
			return self.__absorbentTrie__.get(key, default)

		def all_paths(self) -> Iterator[str]:
			return self.__absorbentTrie__.all_paths()

		@property
		def depth(self) -> int:
			return self.__absorbentTrie__.depth

		def paths_start_with(self, path: str) -> Iterable[str]:
			try:
				return self.__absorbentTrie__.paths_start_with(path)
			except KeyError:
				return ()

		def values(self, path: Optional[str]=None) -> Iterator[Iterable[T]]:
			return (v for v in self.__absorbentTrie__.values(path) if v)

		def values_map(self)-> dict[str, Optional[list[T]]]:
			return self.__absorbentTrie__.values_map()

		def valuesFlat(self, path: Optional[str]=None) -> Iterator[T]:
			return (r for i in self.values(path) for r in i)

		def shortest_paths(self) -> Iterator[str]:
			return self.__absorbentTrie__.shortest_paths()

		def matches(self, path: str) -> bool:
			return self.__absorbentTrie__.matches(path)
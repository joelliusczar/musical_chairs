from typing import Iterable, Optional, Iterator, Sequence, Tuple, cast

keyValueIteratorList = list[Optional[Iterator[Tuple[int,"AbsorbentTrie"]]]]

# if the added string is a substring of a string already
# in the trie, nothing is added
# conversely, if a string is added for which a substring
# exists in the trie, the substring is subsumed into the
# newly added string
class AbsorbentTrie:
	__slots__ = ("_prefix_map", "__count__", "key")

	def __init__(
		self,
		paths: Optional[Iterable[str]]=None,
		key: str=""
	) -> None:
		self._prefix_map: dict[int, "AbsorbentTrie"] = {}
		self.__count__ = 0
		self.key = key
		if paths:
			self.extend(paths)

	def __add__(self, path: str) -> int:
		node = self
		added = 0
		if path:
			while path:
				prefix = path[0]
				key = ord(prefix)
				subTrie = node._prefix_map.get(key, None)
				path = path[1:]

				if subTrie != None:
					node = subTrie
				else:
					subTrie = AbsorbentTrie(key=prefix)
					node._prefix_map[key] = subTrie
					node = subTrie
					added = 1
		return added

	def __update_counts__(self):
		stack: list["AbsorbentTrie"] = [self]
		iterTracker: dict[int, Iterator["AbsorbentTrie"]] = {}
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
						childIter = iter(node)
						iterTracker[id(node)] = childIter
					child = next(childIter)
					stack.append(child)
				except StopIteration:
					del iterTracker[id(node)]
					stack.pop()
					if not node.isLeaf:
						node.__count__ = leafCount
						node.__count__ +=	sum(len(c) for c in node)
						leafCount = 0

	def add(self, path: str) -> int:
		added = self.__add__(path)
		self.__update_counts__()
		return added

	def extend(self, paths: Iterable[str]):
		for path in paths:
			self.__add__(path)
		self.__update_counts__()

	def __contains__(self, path: str) -> bool:
		if path:
			return self.__get_path_end__(path) != None
		return True

	@property
	def isLeaf(self) -> bool:
		return len(self._prefix_map) == 0

	@property
	def keys(self) -> list[str]:
		return [chr(k) for k in self._prefix_map.keys()]

	def values(self) -> Iterator[str]:
		return self.__traverse_path_optimized__("")


	def __len__(self) -> int:
		#went with a backing variable so that getting the length would be O(1)
		#rather than O(N)
		return self.__count__

	@property
	def len(self) -> int:
		return len(self)

	def __iter__(self) -> Iterator["AbsorbentTrie"]:
		return iter(self._prefix_map.values())


	def __bool__(self) -> bool:
		return not self.isLeaf

	def __repr__(self) -> str:
		return self.key or "<root>"

	def __get_path_end__(
		self,
		path: str,
	) -> Optional["AbsorbentTrie"]:
		if path:
			node = self
			while node != None and path:
				prefix = path[0]
				key = ord(prefix)
				node = node._prefix_map.get(key, None)
				if node != None:
					path = path[1:]
			return node
		else:
			return self

	@property
	def depth(self) -> int:
		depth = 0
		stack: list["AbsorbentTrie"] = [self]
		iterTracker: dict[int, Iterator["AbsorbentTrie"]] = {}
		while stack:
			node = stack.pop()
			if node.isLeaf:
				depth = max(depth, len(stack))
			else:
				try:
					childIter = iterTracker.get(id(node), None)
					if not childIter:
						childIter = iter(node)
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

		pathEnd = self.__get_path_end__(path)

		if pathEnd:
			depth = pathEnd.depth
			resultSpace = [[""] * (depth) for _ in range(len(pathEnd))]
			self.__traverse_optimized_helper__(pathEnd, depth, resultSpace)

			for row in resultSpace:
				yield path + "".join(row)


	def __traverse_optimized_helper__(
		self,
		pathEnd: "AbsorbentTrie",
		depth: int,
		resultSpace: Sequence[list[str]]
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
		stack = cast(list[AbsorbentTrie],[None] * (depth + 1))

		iterStack: keyValueIteratorList = [None] * (depth + 1)
		stackPtr = 0
		stack[stackPtr] = pathEnd
		colIdx = 0
		while stackPtr >= 0:
			node = stack[stackPtr]
			try:
				childIter = iterStack[stackPtr]
				if not childIter:
					childIter = iter(node._prefix_map.items())

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
						for i in range(fromIdx, fromIdx + (len(node) or 1)):
							resultSpace[i][colIdx] = charStack[stackPtr]
						heightsStack[colIdx] += (len(node) or 1)
					if stackPtr > 0:
						colIdx -= 1
					charStack[stackPtr] = ""


	def __inorder_traverse_path_iterator__(
		self,
		path: Optional[str]=None
	) -> Iterator[str]:
		if self.isLeaf:
			yield ""
		else:
			if path:
				prefix = path[0]
				key = ord(prefix)
				subTrie = self._prefix_map.get(key, None)
				if subTrie != None:
					for suffix in subTrie.__inorder_traverse_path_iterator__(path[1:]):
						yield prefix + suffix
				return
			else:
				for k, v in self._prefix_map.items():
					for suffix in v.__inorder_traverse_path_iterator__(""):
						yield chr(k) + suffix


	def paths_start_with(self, path: str) -> Iterable[str]:
		return self.__traverse_path_optimized__(path)

from queue import PriorityQueue
from copy import deepcopy

# It will help when using path in another module (API)
# All the dta should come from client side or the user
class Graph:
  def __init__(self, graph: dict, hTable: dict, allEdges: dict, nodes=[]) -> None:
    self.graph = deepcopy(graph) # O(V+E) deep copy no reference etc...
    self.allEdges = deepcopy(allEdges)
    self.hTable = deepcopy(hTable)
    if len(nodes) != 0:
      self.nodes = nodes
    else:
      self.nodes = list(self.graph.keys())
  
  # A*
  def findShortestPath(self, start, target):
    solutions = PriorityQueue()
    solutions.put(Path([start], self))
    visited = dict()
    
    while not solutions.empty():
      solution = solutions.get()
      if solution.path[-1] in visited: continue
      
      if solution.path[-1] == target:
        return solution
      
      visited[solution.path[-1]] = 1
      for node in self.graph[solution.path[-1]]:
        new_path = Path(solution.path.copy(), self) + node[0]
        solutions.put(new_path)
    
    return None
  
  # Represent the graph in a good way
  def __str__(self):
    result = ""
    for node in self.graph:
      result += f"The edges for node {node}: \n"
      for i in range(len(self.graph[node])):
        title, weight = self.graph[node][i]
        nextArrow = f" --{weight}--> "
        result += f"{node}{nextArrow}{title}\n"
      result += "\n"
    return result


# Path data structure very helpfull in A* and TSP
class Path:
  # path -> ["A", "B", "C"]
  def __init__(self, path: list, graph: Graph) -> None:
    self.graph = graph # This O(1) because python pass objects and collections by reference
    self.path = path
    self.gCost = 0
    self.hCost = 0
    self.fCost = 0
    if len(path) != 0:
      self._calcFHG()
  
  # Helper to find h-cost
  def _calcH(self, node = ""):
    if node != "":
      self.hCost = self.graph.hTable[node] if node in self.graph.hTable else float("inf")
    else:
      self.hCost = self.graph.hTable[self.path[-1]] if self.path[-1] in self.graph.hTable else float("inf")
  
  # Helper function to calc g-cost
  def _calcG(self):
    # Path ["A", "B"]
    self.gCost = 0
    for i in range(1, len(self.path)):
      # Check the edge
      curEdge = f"{self.path[i]},{self.path[i-1]}"
      if curEdge in self.graph.allEdges:
        self.gCost += self.graph.allEdges[curEdge]
      else:
        self.gCost += float("inf")
  
  def _calcFHG(self):
    self._calcG()
    self._calcH()
    self.fCost = self.gCost + self.hCost
  
  # Override plus operation to add node to the path
  # Never add somthing except node -> "name"
  def __add__(self, node):
    if len(self.path) == 0:
      edge = 0
    elif f"{self.path[-1]},{node}" in self.graph.allEdges:
      edge = self.graph.allEdges[f"{self.path[-1]},{node}"] # If edge exist fine
    else:
      edge = float("inf") # If not mark this solution as Infinity because we minimize f-cost in A*
    self.gCost += edge
    self.path.append(node)
    self._calcH(node)
    self.fCost = self.gCost + self.hCost
    return self
  
  # It will compare between two paths with f-cost 
  # (In TSP it wouldn't work because it compare with g-cost)
  def __lt__(self, other):
    if self.fCost < other.fCost: return True
    return False
  
  def __gt__(self, other):
    if self.fCost > other.fCost: return True
    return False
  
  # Represent the path in a good way
  def __str__(self):
    path = ""
    for i in range(1, len(self.path)):
      edge = f"{self.path[i-1]},{self.path[i]}"
      weight = self.graph.allEdges[edge] if edge in self.graph.allEdges else float("inf")
      nextArrow = f" --{weight}--> "
      path += f"{self.path[i-1]}"
      path+=nextArrow
      if i == len(self.path)-1: path += self.path[-1]
    return path


if __name__ == "__main__":
  adjList = {
    "A": [["B", 3], ["G", 1]],
    "B": [["C", 2], ["A", 3]],
    "C": [["B", 2], ["G", 5], ["K", 3]],
    "G": [["A", 1], ["C", 5], ["K", 4]],
    "K": [["G", 4], ["C", 3]],
  }

  # H-COST -> This will be calculated in the client side and send it here
  hTable = {
    "A": 5,
    "B": 5,
    "C": 3,
    "G": 4,
    "K": 0
  }

  # All edges also in the client side
  allEdges = {
    "A,B": 3,
    "B,A": 3,
    "A,G": 1,
    "G,A": 1,
    "B,C": 2,
    "C,B": 2,
    "C,G": 5,
    "G,C": 5,
    "C,K": 3,
    "K,C": 3,
    "G,K": 4,
    "K,G": 4,
  }
  graph = Graph(adjList, hTable, allEdges)
  path = Path(["A", "L"], graph)
  print(graph.findShortestPath("A","K"))


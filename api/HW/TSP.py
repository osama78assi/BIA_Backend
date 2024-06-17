from .AStar import Graph, Path
import random

# We will use path because g-cost is what is matter (DRY)

class GeneticTSP:
  def __init__(self, populationsCount: int, generationsCount: int, start: str, graph: Graph, crossoverProp=0.7, mutationProp=0.01) -> None:
    self.populationsCount = populationsCount
    self.generationsCount = generationsCount
    self.start = start
    self.graph = graph # THIS IS OBJECT
    self.CROSSOVER_PROP = crossoverProp
    self.MUTATION_PROP = mutationProp
    self.populations = []
    self.fitnessArr = []
    self.bestFitness = float("inf")
    self.bestFitnessIndex = -1
    self.totalFitness = 0
    self.higherPenalty = -float("inf")
    self._initPopulations()
    self._calcFitness()
  
  # Helper function to know the best fitness
  def _findBestFitness(self, penalty, index):
    if -penalty > -self.bestFitness:
      self.bestFitness = penalty
      self.bestFitnessIndex = index
  
  # Helper function to take the higher penalty
  def _findHigherPenalty(self, penalty):
    if penalty > self.higherPenalty:
      self.higherPenalty = penalty
  
  def _initPopulations(self):
    # Permutations
    for i in range(self.populationsCount):
      path = Path([self.start], self.graph) # We need to find it according to first node
      visited = {
        self.start: 1,
      }
      
      while len(visited) != len(self.graph.nodes):
        randNode = self.graph.nodes[random.randint(0, len(self.graph.nodes)-1)]
        if randNode not in visited:
          path += randNode
          visited[randNode] = 1
      path += self.start
      self.populations.append(path)
      # Find best fitness and higher penalty
      self._findBestFitness(path.gCost, i)
      self._findHigherPenalty(path.gCost)
  
  def _calcFitness(self):
    fitnessArr = []
    totalFitness = 0
    for path in self.populations:
      # The worst solution has a chance to be best solution but give it a low chance like 1
      fitness = (self.higherPenalty - path.gCost) + (1 if self.higherPenalty == path.gCost else 0)
      fitnessArr.append(fitness)
      totalFitness += fitness
    self.fitnessArr = fitnessArr
    self.totalFitness = totalFitness
  
  # Helper to fix the paths
  def _fixPath(self, path: Path):
    missing = [] # Declare missing arr to save indices of missing nodes
    found = {node for node in self.graph.nodes} # Suppose all nodes found
    # Don't go to the end because the end should be repeated in the start
    for i in range(len(path.path)-1):
      node = path.path[i]
      if node in found:
        found.remove(node) # Delete the node if exist in the found (in average O(1))
      else:
        missing.append(i) # Save the repeat index
    if len(missing) == 0:
      return # There is nothing missing
    # Convert set to list
    found = list(found)
    taken = dict()
    while len(taken) != len(missing): # Break if we got all missing elements
      randIndex = random.randint(0, len(missing)-1) # random point
      if randIndex not in taken: # If the point already taken ignore it
        indexInPath = missing[randIndex] # Take the index in the path
        path.path[indexInPath] = found[randIndex] # Set the node
        taken[randIndex] = 1 # Mark the index as taken
  
  def _crossoverMuation(self):
    for i in range(0, self.populationsCount, 2):
      thereIsCrossover = random.random() <= self.CROSSOVER_PROP
      thereIsMutation = random.random() <= self.MUTATION_PROP
      path1 = self.populations[i]
      path2 = self.populations[i+1]
      
      if thereIsCrossover:
        crossoverPoint = random.randint(1, len(path1.path)-1)
        # Do the crossover but save start and end
        path1.path, path2.path = path1.path[0:1] + path2.path[1:crossoverPoint] + path1.path[crossoverPoint:], \
          path2.path[0:1] + path1.path[1:crossoverPoint] + path2.path[crossoverPoint:]
        self._fixPath(path1)
        self._fixPath(path2)
      
      if thereIsMutation: # We made sure the path is correct
        # DON'T take the start or end
        # The mutation will be in the same path by replace the place of two random nodes
        mutationPoints1 = [random.randint(1, len(path1.path)-2), random.randint(1, len(path1.path)-2)]
        mutationPoints2 = [random.randint(1, len(path2.path)-2), random.randint(1, len(path2.path)-2)]
        # A -> B -> C => A -> C -> B
        path1.path[mutationPoints1[0]], path1.path[mutationPoints1[1]] = path1.path[mutationPoints1[1]], path1.path[mutationPoints1[0]]
        path2.path[mutationPoints2[0]], path2.path[mutationPoints2[1]] = path2.path[mutationPoints2[1]], path2.path[mutationPoints2[0]]
      
      # Recalculate the g-cost
      if thereIsCrossover or thereIsMutation:
        path1._calcG()
        path2._calcG()
      
      # Find higher penalty and best fitness
      self._findBestFitness(path1.gCost, i)
      self._findBestFitness(path2.gCost, i)
      self._findHigherPenalty(path1.gCost)
      self._findHigherPenalty(path2.gCost)
  
  def _selection(self):
    probs = []
    for fitness in self.fitnessArr:
      probs.append(fitness / self.totalFitness)
    self.populations = random.choices(self.populations, probs, k=self.populationsCount)
  
  def solve(self):
    for _ in range(self.generationsCount):
      self._selection()
      self._crossoverMuation()
      self._calcFitness()
    return self.populations[self.bestFitnessIndex]


if __name__ == "__main__":
  # This data should come from the client side
  # There is no need to this data but for represntation
  adjList = {
    "A": [["B", 2], ["C", 9], ["D", 10], ["E", 7]],
    "B": [["A", 2], ["C", 6], ["D", 4], ["E", 3]],
    "C": [["A", 9], ["B", 6], ["D", 8], ["E", 5]],
    "D": [["A", 10], ["B", 4], ["C", 8], ["E", 6]],
    "E": [["A", 7], ["B", 3], ["C", 5], ["D", 6]]
  }
  
  # E --7--> A --2--> B --4--> D --8--> C --5--> E
  
  # All this data should come from the client side
  allEdges = {
    "A,B": 2,
    "B,A": 2,
    "A,C": 9,
    "C,A": 9,
    "A,D": 10,
    "D,A": 10,
    "A,E": 7,
    "E,A": 7,
    "B,C": 6,
    "C,B": 6,
    "B,D": 4,
    "D,B": 4,
    "B,E": 3,
    "E,B": 3,
    "C,D": 8,
    "D,C": 8,
    "C,E": 5,
    "E,C": 5,
    "D,E": 6,
    "E,D": 6
  }
  nodes = ["A", "B", "C", "D", "E"]
  graph = Graph(adjList, dict(), allEdges, nodes)
  tsp = GeneticTSP(100, 100, "A", graph)
  # for path in tsp.populations:
  #   print(path)
  #   print(f"F-cost is {path.fCost}")
  #   print(f"G-cost is {path.gCost}")
  #   print("############")
  # path1 = Path(["A", "B", "E", "D", "C", "A"], graph)
  solution = tsp.solve()
  print(solution)
  print(solution.gCost)

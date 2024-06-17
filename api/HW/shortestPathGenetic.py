import random
from .AStar import Path, Graph

# SIDE NOTES:
# init_populations:
#   1. Take random node from the direct connected to last node in the path
#   2. How many nodes should I take ? random simply but what is the range for this random ?
#   in A* term the last node in the path shouldn't be visited again. Why ?
#   because we already add all possibilities for that node to go from it
#   What did we get ? the closed list in A* keep track of all nodes already been fully explored
#   that tells us the maximum nodes in the path souldn't exceed number of nodes
# fitness:
#   1. the less f-cost is the most perefect solution
#   2. we don't know the best solution if we didn't solved the problem 
#   that's mean we don't have fitness tells us this is the perfect solution ever
#   3. fitness called by finding the worst solution penalty and add subtract the
#   fitness from it for one solution this way will keep balace of weight when selection comes into play
# crossover:
#   1. crossover is done between start and end not between all the path -> end not included
#   let's say I have these solutions ["A", "B", "C"] and ["A", "G", "H", "J", "C"] the crossover point
#   was 3 (3 not included) the two solutions would be like this ["A", "G", "H", "C"] and ["A", "B", "J", "C"]

class GeneitcShortestPath:
  # Each solution (chromosome) is Path
  def __init__(self, graph: Graph, populationsCount: int, generationsCount: int, start: str, target: str, crossoverProp=0.7, mutationProp = 0.01) -> None:
    self.graph = graph # THIS IS OBJECCT BE CAREFULL
    self.start = start
    self.target = target
    self.populationsCount = populationsCount
    self.generationsCount = generationsCount
    self.CROSSOVER_PROP = crossoverProp
    self.MUTATION_PROP = mutationProp
    self.populations = []
    self.fitnessArr = [] # keep track of fitness for all solutions
    self.totalFitness = 0 # Keep track of sum of the fitness
    self.bestFitness = float("inf")
    self.higherPenalty = -float("inf") # It will be helpful in taking the probabilites of solutions
    self.bestFitnessIndex = -1
    self._initPopulations()
    self._calcFitness() # Calc the fitness over all initially
  
  # Init populations
  def _initPopulations(self):
    for i in range(self.populationsCount):
      self.populations.append(Path([self.start], self.graph)) # Each path should start from the givin start
      
      nodesToTake = self.graph.graph[self.start] # We take random node from the connected node to the start
      numOfNodes = random.randint(1, len(self.graph.graph) - 2) # because in the path there is start and end
      takenNodes = {
        self.start: 1, # We took the start
      }
      
      for _ in range(numOfNodes):
        randNodeIndex = random.randint(0, len(nodesToTake)-1) # Random node index
        randNode = nodesToTake[randNodeIndex][0] # Random node
        
        if randNode in takenNodes: continue # Skip if node in the path
        
        self.populations[i] += randNode[0] # Add the random node
        takenNodes[randNode] = 1 # Mark the taken node
        nodesToTake = self.graph.graph[randNode] # Take next node that is connected to the taken one
      
      if self.populations[i].path[-1] != self.target: # Add the target if not exist
        self.populations[i] += self.target
      
      self._choseBestFitness(self.populations[i].fCost, i) # F-cost is the penalty and penalty is the negative of fitness
      self._choseHigherPenalty(self.populations[i].fCost) # Chose the worst solution
  
  # Helper function to chose best fitness
  def _choseBestFitness(self, penalty, index):
    if penalty == float("inf"): # If the solution is inf that's mean there is not path
      return
    if -penalty > -self.bestFitness: # penalty oppsite of fitness but the algoritm is MAXIMIZE
      self.bestFitness = penalty
      self.bestFitnessIndex = index
  
  # Helepr to chose the worst fitness (higher one)
  def _choseHigherPenalty(self, penalty):
    if penalty == float("inf"): # If the solution is inf that's mean there is not path
      return
    if penalty > self.higherPenalty:
      self.higherPenalty = penalty + 1 # It's bad solution right ? but maybe crossover operation will make it best one so give it a chance
  
  # Helper for mutation
  def _mutatePath(self, path):
    # If we got a path with two nodes the mutaion would be insert node in the path
    if len(path) == 2:
      connectedNodes = self.graph.graph[path[-1]]
      # The path is A -> B, and A connected to ["G", "F" , "B"] the result of muation would be like -> A -> F -> B or A -> B -> B ...etc
      path = path[0:1] + connectedNodes[random.randint(0, len(connectedNodes)-1)] + path[1:]
    else:
      # Same operations but here we take random node and replace it with another node
      # ["A", "B", "G", "C"]; randNode is B and the nodes connected to B is ["G", "H"]; we took G for example
      # path would be after mutaion like: ["A", "B", "H", "G", "C"] or ["A", "B", "G", "G", "C"] all is random
      randIndex = random.randint(1, len(path)-2) # Save the random index
      randNode = path[randIndex] # Take the node from the path
      connectedNodes = self.graph.graph[randNode] # Take the connected nodes to that random node
      path = path[0:randIndex] + connectedNodes[random.randint(0, len(connectedNodes)-1)] + path[randIndex:] # Insert it

  
  # Crossover and mutation
  def _crossoverMutation(self):
    for i in range(0, self.populationsCount, 2):
      thereIsCrossover = random.random() < self.CROSSOVER_PROP
      thereIsMutation = random.random() < self.MUTATION_PROP
      # The crossover shold keep target at end
      lessPathNodes = self.populations[i].path if len(self.populations[i].path) < len(self.populations[i+1].path) else self.populations[i+1].path
      morePathNodes = self.populations[i].path if len(self.populations[i].path) > len(self.populations[i+1].path) else self.populations[i+1].path
      
      if thereIsCrossover:
        endPoint = len(self.populations[random.randint(i, i+1)].path) - 1 # Chose randomly the crossover point between the two poulations
        corssoverPoint = random.randint(0, endPoint)
        if corssoverPoint >= len(lessPathNodes):
          # ["A", "B", "C"] & ["A", "V", "J", "K", "C"]; endPoint = 3 then the crossover -> ["A", "V", "J", "C"], ["A", "B", "K", "C"]
          lessEndPoint = len(lessPathNodes)-1
          morePathNodes, lessPathNodes = lessPathNodes[:lessEndPoint] + morePathNodes[endPoint:], \
            morePathNodes[:endPoint] + lessPathNodes[lessEndPoint:]
        else:
          lessPathNodes, morePathNodes = lessPathNodes[:endPoint] + morePathNodes[endPoint:] , \
            morePathNodes[:endPoint] + lessPathNodes[endPoint:]
      
      if thereIsMutation:
        self._mutatePath(lessPathNodes)
        self._mutatePath(morePathNodes)
      
      # Optimization
      # Re-calculate the fitness for each path after any operations has happened
      if thereIsCrossover or thereIsMutation:
        self.populations[i]._calcFHG()
        self.populations[i+1]._calcFHG()
      
      # Keep track of best fitness
      self._choseBestFitness(self.populations[i].fCost, i)
      self._choseBestFitness(self.populations[i+1].fCost, i+1)
      # Keep track of higher fitness
      self._choseHigherPenalty(self.populations[i].fCost)
      self._choseHigherPenalty(self.populations[i+1].fCost)
  
  def _calcFitness(self):
    fitnessArr = []
    total = 0
    for pop in self.populations:
      fitness = (self.higherPenalty - pop.fCost ) if pop.fCost != float("inf") else 0
      fitnessArr.append(fitness)
      total += fitness
    self.fitnessArr = fitnessArr
    self.totalFitness = total
  
  def _selection(self):
    probs = []
    for fitness in self.fitnessArr:
      probs.append(fitness / self.totalFitness)
    
    self.populations = random.choices(self.populations, probs, k=self.populationsCount)
  
  def solve(self):
    for _ in range(self.generationsCount):
      self._selection()
      self._crossoverMutation()
      self._calcFitness()
    return self.populations[self.bestFitnessIndex]


if __name__ == "__main__":
  # Again all this data coming from client side
  adjList = {
    "A": [["B", 3], ["G", 1]],
    "B": [["C", 2], ["A", 3]],
    "C": [["B", 2], ["G", 5], ["K", 3]],
    "G": [["A", 1], ["C", 5], ["K", 4]],
    "K": [["G", 4], ["C", 3]]
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
    "K,G": 4
  }
  
  graph = Graph(adjList, hTable, allEdges)
  populations = GeneitcShortestPath(graph, 10, 100, "A", "K")
  for path in populations.populations:
    print(path, end="\n########\n")
  print(populations.solve())
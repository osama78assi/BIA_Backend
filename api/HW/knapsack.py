import random

class TruckError(Exception):
  def __init__(self, arg) -> None:
    self.arg = arg

  def __str__(self):
    return self.arg


class TruckDp:
  def __init__(self, data: list[any, int, list]) -> None:
    # Some validation (this is part of an API so handling error is a good thing)
    if type(data) != list:
      raise TruckError("Data should be list with length of three first element is any data type, second is int and third is list")
    elif type(data[1]) != int:
      raise TruckError("Second element should be integar which is capacity of the truck")
    elif type(data[2]) != list:
      raise TruckError("Third element should be list which is the goods in the truck")
    # name of the truck
    self.name = data[0]
    # capacity of truck
    self.capacity = data[1]
    # payload of the truck, it will help use know what is left in goods
    self.payload = data[2].copy()
    # if the truck full then calculate the weights
    self.loaded = 0 if len(self.payload) == 0 else TruckDp.sumGoodsWeights(data[2])
    # quantity of every single goods in the truck
    self.quantity = 0 if len(self.payload) == 0 else TruckDp.sumGoodsQuantity(data[2])

  # it will help use make the data valid for Json parse
  @staticmethod
  def decodeTrucks(trucks, goods) -> dict:
    result = {"trucks": [], "goods": []}
    for truck in trucks:
      result["trucks"].append({
        "truckName": truck.name,
        "truckCapacity": truck.capacity,
        "payload": truck.payload,
        "totalQuantity": truck.quantity,
        "totalWeight": truck.loaded,
      })
    for item in goods:
      result["goods"].append(item)
    return result

  @staticmethod
  def sumGoodsQuantity(goods) -> int:
    acc = 0
    for single_goods in goods:
      acc += single_goods[2]
    return acc

  @staticmethod
  def sumGoodsWeights(goods) -> int:
    acc = 0
    for single_goods in goods:
      acc += single_goods[1]
    return acc

  # Helper function to reduce number of goods after fill each truck
  @staticmethod
  def filterGoods(goods: list, taken: list) -> list:
    indices = {item[3]:0 for item in taken} # Take the indices of the taken elements
    return list(filter(lambda item: indices[item[3]] if item[3] in indices else 1, goods)) # Filter

  # Function to fill trucks as needed
  @staticmethod
  def fillTrucks(goods: list, trucks: list) -> tuple:
    if(type(trucks) != list): raise TruckError("Trucks argumnt should be of type list")
    
    curr_truck = 0
    while curr_truck < len(trucks):
      if not isinstance(trucks[curr_truck], TruckDp): # If the element is truck
        raise TruckError(f"Element at index {curr_truck} in trucks list isn't a Truck type")
      trucks[curr_truck].fillTruck(goods)
      # Optimization
      goods = TruckDp.filterGoods(goods, trucks[curr_truck].payload)
      curr_truck += 1
    return trucks, goods
  
  # Function to fill one truck
  def fillTruck(self, goods) -> None:
    # NOTE: the function fillMaximumGoods should be a function in the class Truck
    # not inside this function but it will need a two properties addition on the object
    # to make dp dict and indices for unique each one so python has a nested functions it will help us
    
    # To remember each branch we opened in the recursive tree (memoization)
    dp = dict()
    # To remember indices we took in each result
    indices = dict()

    def fillMaximumGoods(i=0, current_weight=0, current_quantity=0):
      nonlocal dp # Take dp from the nearest scope that has dp
      nonlocal goods
      nonlocal indices # Take the indices from the nearst scope
      if i >= len(goods):
        return current_weight, current_quantity
      
      # check if the key exist in dict in python takes O(1) time complexity
      if (i, current_weight) in dp:
        return dp[(i, current_weight)]
      
      exclude_weight, exclude_value = fillMaximumGoods(i + 1, current_weight, current_quantity)

      # Include the current item (if it exceed the capacity then do pruning)
      if current_weight + goods[i][1] <= self.capacity:

        include_weight, include_value = fillMaximumGoods(i + 1, current_weight + goods[i][1], current_quantity + goods[i][2])
      else:
        include_weight, include_value = (-float("inf"), -float("inf")) # If we didn't include it return tiny value

      # Choose the better option
      if include_value > exclude_value:
        result = (include_weight, include_value)
        
        # We care about the item when we added it to the solution
        if result in indices:
          # Each result got an item then what is that item ? add it to the list if there is
          indices[result].append(i)
          # The list may hold repeated items for example [0, 1, 2] in 0 we ignored 0 and take one
          # and in 1 we took one and contiune to the list -> first time (0, 0) next time (1, X)
          # I could use Set but it's slow
        else:
          indices[result] = [i] # if not then create a list and add the index to it
      else:
        result = (exclude_weight, exclude_value)
      dp[(i, current_weight)] = result
      return result
    
    best = fillMaximumGoods() # solution
    # If there is goods
    if len(indices):
      taken = dict()
      for index in indices[best]:
        if goods[index][3] not in taken: # If the goods already taken don't take it (third element is the index of item)
          self += goods[index]
          taken[goods[index][3]] = 1 # Mark the element as taken
  
  # present the truck in a good way
  def __str__(self):
    return str(
      {
        self.name: {
          "capacity": self.capacity,
          "payload": self.payload,
          "loaded": self.loaded,
          "quantity": self.quantity,
        }
      }
    )

  # when adding goods to the truck (never add something except goods)
  def __add__(self, other):
    self.payload.append(other.copy())
    self.loaded += other[1]
    self.quantity += other[2]
    return self

# Data structure for trucks (for genetic solution)
class TruckGen:
  def __init__(self, capacity: int, name: str) -> None:
    self.items = []
    self.name = name
    self.fitness = 0 # Fitness is the total quantity
    self.totalWeight = 0
    self.capacity = capacity

  # Will be helpful after mutation and crossover to avoid wrong solution and calculate fitness
  def reCalcFitness(self, bestFitness):
    indecies = dict() # Mark the items to know if there is a repeat solution
    thereIsRepeat = False
    self.fitness = 0
    self.totalWeight = 0
    for i in range(len(self.items)):
      self.totalWeight += self.items[i][1]
      self.fitness += self.items[i][2]
      
      # We make sure the item get added once
      if self.items[i][3] in indecies: thereIsRepeat = True
      indecies[self.items[i][3]] = 1
    
    if self.totalWeight > self.capacity or thereIsRepeat:
      self.items.clear() # Change it into empty solution
    
    # Empty truck must have a chance to survive
    if len(self.items) == 0:
      self.fitness = random.randint(1, bestFitness)

  @staticmethod
  def decodeTrucks(trucks: list, goods: list, genCount: int, popCount: int):
    result = {
      "trucks": [],
      "goods": [],
      "generationsCount": genCount,
      "populationsCount": popCount,
    }
    
    for index in range(len(trucks)):
      result["trucks"].append({
        "truckName": trucks[index].name,
        "truckCapacity": trucks[index].capacity,
        "payload": trucks[index].items,
        "totalWeight": trucks[index].totalWeight,
        "totalQuantity": trucks[index].fitness
      })
    
    for item in goods:
      result["goods"].append(item)
    
    return result

  # Simulate adding an item
  def __add__(self, other):
    self.items.append(other) # Add the item
    self.totalWeight += other[1] # Add the weight
    self.fitness += other[2] # Then add the quantity as fitness
    return self

  # Represent the solution in a good way
  def __str__(self):
    return str({
      "name": self.name,
      "goods": self.items,
      "fitness": self.fitness,
      "capacity": self.capacity,
      "totalWeight": self.totalWeight
    })

# Class for solving the knapsack using genetic algoritm
class TruckGenSolution:
  def __init__(self, populationsCount: int, generationsCount: int, capacity: int, name: str, goods: list, crossoverProp = 0.7, mutationProp = 0.01) -> None:
    self.goods = goods
    self.name = name
    self.capacity = capacity
    self.populationsCount = populationsCount
    self.generationsCount = generationsCount
    self.bestFitness = -float("inf") # Keep track of best fitness with index (-inf because we maximize)
    self.INITIAL_FITNESS = 5 # When the first generations is empty take this as fitness
    self.lessWeight = float("inf") # Keep track of total weight for the best solution (inf because we minimize)
    self.bestFitnessIndex = -1
    self.totalFitness = 0 # Keep track of sum of the fitness (to calculate the probabilities easier)
    self.populations =[]
    self._initPopulations()
    self.CROSSOVERPROP = crossoverProp # Porbability of crossover
    self.MUTATIONPROP = mutationProp # Porbability of crossover

  def _initPopulations(self):
    totalFitness = 0
    for i in range(self.generationsCount):
      self.populations.append(TruckGen(self.capacity, self.name)) # Add first solution
      
      for item in self.goods:
        take = random.randint(0, 1) # either take the item or leave it
        chromosome = self.populations[i] # take the solution for more readable code
        
        if take == 1 :
          if chromosome.totalWeight + item[1] > chromosome.capacity: continue # Ignore the item if it ruin the solution (make the first generation correct solutions)
          chromosome += item
      
      if len(self.populations[i].items) == 0: # Empty truck
        self.populations[i].reCalcFitness(self.bestFitness if self.bestFitness != -float("inf") else self.INITIAL_FITNESS)
      # Add to total fitness
      totalFitness += self.populations[i].fitness
      # Find better fitenss till now
      self._betterFitness(self.populations[i], i)
    self.totalFitness = totalFitness # Save the total fitness
  
  # Helper function to take the length and determine the point
  def _findCrossoverMutationPoint(self, truckOne, truckTwo):
    # Take crossover point according to the min items count because the one which has less than other
    # if we added more to it more than what it holds it may overflow and ruin a solution
    itemsOne = len(truckOne.items)
    itemsTwo = len(truckTwo.items)
    
    minEndPoint = min(itemsOne-1 if itemsOne > 0 else itemsOne, itemsTwo-1 if itemsTwo > 0 else itemsTwo)
    maxEndPoint = max(itemsOne-1 if itemsOne > 0 else itemsOne, itemsTwo-1 if itemsTwo > 0 else itemsTwo)
    
    return itemsOne, itemsTwo, minEndPoint, maxEndPoint
  
  def _crossoverMutation(self):
    newFitnessSum = 0 # To keep track of sum of all fitness
    for i in range(0, self.populationsCount, 2):
      crossoverChance = random.random()
      mutationChance = random.random()
      thereIsCrossover = crossoverChance <= self.CROSSOVERPROP # To know if there is crossover
      thereIsMutation = mutationChance <= self.MUTATIONPROP # To know if there is mutation
      
      itemsOne, itemsTwo, minEndPoint, maxEndPoint = self._findCrossoverMutationPoint(self.populations[i], self.populations[i+1])
      # If both truks is empty ignore crossover
      if itemsOne == itemsTwo == 0: thereIsCrossover = False
      
      if thereIsCrossover:
        # When truck has one item fine but more than 1 don't include end (to not change position of solution)
        point = random.randint(0, minEndPoint if minEndPoint == 0 else minEndPoint-1)
        
        # Doing the crossover
        self.populations[i].items, self.populations[i+1].items = self.populations[i].items[:point] + self.populations[i+1].items[point:], \
          self.populations[i+1].items[:point] + self.populations[i].items[point:]
        
        # Redo this operations because after crossover the things have changed
        itemsOne, itemsTwo, minEndPoint, maxEndPoint = self._findCrossoverMutationPoint(self.populations[i], self.populations[i+1])
      
      if thereIsMutation:
        # The mutation for two empty solution
        if itemsOne == itemsTwo == 0:
          self.populations[i].items.append(self.goods[random.randint(0, len(self.goods)-1)]) # Put random element
          self.populations[i+1].items.append(self.goods[random.randint(0, len(self.goods)-1)]) # Put random element
        
        # May run into solution has zero items (index out of range expected)
        if minEndPoint == 0:
          randomPoint = random.randint(0, maxEndPoint) # Take random index from the one which has more
          
          if itemsTwo > itemsOne:
            self.populations[i].items.append(self.populations[i+1].items[randomPoint]) # Add to the empty solution random item from second solution
            self.populations[i+1].items[randomPoint] = self.goods[random.randint(0, len(self.goods)-1)] # Make mutation
          else:
            self.populations[i+1].items.append(self.populations[i].items[randomPoint])
            self.populations[i].items[randomPoint] = self.goods[random.randint(0, len(self.goods)-1)] # Make mutation
          
        else:
          randomPoint = random.randint(0, minEndPoint)
          # Doing the mutation -ex-> [1, 2, 3], [4, 5, 6] ; randPoint = 2 -result-> [1, 2, 6], [4, 5, 3]
          self.populations[i].items[randomPoint], self.populations[i+1].items[randomPoint] = self.populations[i+1].items[randomPoint], \
            self.populations[i].items[randomPoint]
      
      # Optimization
      # Re-calculate the fitness for each truck after any operations has happened
      if thereIsCrossover or thereIsMutation:
        # If the truck is empty it's not a wrong answer instead it's a solution that has a lot of opportunities
        # but it won't survive but what is the possibility of survive ?
        # We can generate it depened on the max fitness of current state
        self.populations[i].reCalcFitness(self.bestFitness if self.bestFitness != -float("inf") else self.INITIAL_FITNESS)
        self.populations[i+1].reCalcFitness(self.bestFitness if self.bestFitness != -float("inf") else self.INITIAL_FITNESS)

      newFitnessSum += self.populations[i].fitness + self.populations[i+1].fitness
      # Re-chose the better fitness
      self._betterFitness(self.populations[i], i)
      self._betterFitness(self.populations[i+1], i+1)
    # END FOR
    self.totalFitness = newFitnessSum # Save the new total fitness
  
  def _betterFitness(self, population, index):
    fitness = population.fitness
    totalWeight = population.totalWeight
    
    if fitness == self.bestFitness: # If both solutions has the same fitness take the less weight
      if totalWeight < self.lessWeight:
        self.bestFitness = fitness
        self.lessWeight = totalWeight
        self.bestFitnessIndex = index
    elif fitness > self.bestFitness: # Chose best fitness with index
      self.bestFitness = fitness
      self.lessWeight = totalWeight
      self.bestFitnessIndex = index
  
  def _selection(self):
    probs = [] # Probabilities of each solution to be selected
    for i in range(self.populationsCount):
      probs.append(self.populations[i].fitness / self.totalFitness)
    # Save the new selected populations
    self.populations = random.choices(self.populations, probs, k=self.populationsCount)
  
  @staticmethod
  def fillTrucks(trucksCapacities: list, trucksNames: list, goods: list, populationsCount: int, generationsCount: int) -> tuple:
    solutions = []
    for i in range(len(trucksCapacities)):
      truck = TruckGenSolution(populationsCount, generationsCount, trucksCapacities[i], trucksNames[i], goods).solve() # This will return TruckGen
      solutions.append(truck)
      # This step will reduce the amount of calculate fitness operations because it go over the goods list in each operation
      goods = TruckDp.filterGoods(goods, truck.items)
    
    return solutions, goods
  
  # The main goal
  def solve(self):
    for _ in range(self.generationsCount):
      self._selection()
      self._crossoverMutation()
    return self.populations[self.bestFitnessIndex]


if __name__ == "__main__":
  # Init trucks
  truck1 = TruckDp(["A", 18, []])
  truck2 = TruckDp(["B", 19, []])
  truck3 = TruckDp(["C", 9, []])
  # Init goods
  goods = [
  # Name, Weight, Quantity, index,
  ["Potato", 6, 6, 0],
  ["Tomato", 5, 6, 1],
  ["Carrot", 6, 4, 2],
  ["Melon", 6, 6, 3],
  ["Apple", 3, 5, 4],
  ["Orange", 7, 2, 5],
  ["Potato", 6, 6, 6],
  ]
  # Solve
  resultDp, resultGoods = TruckDp.fillTrucks(goods, [truck1, truck2, truck3])
  print("#########Dynamic Solution#########")
  print(truck1, truck2, truck3, sep="\n#######\n")
  print(f"Goods after: {resultDp}")

  # START GENETIC
  print(f"\n#########Genetic Solution#########")
  result, goodsAfter = TruckGenSolution.fillTrucks([18, 19, 9], ["A", "B", "C"], goods, 100, 100)
  for truck in result:
    print(truck)
  print("###")
  print(f"Goods After {goodsAfter}")



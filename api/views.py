from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .HW import knapsack
from .HW import TSP
from .HW import AStar
from .HW import shortestPathGenetic

@csrf_exempt
def solveTrucksGen(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      
      trucks = data.get("trucks", [])
      goods = data.get("goods", [])
      genCount = data.get("generationsCount", 100)
      popCount = data.get("populationsCount", 100)
      
      if len(trucks) == 0 or len(goods) == 0:
        return JsonResponse({"message": "Missing Data"}, safe=False, status=500)

      names = []
      capacities = []
      for truck in trucks:
        names.append(truck["name"])
        capacities.append(truck["capacity"])
      
      resultTrucks, resultGoods = knapsack.TruckGenSolution.fillTrucks(capacities, names, goods, popCount, genCount)
      result = knapsack.TruckGen.decodeTrucks(resultTrucks, resultGoods, genCount, popCount)
      response = {
        "data": result,
      }
      
      return JsonResponse(response)
    except json.JSONDecodeError as e:
      return JsonResponse({"message": "invalid JSON"}, safe=False, status=400)
  else:
    return JsonResponse({"message": "Only Post Allowed"}, safe=False, status=403)

@csrf_exempt
def solveTrucksDp(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      
      trucks = data.get("trucks", [])
      goods = data.get("goods", [])
      
      if len(trucks) == 0 or len(goods) == 0:
        return JsonResponse({"message": "Missing Data"}, safe=False, status=500)
      
      trucksResult, goodsResult = knapsack.TruckDp.fillTrucks(goods, list(map(lambda truck: knapsack.TruckDp([*truck.values(), []]), trucks)))
      result = knapsack.TruckDp.decodeTrucks(trucksResult, goodsResult)
      response = {
        "data": result
      }
      
      return JsonResponse(response)
    except json.JSONDecodeError as e:
      return JsonResponse({"message": "invalid JSON"}, safe=False, status=400)
  else:
    return JsonResponse({"message": "Only Post Allowed"}, safe=False, status=403)

@csrf_exempt
def sovleTSP(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      
      allEdges = data.get("allEdges")
      nodes = data.get("nodes")
      adjList = data.get("graph")
      start = data.get("start")
      popCount = data.get("populationsCount")
      gencount = data.get("generationsCount")
      
      if start == "" or not len(allEdges) or not len(nodes) or not len(adjList) or not gencount or not popCount:
        return JsonResponse({"message": "Missing Data"}, safe=False, status=500)
      graph = AStar.Graph(adjList, dict(), allEdges, nodes)
      tspPath = TSP.GeneticTSP(popCount, gencount, start, graph).solve().path
      
      response = {
        "path": tspPath
      }
      
      return JsonResponse(response)
    except json.JSONDecodeError as e:
      return JsonResponse({"message": "invalid JSON"}, safe=False, status=400)
  else:
    return JsonResponse({"message": "Only Post Allowed"}, safe=False, status=403)

@csrf_exempt
def shortestPathGen(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      
      allEdges = data.get("allEdges")
      nodes = data.get("nodes")
      adjList = data.get("graph")
      hTable = data.get("hTable")
      start = data.get("start")
      target = data.get("target")
      popCount = data.get("populationsCount")
      gencount = data.get("generationsCount")
      
      if start == "" or target == "" or not len(allEdges) or not len(nodes) or not len(adjList) or not len(hTable) or not gencount or not popCount:
        return JsonResponse({"message": "Missing Data"}, safe=False, status=500)
      
      graph = AStar.Graph(adjList, hTable, allEdges, nodes)
      path = shortestPathGenetic.GeneitcShortestPath(graph, popCount, gencount, start, target).solve().path
      response = {
        "path": path
      }
      
      return JsonResponse(response)
    except json.JSONDecodeError as e:
      return JsonResponse({"message": "invalid JSON"}, safe=False, status=400)
  else:
    return JsonResponse({"message": "Only Post Allowed"}, safe=False, status=403)

@csrf_exempt
def shortestPathA(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      
      allEdges = data.get("allEdges")
      nodes = data.get("nodes")
      adjList = data.get("graph")
      hTable = data.get("hTable")
      start = data.get("start")
      target = data.get("target")
      
      if start == "" or target == "" or not len(allEdges) or not len(nodes) or not len(adjList) or not len(hTable):
        return JsonResponse({"message": "Missing Data"}, safe=False, status=500)
      
      graph = AStar.Graph(adjList, hTable, allEdges, nodes)
      path = graph.findShortestPath(start, target)
      
      response = {
        "path": path.path
      }
      
      return JsonResponse(response)
    except json.JSONDecodeError as e:
      return JsonResponse({"message": "invalid JSON"}, safe=False, status=400)
  else:
    return JsonResponse({"message": "Only Post Allowed"}, safe=False, status=403)


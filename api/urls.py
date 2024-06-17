from . import views
from django.urls import path

urlpatterns = [
  path("solveTrucksGen", views.solveTrucksGen, name="solveTrucksGen"),
  path("solveTrucksDp", views.solveTrucksDp, name="solveTrucksDp"),
  path("sovleTSP", views.sovleTSP, name="sovleTSP"),
  path("shortestPathGen", views.shortestPathGen, name="shortestPathGen"),
  path("shortestPathA", views.shortestPathA, name="shortestPathA"),
]

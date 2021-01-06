from rest_framework import routers
from simulator import api_views as simulator_views

router = routers.SimpleRouter()
router.register(
    r'stocks',
    simulator_views.StockViewset,
    'stocks-list-api'
)
# router.register(
#     r'stocks/{pk}',
#     simulator_views.get_stock_detail,
#     'stock-detail-api'
# )

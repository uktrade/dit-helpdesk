from search.views import CommodityDocumentViewSet

from rest_framework.routers import SimpleRouter

app_name = 'search'

router = SimpleRouter()
router.register(
    prefix=r'',
    base_name='commodities',
    viewset=CommodityDocumentViewSet
)

urlpatterns = router.urls

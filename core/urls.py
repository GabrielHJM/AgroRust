from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PerfilJogadorViewSet, CartasBaseViewSet, 
    InventarioCartasViewSet, EdificiosJogadorViewSet,
    TerrenoGridViewSet, EstoqueArmazemViewSet,
    LojaViewSet, DeckJogadorViewSet, EdificioEspecialViewSet,
    RaideViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfis', PerfilJogadorViewSet, basename='perfil')
router.register(r'cartas', CartasBaseViewSet)
router.register(r'inventario', InventarioCartasViewSet, basename='inventario')
router.register(r'edificios', EdificiosJogadorViewSet, basename='edificios')
router.register(r'terrenos', TerrenoGridViewSet, basename='terrenos')
router.register(r'estoques', EstoqueArmazemViewSet, basename='estoque')
router.register(r'loja', LojaViewSet, basename='loja')
router.register(r'deck', DeckJogadorViewSet, basename='deck')
router.register(r'edificios-especiais', EdificioEspecialViewSet, basename='edificios-especiais')
router.register(r'raides', RaideViewSet, basename='raides')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

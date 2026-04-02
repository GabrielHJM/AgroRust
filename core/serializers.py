from rest_framework import serializers
from .models import (
    User, PerfilJogador, CartasBase, InventarioCartas, 
    EdificiosJogador, EdificioEspecial, TerrenoGrid, 
    EstoqueArmazem, DeckJogador, RegistroRaide
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_active']

class PerfilJogadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilJogador
        fields = '__all__'

class CartasBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartasBase
        fields = '__all__'

class InventarioCartasSerializer(serializers.ModelSerializer):
    carta_detalhada = CartasBaseSerializer(source='carta', read_only=True)

    class Meta:
        model = InventarioCartas
        fields = ['id', 'perfil', 'carta', 'carta_detalhada', 'quantidade', 'nivel']

class EdificiosJogadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdificiosJogador
        fields = '__all__'

class TerrenoGridSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerrenoGrid
        fields = '__all__'

class EstoqueArmazemSerializer(serializers.ModelSerializer):
    item_detalhado = CartasBaseSerializer(source='item', read_only=True)
    
    class Meta:
        model = EstoqueArmazem
        fields = ['id', 'perfil', 'item', 'item_detalhado', 'quantidade']

class DeckJogadorSerializer(serializers.ModelSerializer):
    cartas_detalhadas = CartasBaseSerializer(source='cartas', many=True, read_only=True)
    
    class Meta:
        model = DeckJogador
        fields = ['id', 'perfil', 'cartas', 'cartas_detalhadas']

class EdificioEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdificioEspecial
        fields = '__all__'

class RegistroRaideSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroRaide
        fields = '__all__'

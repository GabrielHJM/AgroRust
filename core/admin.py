from django.contrib import admin
from .models import (
    User, PerfilJogador, CartasBase, InventarioCartas, 
    EdificiosJogador, TerrenoGrid, EstoqueArmazem, 
    DeckJogador, EdificioEspecial, RegistroRaide
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_superuser')
    search_fields = ('email',)

@admin.register(PerfilJogador)
class PerfilJogadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'moedas_ouro', 'gemas_premium')
    search_fields = ('user__email',)

@admin.register(CartasBase)
class CartasBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'tipo', 'raridade')
    list_filter = ('tipo', 'raridade')
    search_fields = ('nome',)

@admin.register(InventarioCartas)
class InventarioCartasAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'carta', 'quantidade', 'nivel')
    list_filter = ('carta__tipo', 'carta__raridade')
    search_fields = ('perfil__user__email', 'carta__nome')

@admin.register(EdificiosJogador)
class EdificiosJogadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'casa_nivel', 'armazem_ocupacao', 'armazem_capacidade_maxima')
    search_fields = ('perfil__user__email',)

@admin.register(TerrenoGrid)
class TerrenoGridAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'x', 'y', 'carta', 'plantado_em', 'conclui_em')
    list_filter = ('carta__tipo',)
    search_fields = ('perfil__user__email',)

@admin.register(EstoqueArmazem)
class EstoqueArmazemAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'item', 'quantidade')
    search_fields = ('perfil__user__email', 'item__nome')

@admin.register(DeckJogador)
class DeckJogadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil')
    filter_horizontal = ('cartas',) # Interface amigável para selecionar as 8 cartas

@admin.register(EdificioEspecial)
class EdificioEspecialAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'tipo_especial', 'nivel', 'x', 'y', 'area_de_efeito')
    list_filter = ('tipo_especial',)
    search_fields = ('perfil__user__email',)

@admin.register(RegistroRaide)
class RegistroRaideAdmin(admin.ModelAdmin):
    list_display = ('id', 'atacante', 'vitima', 'ouro_saqueado', 'sucesso', 'data_raide')
    list_filter = ('sucesso', 'data_raide')
    search_fields = ('atacante__user__email', 'vitima__user__email')

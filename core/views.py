import random
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    User, PerfilJogador, CartasBase, InventarioCartas, 
    EdificiosJogador, TerrenoGrid, EstoqueArmazem, 
    DeckJogador, EdificioEspecial, RegistroRaide
)
from .serializers import (
    UserSerializer, PerfilJogadorSerializer, CartasBaseSerializer, 
    InventarioCartasSerializer, EdificiosJogadorSerializer,
    TerrenoGridSerializer, EstoqueArmazemSerializer,
    DeckJogadorSerializer, EdificioEspecialSerializer,
    RegistroRaideSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class PerfilJogadorViewSet(viewsets.ModelViewSet):
    """API endpoint that allows profiles to be viewed or edited."""
    def get_queryset(self):
        qs = PerfilJogador.objects.filter(user=self.request.user)
        for p in qs:
            p.processar_regeneracao()
        return qs
    serializer_class = PerfilJogadorSerializer

class CartasBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading available base cards."""
    queryset = CartasBase.objects.all()
    serializer_class = CartasBaseSerializer

class InventarioCartasViewSet(viewsets.ModelViewSet):
    """API endpoint for managing player cards inventory."""
    def get_queryset(self):
        return InventarioCartas.objects.filter(perfil__user=self.request.user)
    serializer_class = InventarioCartasSerializer

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        inventario = self.get_object()
        perfil = inventario.perfil
        
        copias_necessarias = inventario.nivel * 2
        ouro_necessario = inventario.nivel * 100

        if inventario.quantidade <= copias_necessarias:
            return Response(
                {"erro": f"Cópias insuficientes. Necessário ter mais de {copias_necessarias} (você usará {copias_necessarias}). Atual: {inventario.quantidade}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if perfil.moedas_ouro < ouro_necessario:
            return Response(
                {"erro": f"Ouro insuficiente para o Upgrade. Custo: {ouro_necessario}. Seu Saldo: {perfil.moedas_ouro}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            perfil.moedas_ouro -= ouro_necessario
            perfil.save()

            inventario.quantidade -= copias_necessarias
            inventario.nivel += 1
            inventario.save()

        return Response({
            "mensagem": f"Parabéns! Carta {inventario.carta.nome} subiu para o Nível {inventario.nivel}!",
            "novo_nivel": inventario.nivel,
            "copias_restantes": inventario.quantidade,
            "ouro_restante": perfil.moedas_ouro
        })

class EdificiosJogadorViewSet(viewsets.ModelViewSet):
    """API endpoint that allows buildings to be viewed or edited."""
    def get_queryset(self):
        return EdificiosJogador.objects.filter(perfil__user=self.request.user)
    serializer_class = EdificiosJogadorSerializer

class TerrenoGridViewSet(viewsets.ModelViewSet):
    """API endpoint for managing farm grid placement."""
    def get_queryset(self):
        return TerrenoGrid.objects.filter(perfil__user=self.request.user)
    serializer_class = TerrenoGridSerializer

class EstoqueArmazemViewSet(viewsets.ModelViewSet):
    """API endpoint for checking player stored items."""
    def get_queryset(self):
        return EstoqueArmazem.objects.filter(perfil__user=self.request.user)
    serializer_class = EstoqueArmazemSerializer

class LojaViewSet(viewsets.ViewSet):
    """API endpoint genérico para interações na Loja do Jogo."""
    
    @action(detail=False, methods=['post'], url_path='abrir-pacote')
    def abrir_pacote(self, request):
        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return Response({"erro": "Perfil de jogador não encontrado para este usuário."}, status=status.HTTP_400_BAD_REQUEST)

        custo = 500 
        if perfil.moedas_ouro < custo:
            return Response(
                {"erro": f"Ouro insuficiente para abrir o Pacote de Cartas. Custo: {custo}, Atual: {perfil.moedas_ouro}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cartas_db = list(CartasBase.objects.all())
        if not cartas_db:
             return Response({"erro": "Catálogo vazio! Crie CartasBase no Admin internamente primeiro."}, status=status.HTTP_400_BAD_REQUEST)

        pesos = { 'comum': 60, 'incomum': 25, 'raro': 10, 'epico': 4, 'lendario': 1 }
        roleta = []
        for carta in cartas_db:
            peso = pesos.get(carta.raridade, 10)
            roleta.extend([carta] * peso)

        sorteadas = []
        with transaction.atomic():
            perfil.moedas_ouro -= custo
            perfil.save()

            for _ in range(5):
                ganha = random.choice(roleta)
                sorteadas.append(ganha)
                
                inv, created = InventarioCartas.objects.get_or_create(
                    perfil=perfil, carta=ganha,
                    defaults={'quantidade': 1, 'nivel': 1}
                )
                if not created:
                    inv.quantidade += 1
                    inv.save()

        resumo = [ c.nome for c in sorteadas ]
        return Response({
            "mensagem": "Pacote aberto com sucesso! (-500 de Ouro)",
            "cartas_geradas": resumo,
            "ouro_restante": perfil.moedas_ouro
        })

class DeckJogadorViewSet(viewsets.ModelViewSet):
    """API endpoint for managing player's active deck."""
    def get_queryset(self):
        return DeckJogador.objects.filter(perfil__user=self.request.user)
    serializer_class = DeckJogadorSerializer

class EdificioEspecialViewSet(viewsets.ModelViewSet):
    """API endpoint for managing grid-based strategic buildings."""
    def get_queryset(self):
        return EdificioEspecial.objects.filter(perfil__user=self.request.user)
    serializer_class = EdificioEspecialSerializer

class RaideViewSet(viewsets.ViewSet):
    """Sistema de Ataques (Raides) CoC Style."""
    
    @action(detail=True, methods=['post'], url_path='atacar')
    def atacar(self, request, pk=None):
        atacante_perfil = getattr(request.user, 'perfil', None)
        if atacante_perfil:
            atacante_perfil.processar_regeneracao()

        try:
            vitima_perfil = PerfilJogador.objects.get(pk=pk)
            vitima_perfil.processar_regeneracao()
        except PerfilJogador.DoesNotExist:
            return Response({"erro": "Perfil alvo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if atacante_perfil == vitima_perfil:
            return Response({"erro": "Você não pode se auto-atacar."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Verificar Escudo da Vítima
        if vitima_perfil.escudo_ate and vitima_perfil.escudo_ate > timezone.now():
            restante = vitima_perfil.escudo_ate - timezone.now()
            mins = int(restante.total_seconds() // 60)
            return Response({"erro": f"Esta fazenda está sob um escudo de proteção por mais {mins} minutos."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Verificar se a vítima tem ouro para saquear
        if vitima_perfil.moedas_ouro < 100:
            return Response({"erro": "Esta fazenda está muito pobre para ser saqueada."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Lógica de Cálculo de Saque (CoC Style)
        # Base: 20% do ouro atual
        tentativa_saque = int(vitima_perfil.moedas_ouro * 0.20)
        
        # Redução por Defesa (AoE)
        # Se qualquer edifício de defesa (cerca, espantalho, cao) estiver no grid, ele reduz o saque
        defesas = EdificioEspecial.objects.filter(perfil=vitima_perfil)
        total_defesa = sum(d.poder_defesa for d in defesas)
        
        saque_final = max(0, tentativa_saque - (total_defesa * 10)) # Cada ponto de defesa tira 10 de ouro do saque

        with transaction.atomic():
            # Executa o Roubo
            vitima_perfil.moedas_ouro -= saque_final
            # Aplica Escudo de 12 horas após saque bem sucedido
            vitima_perfil.escudo_ate = timezone.now() + timedelta(hours=12)
            vitima_perfil.save()

            atacante_perfil.moedas_ouro += saque_final
            atacante_perfil.save()

            # Registra o Log
            log = RegistroRaide.objects.create(
                atacante=atacante_perfil,
                vitima=vitima_perfil,
                ouro_saqueado=saque_final,
                sucesso=True if saque_final > 0 else False
            )

        return Response({
            "mensagem": f"Invasão concluída! Você saqueou {saque_final} moedas de ouro.",
            "ouro_saqueado": saque_final,
            "vitima": vitima_perfil.user.email,
            "escudo_aplicado_na_vitima": "12 horas"
        })

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """User model."""
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class PerfilJogador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    moedas_ouro = models.PositiveIntegerField(default=0, verbose_name="Moedas de Ouro")
    gemas_premium = models.PositiveIntegerField(default=0, verbose_name="Gemas Premium")
    
    # Energia (Clash Royale / RPG Style)
    energia_maxima = models.PositiveIntegerField(default=100)
    energia_atual = models.PositiveIntegerField(default=100)
    
    # Combustível (AgroRust 2.1)
    gasolina_maxima = models.PositiveIntegerField(default=100)
    gasolina_atual = models.PositiveIntegerField(default=100)

    # Defesa
    escudo_ate = models.DateTimeField(null=True, blank=True, verbose_name="Escudo de Proteção Até")
    
    # Controle de Tempo (Regeneração Lazy)
    ultima_atualizacao_recursos = models.DateTimeField(default=timezone.now)

    def processar_regeneracao(self):
        """Calcula quanto de energia e gasolina deve ter regenerado desde o último acesso."""
        agora = timezone.now()
        diff = agora - self.ultima_atualizacao_recursos
        minutos_passados = int(diff.total_seconds() // 60)
        
        if minutos_passados > 0:
            # Regeneração: 1 ponto por minuto
            self.energia_atual = min(self.energia_maxima, self.energia_atual + minutos_passados)
            self.gasolina_atual = min(self.gasolina_maxima, self.gasolina_atual + minutos_passados)
            self.ultima_atualizacao_recursos = agora
            self.save()

    def __str__(self):
        return f"Perfil de {self.user.email}"

class CartasBase(models.Model):
    TIPOS_CARTAS = (
        ('semente', 'Semente'),
        ('maquina', 'Máquina'),
        ('fertilizante', 'Fertilizante'),
        ('vestuario', 'Vestuário'),
    )
    RARIDADES = (
        ('comum', 'Comum'),
        ('incomum', 'Incomum'),
        ('raro', 'Raro'),
        ('epico', 'Épico'),
        ('lendario', 'Lendário'),
    )
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS_CARTAS)
    raridade = models.CharField(max_length=20, choices=RARIDADES)
    imagem_url = models.URLField(max_length=500, blank=True, null=True)

    # Economia (AgroRust 2.1)
    RECURSO_CHOICES = (
        ('estamina', 'Estamina (Energia)'),
        ('gasolina', 'Gasolina (Combustível)'),
    )
    recurso_tipo = models.CharField(max_length=15, choices=RECURSO_CHOICES, default='estamina')
    custo_recurso = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.nome} ({self.get_raridade_display()})"

class InventarioCartas(models.Model):
    perfil = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='inventario_cartas')
    carta = models.ForeignKey(CartasBase, on_delete=models.CASCADE, related_name='inventarios')
    quantidade = models.PositiveIntegerField(default=1)
    nivel = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('perfil', 'carta')
        verbose_name = "Inventário de Carta"
        verbose_name_plural = "Inventários de Cartas"

    def __str__(self):
        return f"{self.quantidade}x {self.carta.nome} Nv.{self.nivel} (Jogador: {self.perfil.user.email})"

class DeckJogador(models.Model):
    """Sistema de Deck (Clash Royale Style) - Escolha de 8 cartas ativas."""
    perfil = models.OneToOneField(PerfilJogador, on_delete=models.CASCADE, related_name='deck')
    cartas = models.ManyToManyField(CartasBase, related_name='decks_que_participa')

    def clean(self):
        # Validação de limite de 8 cartas no deck (regra opcional no salvamento)
        if self.pk and self.cartas.count() > 8:
            raise ValidationError("Um deck não pode ter mais de 8 cartas.")

    class Meta:
        verbose_name = "Deck do Jogador"

class EdificiosJogador(models.Model):
    perfil = models.OneToOneField(PerfilJogador, on_delete=models.CASCADE, related_name='edificios')
    
    # Casa
    casa_nivel = models.PositiveIntegerField(default=1)
    casa_skin = models.CharField(max_length=100, default='padrao')
    
    # Armazem
    armazem_nivel = models.PositiveIntegerField(default=1)
    armazem_capacidade_maxima = models.PositiveIntegerField(default=100)
    armazem_ocupacao = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Edifício do Jogador"
        verbose_name_plural = "Edifícios dos Jogadores"

    def __str__(self):
        return f"Edifícios de {self.perfil.user.email}"

class EdificioEspecial(models.Model):
    """Edifícios Estratégicos (Clash of Clans Style) com Área de Efeito (AoE)."""
    TIPOS_EDIFICIOS = (
        ('poco', 'Poço Artesiano'), # Dá bônus de crescimento
        ('cerca', 'Cerca Reforçada'), # Protege contra roubos (raides)
        ('espantalho', 'Espantalho Místico'), # Afasta pragas ou ladrões
        ('celeiro', 'Celeiro de Maquinário'), # Reduz custo de energia de máquinas
    )
    perfil = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='edificios_especiais')
    tipo_especial = models.CharField(max_length=20, choices=TIPOS_EDIFICIOS)
    
    # Posicionamento no Grid
    x = models.IntegerField()
    y = models.IntegerField()
    
    nivel = models.PositiveIntegerField(default=1)
    area_de_efeito = models.PositiveIntegerField(default=1) # Raio em quadrados (CoC Style)
    
    # Atributos de Combate (AgroRust 2.1)
    saude_maxima = models.PositiveIntegerField(default=100)
    saude_atual = models.PositiveIntegerField(default=100)
    poder_defesa = models.PositiveIntegerField(default=10) # Redução de saque ou dano

    class Meta:
        unique_together = ('perfil', 'x', 'y')
        verbose_name = "Edifício Especial (Grid)"

    def __str__(self):
        return f"{self.get_tipo_especial_display()} Nv.{self.nivel} em [{self.x},{self.y}]"

class TerrenoGrid(models.Model):
    perfil = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='terrenos')
    x = models.IntegerField()
    y = models.IntegerField()
    carta = models.ForeignKey(CartasBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='grids_posicionados')
    plantado_em = models.DateTimeField(null=True, blank=True)
    conclui_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('perfil', 'x', 'y')
        verbose_name = "Terreno Grid"
        verbose_name_plural = "Terrenos Grid"

    def clean(self):
        if not self.pk and TerrenoGrid.objects.filter(perfil=self.perfil, x=self.x, y=self.y).exists():
            raise ValidationError(f"A coordenada ({self.x}, {self.y}) já está ocupada no terreno.")

    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Regenera antes de gastar (AgroRust 2.1)
        self.perfil.processar_regeneracao()

        # Lógica de Desconto de Recursos (AgroRust 2.1)
        if not self.pk and self.carta:
            perfil = self.perfil
            custo = self.carta.custo_recurso
            
            if self.carta.recurso_tipo == 'estamina':
                if perfil.energia_atual < custo:
                    raise ValidationError(f"Estamina insuficiente! Necessário: {custo}, Atual: {perfil.energia_atual}")
                perfil.energia_atual -= custo
            else:
                if perfil.gasolina_atual < custo:
                    raise ValidationError(f"Gasolina insuficiente! Necessário: {custo}, Atual: {perfil.gasolina_atual}")
                perfil.gasolina_atual -= custo
            
            perfil.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Grid [{self.x},{self.y}] de {self.perfil.user.email} - Carta: {self.carta.nome if self.carta else 'Vazio'}"

class EstoqueArmazem(models.Model):
    perfil = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='estoques')
    item = models.ForeignKey(CartasBase, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('perfil', 'item')
        verbose_name = "Estoque do Armazém"
        verbose_name_plural = "Estoques do Armazém"

    def clean(self):
        qs = EstoqueArmazem.objects.filter(perfil=self.perfil)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
            
        ocupacao_atual = sum(estoque.quantidade for estoque in qs)
        nova_ocupacao = ocupacao_atual + self.quantidade

        try:
            capacidade_maxima = self.perfil.edificios.armazem_capacidade_maxima
        except EdificiosJogador.DoesNotExist:
            capacidade_maxima = 0

        if nova_ocupacao > capacidade_maxima:
            raise ValidationError(f"Capacidade do Armazém excedida! Limite: {capacidade_maxima}, Tentativa: {nova_ocupacao}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.item.nome} no Armazém de {self.perfil.user.email}"

class RegistroRaide(models.Model):
    """Logs de Ataques (Raides) entre jogadores."""
    atacante = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='ataques_realizados')
    vitima = models.ForeignKey(PerfilJogador, on_delete=models.CASCADE, related_name='defesas_sofridas')
    ouro_saqueado = models.PositiveIntegerField(default=0)
    sucesso = models.BooleanField(default=False)
    data_raide = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Sucesso" if self.sucesso else "Falha"
        return f"Raide: {self.atacante.user.email} -> {self.vitima.user.email} ({status})"

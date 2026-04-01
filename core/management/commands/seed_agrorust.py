import random
from django.core.management.base import BaseCommand
from core.models import (
    User, PerfilJogador, CartasBase, InventarioCartas, 
    EdificiosJogador, DeckJogador, EdificioEspecial
)

class Command(BaseCommand):
    help = 'Seeds the database with initial game data and a test user.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create Test User
        user, created = User.objects.get_or_create(
            email='admin@agrorust.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Agro',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {user.email} created.'))
        else:
            self.stdout.write(f'User {user.email} already exists.')

        # 2. Ensure Profile and Buildings exist
        perfil, created = PerfilJogador.objects.get_or_create(
            user=user,
            defaults={
                'moedas_ouro': 10000, 
                'gemas_premium': 1000,
                'energia_atual': 100,
                'gasolina_atual': 100
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Profile created with 10k Gold and 1k Gems.'))
        
        EdificiosJogador.objects.get_or_create(
            perfil=perfil,
            defaults={'casa_nivel': 1, 'armazem_capacidade_maxima': 100}
        )

        # 3. Seed Base Cards
        cartas = [
            # Sementes (Gasto: Estamina)
            {'nome': 'Semente de Trigo', 'tipo': 'semente', 'raridade': 'comum', 'imagem_url': 'seed_trigo.png', 'recurso_tipo': 'estamina', 'custo_recurso': 5},
            {'nome': 'Semente de Milho', 'tipo': 'semente', 'raridade': 'comum', 'imagem_url': 'seed_milho.png', 'recurso_tipo': 'estamina', 'custo_recurso': 5},
            {'nome': 'Semente de Tomate', 'tipo': 'semente', 'raridade': 'incomum', 'imagem_url': 'seed_tomate.png', 'recurso_tipo': 'estamina', 'custo_recurso': 8},
            {'nome': 'Semente de Algodão', 'tipo': 'semente', 'raridade': 'incomum', 'imagem_url': 'seed_algodao.png', 'recurso_tipo': 'estamina', 'custo_recurso': 8},
            {'nome': 'Semente de Soja Mística', 'tipo': 'semente', 'raridade': 'raro', 'imagem_url': 'seed_soja_mistic.png', 'recurso_tipo': 'estamina', 'custo_recurso': 15},
            {'nome': 'Rosa de Cristal', 'tipo': 'semente', 'raridade': 'epico', 'imagem_url': 'seed_rosa_cristal.png', 'recurso_tipo': 'estamina', 'custo_recurso': 25},
            {'nome': 'Árvore de Ouro', 'tipo': 'semente', 'raridade': 'lendario', 'imagem_url': 'seed_tree_gold.png', 'recurso_tipo': 'estamina', 'custo_recurso': 50},
            
            # Máquinas (Gasto: Gasolina)
            {'nome': 'Trator Velho', 'tipo': 'maquina', 'raridade': 'comum', 'imagem_url': 'machine_trator_old.png', 'recurso_tipo': 'gasolina', 'custo_recurso': 10},
            {'nome': 'Irrigador Simples', 'tipo': 'maquina', 'raridade': 'comum', 'imagem_url': 'machine_irrigator.png', 'recurso_tipo': 'gasolina', 'custo_recurso': 5},
            {'nome': 'Colheitadeira A1', 'tipo': 'maquina', 'raridade': 'incomum', 'imagem_url': 'machine_harvester_a1.png', 'recurso_tipo': 'gasolina', 'custo_recurso': 20},
            {'nome': 'Drone de Monitoramento', 'tipo': 'maquina', 'raridade': 'raro', 'imagem_url': 'machine_drone.png', 'recurso_tipo': 'gasolina', 'custo_recurso': 15},
            {'nome': 'Mega Trator Turbo', 'tipo': 'maquina', 'raridade': 'epico', 'imagem_url': 'machine_trator_turbo.png', 'recurso_tipo': 'gasolina', 'custo_recurso': 40},
            
            # Fertilizantes (Gasto: Estamina)
            {'nome': 'Adubo Comum', 'tipo': 'fertilizante', 'raridade': 'comum', 'imagem_url': 'item_adubo.png', 'recurso_tipo': 'estamina', 'custo_recurso': 10},
            {'nome': 'Fertilizante Rápido', 'tipo': 'fertilizante', 'raridade': 'incomum', 'imagem_url': 'item_fert_fast.png', 'recurso_tipo': 'estamina', 'custo_recurso': 15},
            {'nome': 'Poção de Crescimento', 'tipo': 'fertilizante', 'raridade': 'raro', 'imagem_url': 'item_potion.png', 'recurso_tipo': 'estamina', 'custo_recurso': 30},
        ]

        for c_data in cartas:
            obj, c = CartasBase.objects.get_or_create(nome=c_data['nome'], defaults=c_data)
            if c:
                self.stdout.write(f'Card {obj.nome} created.')

        # 4. Give some initial cards to the player
        if InventarioCartas.objects.filter(perfil=perfil).count() == 0:
            cartas_db = list(CartasBase.objects.all())
            for _ in range(5):
                carta = random.choice(cartas_db)
                InventarioCartas.objects.create(
                    perfil=perfil,
                    carta=carta,
                    quantidade=random.randint(1, 5),
                    nivel=1
                )
            self.stdout.write(self.style.SUCCESS('Initial inventory seeded.'))

        # 5. Create Initial Deck (active 8 cards)
        deck, created = DeckJogador.objects.get_or_create(perfil=perfil)
        if deck.cartas.count() == 0:
            all_inventory = list(InventarioCartas.objects.filter(perfil=perfil))
            # Pega até 8 cartas do inventário para o deck
            for inv_item in all_inventory[:8]:
                deck.cartas.add(inv_item.carta)
            self.stdout.write(self.style.SUCCESS(f'Initial deck created with {deck.cartas.count()} cards.'))

        # 6. Create some Special Buildings (CoC Style)
        if EdificioEspecial.objects.filter(perfil=perfil).count() == 0:
            EdificioEspecial.objects.create(
                perfil=perfil,
                tipo_especial='poco',
                x=5, y=5,
                nivel=1,
                area_de_efeito=2
            )
            self.stdout.write(self.style.SUCCESS('Initial special buildings (Poço) created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))

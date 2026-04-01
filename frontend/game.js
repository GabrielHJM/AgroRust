// API
const API_BASE_URL = 'http://localhost:8000/api';
let draggingCardData = null; 

class InterfaceManager {
    constructor() {
        this.goldDisplay = document.getElementById('gold-amount');
        this.gemsDisplay = document.getElementById('gems-amount');
        this.energyDisplay = document.getElementById('energy-amount');
        this.gasolineDisplay = document.getElementById('gasoline-amount');
        this.shieldDisplay = document.getElementById('shield-status');
        this.deckContainer = document.getElementById('card-deck');
        this.loginOverlay = document.getElementById('login-overlay');
        this.loginForm = document.getElementById('login-form');
        this.loginError = document.getElementById('login-error');
        this.token = localStorage.getItem('agrorust_token');
    }

    async boot() {
        if (!this.token) { this.showLogin(); return; }
        this.hideLogin();
        if (!window.game) window.game = new Phaser.Game(config);
        await this.fetchEconomics();
        await this.fetchDeck(); // Agora busca o Deck Ativo (Royale Style)
        this.setupDragDropGlobal();
    }

    showLogin() {
        this.loginOverlay.style.display = 'flex';
        this.loginForm.onsubmit = async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            try {
                const res = await fetch(`http://localhost:8000/api/token/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                if (res.ok) {
                    const data = await res.json();
                    this.token = data.access;
                    localStorage.setItem('agrorust_token', this.token);
                    this.boot();
                } else { this.loginError.innerText = "Erro no Login."; }
            } catch (err) { this.loginError.innerText = "Erro de conexão."; }
        };
    }

    hideLogin() { this.loginOverlay.style.display = 'none'; }

    async authFetch(url, options = {}) {
        const res = await fetch(url, {
            ...options,
            headers: { ...options.headers, 'Authorization': `Bearer ${this.token}`, 'Content-Type': 'application/json' }
        });
        if (res.status === 401) { localStorage.removeItem('agrorust_token'); location.reload(); }
        return res;
    }

    async fetchEconomics() {
        try {
            const req = await this.authFetch(`${API_BASE_URL}/perfis/`);
            const perfis = await req.json();
            if(perfis.length > 0) {
                const p = perfis[0];
                this.goldDisplay.innerText = p.moedas_ouro;
                this.gemsDisplay.innerText = p.gemas_premium;
                this.energyDisplay.innerText = `${p.energia_atual}/${p.energia_maxima}`;
                this.gasolineDisplay.innerText = `${p.gasolina_atual}/${p.gasolina_maxima}`;

                // Lógica de exibição do Escudo
                if (p.escudo_ate) {
                    const agora = new Date();
                    const expira = new Date(p.escudo_ate);
                    if (expira > agora) {
                        this.shieldDisplay.style.display = 'inline-flex';
                        const diffMins = Math.ceil((expira - agora) / (1000 * 60));
                        this.shieldDisplay.title = `Protegido por mais ${diffMins} minutos`;
                    } else {
                        this.shieldDisplay.style.display = 'none';
                    }
                } else {
                    this.shieldDisplay.style.display = 'none';
                }
            }
        } catch (e) {}
    }

    // CLASH ROYALE STYLE: Busca apenas as 8 cartas do DECK ATIVO
    async fetchDeck() {
        try {
            const req = await this.authFetch(`${API_BASE_URL}/deck/`);
            const decks = await req.json();
            this.deckContainer.innerHTML = "";

            if(decks.length === 0 || decks[0].cartas_detalhadas.length === 0) {
                this.deckContainer.innerHTML = `<div style="margin:auto; opacity:0.5;">Monte seu deck no painel!</div>`;
                return;
            }

            const activeDeck = decks[0];
            activeDeck.cartas_detalhadas.forEach(carta => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'carta-ui';
                cardDiv.setAttribute('draggable', 'true');
                cardDiv.innerHTML = `
                    <div class="rarity ${carta.raridade}"></div>
                    <span class="name">${carta.nome}</span>
                `;
                cardDiv.addEventListener('dragstart', (e) => {
                    draggingCardData = { card_id: carta.id, name: carta.nome };
                });
                cardDiv.addEventListener('dragend', () => { setTimeout(() => draggingCardData = null, 50); });
                this.deckContainer.appendChild(cardDiv);
            });
        } catch (e) {}
    }

    setupDragDropGlobal() {
        const gameContainer = document.getElementById('phaser-app');
        gameContainer.addEventListener('dragover', (e) => e.preventDefault());
        gameContainer.addEventListener('drop', (e) => e.preventDefault());
    }
}

// PHASER FARM SCENE
class FarmScene extends Phaser.Scene {
    constructor() { super('FarmScene'); this.gridSize = 64; }

    create() {
        this.cameras.main.setBackgroundColor('#7CB342');
        this.drawGrid();
        this.input.on('pointerup', this.handleCanvasDrop, this);
        this.fetchTerrenos();
        this.fetchEdificiosEspeciais(); // CLASH OF CLANS STYLE: Poe os edifícios no grid
    }

    drawGrid() {
        const graphics = this.add.graphics();
        graphics.lineStyle(1, 0x000000, 0.15);
        for (let i = 0; i < this.scale.width; i += this.gridSize) { graphics.moveTo(i, 0); graphics.lineTo(i, this.scale.height); }
        for (let j = 0; j < this.scale.height; j += this.gridSize) { graphics.moveTo(0, j); graphics.lineTo(this.scale.width, j); }
        graphics.strokePath();
    }

    async handleCanvasDrop(pointer) {
        if (!draggingCardData) return;
        const gx = Math.floor(pointer.worldX / this.gridSize);
        const gy = Math.floor(pointer.worldY / this.gridSize);

        try {
            const req = await window.uiManager.authFetch(`${API_BASE_URL}/terrenos/`, {
                method: 'POST',
                body: JSON.stringify({ x: gx, y: gy, carta: draggingCardData.card_id })
            });

            if(req.ok) {
                this.add.rectangle(gx * 64 + 32, gy * 64 + 32, 58, 58, 0x8d6e63);
                this.add.text(gx * 64 + 5, gy * 64 + 25, draggingCardData.name.substring(0,6), { fontSize: '10px' });
                // Atualiza energia após plantar
                window.uiManager.fetchEconomics();
            } else {
                const err = await req.json();
                alert(JSON.stringify(err));
            }
        } catch(e) {}
        draggingCardData = null;
    }

    async fetchTerrenos() {
        const req = await window.uiManager.authFetch(`${API_BASE_URL}/terrenos/`);
        const data = await req.json();
        data.forEach(t => {
            this.add.rectangle(t.x * 64 + 32, t.y * 64 + 32, 58, 58, 0x8d6e63);
        });
    }

    // CLASH OF CLANS: Renderiza Poços, Cercas, etc.
    async fetchEdificiosEspeciais() {
        try {
            const req = await window.uiManager.authFetch(`${API_BASE_URL}/edificios-especiais/`);
            const edificios = await req.json();
            edificios.forEach(e => {
                // Desenha Edifício (Azul para diferenciar de plantas)
                this.add.rectangle(e.x * 64 + 32, e.y * 64 + 32, 60, 60, 0x1976D2);
                this.add.text(e.x * 64 + 5, e.y * 64 + 25, e.tipo_especial.toUpperCase(), { fontSize: '10px', fontStyle: 'bold' });
                
                // Desenha Área de Efeito (AoE) - Círculo transparente
                const circle = this.add.circle(e.x * 64 + 32, e.y * 64 + 32, e.area_de_efeito * 64, 0x2196F3, 0.1);
            });
        } catch(e) {}
    }
}

const config = {
    type: Phaser.AUTO,
    parent: 'phaser-app',
    width: '100%',
    height: '100%',
    scale: { mode: Phaser.Scale.RESIZE, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [FarmScene]
};

window.onload = () => {
    window.uiManager = new InterfaceManager();
    window.uiManager.boot();
};

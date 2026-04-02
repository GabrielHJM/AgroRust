// AGRO RUST WEATHER MANAGER
class WeatherManager {
    constructor(ui) {
        this.ui = ui;
        this.currentState = 'clear';
    }

    // O Clima agora é passivo, sincronizado pelo InterfaceManager
    sync(state) {
        if (this.currentState !== state) {
            this.setWeather(state);
        }
    }

    setWeather(state) {
        this.currentState = state;
        this.ui.updateWeatherHUD(state);
        if (window.game && window.game.scene.getScene('FarmScene')) {
            window.game.scene.getScene('FarmScene').applyAtmosphere(state);
        }
        
        // Som Ambiente de Chuva
        if (state === 'rain' || state === 'storm') {
            this.ui.soundManager.playSFX('rain_loop', true);
        } else {
            if (this.ui.soundManager.loops['rain_loop']) {
                this.ui.soundManager.loops['rain_loop'].pause();
            }
        }
    }
}

// AGRO RUST SETTINGS MANAGER
class SettingsManager {
    constructor(ui) {
        this.ui = ui;
        this.defaults = {
            fps: 60,
            quality: 'medium',
            hud: true,
            music: 50,
            sfx: 70
        };
        this.data = JSON.parse(localStorage.getItem('agrorust_settings')) || { ...this.defaults };
    }

    save() {
        localStorage.setItem('agrorust_settings', JSON.stringify(this.data));
        this.apply();
    }

    apply() {
        if (this.ui.soundManager) {
            this.ui.soundManager.setMusicVolume(this.data.music);
            this.ui.soundManager.sfxVolume = this.data.sfx / 100;
        }

        if (window.game) {
            window.game.loop.targetFps = parseInt(this.data.fps);
        }

        if (window.game && window.game.scene.getScene('FarmScene')) {
            window.game.scene.getScene('FarmScene').updateQuality(this.data.quality);
        }

        document.getElementById('hud-container').style.display = this.data.hud ? 'block' : 'none';
        
        document.getElementById('setting-fps').value = this.data.fps;
        document.getElementById('setting-quality').value = this.data.quality;
        document.getElementById('setting-hud').checked = this.data.hud;
        document.getElementById('volume-music').value = this.data.music;
        document.getElementById('volume-sfx').value = this.data.sfx;
    }
}

// AGRO RUST SOUND MANAGER
class SoundManager {
    constructor() {
        this.music = new Audio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'); 
        this.music.loop = true;
        this.sfxVolume = 0.7;
        this.loops = {};
    }

    playMusic() { this.music.play().catch(e => {}); }
    setMusicVolume(vol) { this.music.volume = vol / 100; }
    
    playSFX(type, isLoop = false) {
        const sounds = {
            'click': 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3',
            'plant': 'https://assets.mixkit.co/active_storage/sfx/2591/2591-preview.mp3',
            'attack': 'https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3',
            'rain_loop': 'https://assets.mixkit.co/active_storage/sfx/2453/2453-preview.mp3'
        };
        const audio = new Audio(sounds[type]);
        audio.volume = this.sfxVolume;
        if(isLoop) {
            audio.loop = true;
            this.loops[type] = audio;
        }
        audio.play();
    }
}

class InterfaceManager {
    constructor() {
        this.goldDisplay = document.getElementById('gold-amount');
        this.gemsDisplay = document.getElementById('gems-amount');
        this.energyDisplay = document.getElementById('energy-amount');
        this.gasolineDisplay = document.getElementById('gasoline-amount');
        this.shieldDisplay = document.getElementById('shield-status');
        this.weatherIcon = document.querySelector('.weather-icon');
        this.deckContainer = document.getElementById('card-deck');
        
        this.authContainer = document.getElementById('auth-container');
        this.loginScreen = document.getElementById('login-screen');
        this.mainMenu = document.getElementById('main-menu');
        this.welcomeUser = document.getElementById('welcome-user');
        
        this.loginForm = document.getElementById('login-form');
        this.loginError = document.getElementById('login-error');
        this.token = localStorage.getItem('agrorust_token');
        
        this.soundManager = new SoundManager();
        this.settings = new SettingsManager(this);
        this.weather = new WeatherManager(this);
        
        this.setupMenuButtons();
        this.settings.apply();
        this.setupSettingsListeners();
    }

    updateWeatherHUD(state) {
        const icons = {
            'clear': 'fa-sun',
            'rain': 'fa-cloud-showers-heavy',
            'heat': 'fa-fire',
            'storm': 'fa-cloud-bolt'
        };
        const colors = {
            'clear': '#FFCA28',
            'rain': '#4FC3F7',
            'heat': '#FF7043',
            'storm': '#7E57C2'
        };
        this.weatherIcon.className = `fa-solid ${icons[state]} weather-icon`;
        this.weatherIcon.style.color = colors[state];
    }

    async boot() {
        if (!this.token) { this.showLogin(); return; }
        await this.showMainMenu();
    }

    showLogin() {
        this.authContainer.style.display = 'flex';
        this.loginScreen.style.display = 'block';
        this.mainMenu.style.display = 'none';

        this.loginForm.onsubmit = async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            try {
                const res = await fetch(`http://localhost:8000/api/token/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                if (res.ok) {
                    const data = await res.json();
                    this.token = data.access;
                    localStorage.setItem('agrorust_token', this.token);
                    this.showMainMenu();
                } else { this.loginError.innerText = "Usuário ou senha incorretos."; }
            } catch (err) { this.loginError.innerText = "Erro de conexão."; }
        };
    }

    async showMainMenu() {
        this.authContainer.style.display = 'flex';
        this.loginScreen.style.display = 'none';
        this.mainMenu.style.display = 'block';
        try {
            const req = await this.authFetch(`${API_BASE_URL}/users/me/`);
            if (req.ok) {
                const user = await req.json();
                this.welcomeUser.innerText = `Olá, ${user.username}!`;
            }
        } catch (e) { this.welcomeUser.innerText = `Bem-vindo!`; }
    }

    setupMenuButtons() {
        document.getElementById('btn-new-game').onclick = async () => {
            if(confirm("Deseja resetar sua fazenda?")) {
                const res = await this.authFetch(`${API_BASE_URL}/perfis/novo_jogo/`, { method: 'POST' });
                if(res.ok) this.startGame();
            }
        };
        document.getElementById('btn-load-game').onclick = () => this.startGame();
        document.getElementById('btn-exit').onclick = () => {
            localStorage.removeItem('agrorust_token');
            location.reload();
        };
        document.getElementById('btn-options').onclick = () => {
            document.getElementById('options-modal').style.display = 'flex';
        };
    }

    setupSettingsListeners() {
        const fps = document.getElementById('setting-fps');
        const quality = document.getElementById('setting-quality');
        const hud = document.getElementById('setting-hud');
        const music = document.getElementById('volume-music');
        const sfx = document.getElementById('volume-sfx');

        fps.onchange = (e) => { this.settings.data.fps = e.target.value; this.settings.save(); };
        quality.onchange = (e) => { this.settings.data.quality = e.target.value; this.settings.save(); };
        hud.onchange = (e) => { this.settings.data.hud = e.target.checked; this.settings.save(); };
        music.oninput = (e) => { this.settings.data.music = e.target.value; this.settings.save(); };
        sfx.oninput = (e) => { this.settings.data.sfx = e.target.value; this.settings.save(); };
    }

    async startGame() {
        this.authContainer.style.display = 'none';
        this.soundManager.playMusic();
        if (!window.game) window.game = new Phaser.Game(config);
        await this.fetchEconomics();
        await this.fetchDeck();
        await this.fetchPanels(); 
        this.setupDragDropGlobal();
        this.settings.apply();
        // Polling constante para manter clima e recursos sincronizados
        setInterval(() => this.fetchEconomics(), 10000);
    }

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
                
                // Sincroniza Clima
                this.weather.sync(p.clima_atual || 'clear');
                
                if (p.escudo_ate) {
                    const expira = new Date(p.escudo_ate);
                    if (expira > new Date()) {
                        this.shieldDisplay.style.display = 'inline-flex';
                    } else { this.shieldDisplay.style.display = 'none'; }
                } else { this.shieldDisplay.style.display = 'none'; }
            }
        } catch (e) {}
    }

    async fetchPanels() {
        const reqInv = await this.authFetch(`${API_BASE_URL}/inventario/`);
        const invData = await reqInv.json();
        const machinePanel = document.querySelector('#panel-machines .panel-content');
        machinePanel.innerHTML = "";
        invData.filter(i => i.carta_detalhada.tipo === 'maquina').forEach(m => {
            machinePanel.innerHTML += `<div class="machine-item"><span>${m.carta_detalhada.nome} Nv.${m.nivel}</span><div class="status online">x${m.quantidade}</div></div>`;
        });

        const reqEst = await this.authFetch(`${API_BASE_URL}/estoques/`);
        const estData = await reqEst.json();
        const warehousePanel = document.querySelector('#panel-warehouse .panel-content');
        warehousePanel.innerHTML = "";
        estData.forEach(i => {
            warehousePanel.innerHTML += `<div class="machine-item"><span>${i.item_detalhado.nome}</span><small>Qtd: ${i.quantidade}</small></div>`;
        });
    }

    async fetchDeck() {
        const req = await this.authFetch(`${API_BASE_URL}/deck/`);
        const decks = await req.json();
        this.deckContainer.innerHTML = "";
        
        // Mapeamento de Imagens para as Cartas (Baseado no nome/slug)
        const imageMap = {
            'Trator': 'agrorust_tractor_premium_1775088524505.png',
            'Colheitadeira': 'agrorust_harvester_premium_1775088568489.png',
            'Semente de Trigo': 'agrorust_crop_wheat_premium_1775088581666.png',
            'Sede Modular': 'agrorust_house_premium_1775088542098.png'
        };

        if(decks.length > 0) {
            decks[0].cartas_detalhadas.forEach(c => {
                const img = imageMap[c.nome] || 'agrorust_crop_wheat_premium_1775088581666.png';
                const div = document.createElement('div');
                div.className = `carta-ui rarity-${c.raridade}`;
                div.setAttribute('draggable', 'true');
                div.innerHTML = `
                    <div class="card-image" style="background-image: url('${img}')"></div>
                    <span class="name">${c.nome}</span>
                `;
                div.addEventListener('dragstart', () => draggingCardData = { card_id: c.id, name: c.nome });
                this.deckContainer.appendChild(div);
            });
        }
    }

    showRaidMenu() {
        const modal = document.getElementById('raid-modal');
        const list = document.getElementById('rivals-list');
        modal.style.display = 'flex';
        this.authFetch(`${API_BASE_URL}/raides/listar_rivais/`).then(res => res.json()).then(data => {
            list.innerHTML = "";
            data.forEach(r => {
                const div = document.createElement('div');
                div.className = 'rival-item';
                div.innerHTML = `<div class="rival-info"><span>${r.username}</span><small>${r.ouro} Ouro</small></div><button class="btn-attack" ${r.protegido ? 'disabled' : ''} onclick="window.uiManager.performRaid(${r.id})">ATACAR</button>`;
                list.appendChild(div);
            });
        });
    }

    async performRaid(id) {
        this.soundManager.playSFX('attack');
        const res = await this.authFetch(`${API_BASE_URL}/raides/${id}/atacar/`, { method: 'POST' });
        const data = await res.json();
        alert(data.mensagem || data.erro);
        document.getElementById('raid-modal').style.display = 'none';
        this.fetchEconomics();
    }

    setupDragDropGlobal() {
        const canvas = document.getElementById('phaser-app');
        canvas.addEventListener('dragover', (e) => e.preventDefault());
    }
}

// PHASER FARM SCENE
class FarmScene extends Phaser.Scene {
    constructor() { super('FarmScene'); this.gridSize = 64; this.weatherParticles = null; }

    preload() {
        // Gera um pixel branco processualmente para as partículas
        const canvas = document.createElement('canvas');
        canvas.width = 1; canvas.height = 1;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 1, 1);
        this.textures.addCanvas('pixel', canvas);

        // Carrega Ativos Premium Gerados
        this.load.image('tractor', 'agrorust_tractor_premium_1775088524505.png');
        this.load.image('harvester', 'agrorust_harvester_premium_1775088568489.png');
        this.load.image('house', 'agrorust_house_premium_1775088542098.png');
        this.load.image('wheat', 'agrorust_crop_wheat_premium_1775088581666.png');
        this.load.image('character', 'agrorust_character_portrait_1775088507310.png');
    }

    create() {
        this.cameras.main.setBackgroundColor('#455A64');
        this.drawGrid();
        this.input.on('pointerup', this.handleCanvasDrop, this);
        this.fetchTerrenos();
        this.fetchEdificiosEspeciais();
        
        document.querySelector('.toggle-right').addEventListener('contextmenu', (e) => {
            e.preventDefault();
            window.uiManager.showRaidMenu();
        });

        this.applyVisuals();
    }

    updateQuality(quality) { this.applyVisuals(quality); }

    applyVisuals(quality = null) {
        const q = quality || window.uiManager.settings.data.quality;
        this.cameras.main.resetPostPipeline();
        if (q === 'ultra') {
            this.cameras.main.setPostPipeline(Phaser.Renderer.WebGL.Pipelines.FX.Bloom);
            this.cameras.main.setPostPipeline(Phaser.Renderer.WebGL.Pipelines.FX.Vignette);
        } else if (q === 'medium') {
            this.cameras.main.setPostPipeline(Phaser.Renderer.WebGL.Pipelines.FX.Vignette);
        }
    }

    applyAtmosphere(state) {
        if (this.weatherParticles) this.weatherParticles.destroy();
        
        if (state === 'rain' || state === 'storm') {
            this.weatherParticles = this.add.particles(0, 0, 'pixel', {
                x: { min: 0, max: 1200 },
                y: -10,
                speedY: { min: 300, max: 500 },
                lifespan: 2000,
                quantity: 2,
                scale: { start: 0.1, end: 0.2 },
                alpha: { start: 0.6, end: 0 }
            });
            if (state === 'storm') {
                this.time.addEvent({ delay: 5000, callback: () => this.cameras.main.flash(500), loop: true });
            }
        }
        
        if (state === 'heat' && window.uiManager.settings.data.quality === 'ultra') {
            this.cameras.main.setPostPipeline(Phaser.Renderer.WebGL.Pipelines.FX.Shine);
        }
    }

    juiceUp(obj) {
        this.tweens.add({
            targets: obj,
            scaleX: 1.2,
            scaleY: 0.8,
            duration: 100,
            yoyo: true,
            ease: 'Sine.easeInOut'
        });
    }

    drawGrid() {
        const g = this.add.graphics();
        g.lineStyle(1, 0x000000, 0.1);
        for (let i = 0; i < this.scale.width; i += 64) { g.moveTo(i, 0); g.lineTo(i, this.scale.height); }
        for (let j = 0; j < this.scale.height; j += 64) { g.moveTo(0, j); g.lineTo(this.scale.width, j); }
        g.strokePath();
    }

    async handleCanvasDrop(pointer) {
        if (!draggingCardData) return;
        const gx = Math.floor(pointer.worldX / 64);
        const gy = Math.floor(pointer.worldY / 64);
        
        // Alerta Visual de Clima
        const weather = window.uiManager.weather.currentState;
        if (weather === 'heat') console.log("🔥 Onda de calor: Custo de energia +2");

        try {
            const res = await window.uiManager.authFetch(`${API_BASE_URL}/terrenos/`, {
                method: 'POST',
                body: JSON.stringify({ x: gx, y: gy, carta: draggingCardData.card_id })
            });
            if(res.ok) {
                window.uiManager.soundManager.playSFX('plant');
                
                // Mapeia o Sprite com base no nome da carta
                const name = draggingCardData.name;
                let key = 'wheat';
                if (name.includes('Trator')) key = 'tractor';
                if (name.includes('Colheitadeira')) key = 'harvester';
                if (name.includes('Sede')) key = 'house';

                const spr = this.add.sprite(gx * 64 + 32, gy * 64 + 32, key);
                spr.setDisplaySize(58, 58);
                this.juiceUp(spr);
                
                if (weather === 'rain') console.log("🌧️ Crescimento acelerado (Chuva)!");
                if (weather === 'storm') console.log("⚡ Crescimento ULTRA acelerado (Tempestade)!");
                
                window.uiManager.fetchEconomics();
            } else {
                const data = await res.json();
                alert(data.error || "Recursos insuficientes.");
            }
        } catch(e) {}
        draggingCardData = null;
    }

    async fetchTerrenos() {
        const req = await window.uiManager.authFetch(`${API_BASE_URL}/terrenos/`);
        const data = await req.json();
        const map = { 'maquina': 'tractor', 'semente': 'wheat' };
        data.forEach(t => { 
            const key = t.carta_detalhada ? map[t.carta_detalhada.tipo] : 'wheat';
            const spr = this.add.sprite(t.x * 64 + 32, t.y * 64 + 32, key);
            spr.setDisplaySize(58, 58);
        });
    }

    async fetchEdificiosEspeciais() {
        const req = await window.uiManager.authFetch(`${API_BASE_URL}/edificios-especiais/`);
        const edfs = await req.json();
        edfs.forEach(e => {
            const spr = this.add.sprite(e.x * 64 + 32, e.y * 64 + 32, 'house');
            spr.setDisplaySize(60, 60);
            this.add.circle(e.x * 64 + 32, e.y * 64 + 32, e.area_de_efeito * 64, 0x2196F3, 0.05);
        });
    }
}

const config = {
    type: Phaser.AUTO,
    parent: 'phaser-app',
    width: '100%',
    height: '100%',
    scale: { mode: Phaser.Scale.RESIZE, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [FarmScene],
    fps: { target: 60, forceSetTimeOut: true }
};

window.onload = () => {
    window.uiManager = new InterfaceManager();
    window.uiManager.boot();
};

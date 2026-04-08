# AgroRust 🚜🌾

*Da enxada à automação industrial.*

O **AgroRust** é um simulador agrícola web visionário que rompe com a estética infantilizada dos jogos de fazenda tradicionais. Ele combina o peso e o realismo do trabalho no campo com a inovação mecânica de jogos de cartas (deck-building) e RPG. O jogador atua como um arquiteto do seu próprio império agrícola, gerenciando não apenas o plantio, mas o clima, o maquinário pesado e a economia de mercado.

## 🚀 Visão Geral do Projeto

Construído sob uma arquitetura de software sólida, o sistema utiliza um painel de controle robusto no backend para cálculos financeiros precisos e persistência de dados, enquanto entrega uma experiência fluida, reativa e de alta fidelidade visual no navegador do usuário, com adaptação Mobile-First.

### 🌟 Diferenciais e Mecânicas
* **Sistema de Cartas (Deck & Upgrade):** Sementes, fertilizantes e maquinário pesado (como a Aradeira Mecânica) são representados por cartas que podem ser colecionadas, aprimoradas e aplicadas no grid da fazenda (Drag-and-Drop).
* **Matriz Espacial (Grid-based RPG):** O jogador tem total liberdade para organizar sua sede, galpão e plantações utilizando um sistema inteligente de coordenadas (X, Y).
* **Clima e Realismo em WebGL:** Tempestades, poeira e ciclos diurnos dinâmicos que afetam diretamente a jogabilidade e a durabilidade dos implementos.
* **Economia Dinâmica e Mercado:** Um sistema de cotação flutuante onde o preço das safras dita as regras do lucro diário, forçando gestão estratégica do Armazém.

## 🛠️ Arquitetura e Tecnologias

O projeto valoriza as bases tradicionais de desenvolvimento web em harmonia com motores gráficos modernos:

**Backend (O Cérebro Financeiro e Lógico)**
* **Python / Django:** Gestão de usuários, segurança, autenticação de sessão e lógica de negócios.
* **Django Rest Framework (DRF):** Criação da API RESTful para comunicação ágil com o motor do jogo.
* **PostgreSQL:** Banco de dados relacional de alta confiabilidade para salvar os estados do inventário, coordenadas e transações financeiras.

**Frontend (O Palco)**
* **Phaser.js:** Motor HTML5/WebGL para renderização em tempo real, física e sistemas de partículas (chuva/poeira).
* **HTML5 / CSS3 (Grid & Flexbox):** Interface (HUD) desenhada de forma responsiva, adaptando-se do desktop para o toque no celular sem perda de imersão.

**Infraestrutura**
* Hospedagem planejada no **Render**, garantindo escalabilidade para o tráfego do servidor e banco de dados.

## ⚙️ Instalação e Execução Local

Siga os passos abaixo para rodar o ambiente de desenvolvimento na sua máquina:

1. **Ative o ambiente virtual (venv):**
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Instale as dependências (se necessário):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o servidor de desenvolvimento Django:**
   ```bash
   python manage.py runserver
   ```
   *O backend estará rodando em `http://localhost:8000/`. É necessário que ele esteja ativo para o jogo funcionar.*

4. **Abra o Jogo:**
   - Navegue até a pasta `frontend/` e abra o arquivo `index.html` em seu navegador.
   - **Dica:** Para uma melhor experiência e evitar problemas de cache, você pode usar a extensão "Live Server" do VS Code.

5. **Login de Teste:**
   - **Usuário:** `farmer`
   - **Senha:** `agrorust123` *(Resetei a senha para facilitar seu teste)*

---

## 🏗️ Estado Atual do Projeto

- [x] Backend Django CRUD + Auth JWT
- [x] Motor de Jogo Phaser 3 Integrado
- [x] Sistema de Clima e Regeneração de Recursos
- [x] Sprites Premium de Maquinário e Edifícios
- [ ] Sistema de Marketplace (Em desenvolvimento)

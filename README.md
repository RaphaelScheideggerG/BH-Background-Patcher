# Brawlhalla Background Patcher (BHBP)

### O Problema
No cenário competitivo de Brawlhalla, a clareza visual é fundamental. Muitos jogadores preferem substituir os fundos detalhados dos mapas por imagens minimalistas ou cores sólidas para aumentar o contraste e maximizar a taxa de quadros (FPS). No entanto, o jogo exige que o usuário substitua manualmente no diretório da Steam, renomeando cada um deles para corresponder ao mapa específico — um processo repetitivo, propenso a erros e ineficiente.

---

### A Solução
O BBP é uma ferramenta desktop desenvolvida em Python que automatiza esse "gargalo" de produtividade. Com apenas um clique, o software valida o diretório do jogo, realiza o backup das texturas originais e aplica a nova imagem de fundo em todos os mapas selecionados.

---

### Funcionalidades
1. GUI
2. Validar local da pasta
3. Tentar preenchimento automatico por diretório padrão (Linux, Windows, MacOS)
4. Aceitar varios tipos de imagem se possivel converter para o padrão do brawlhalla (jpg)
5. Opção de modo para seleção especifica ou exceção dos arquivos a serem substituidos
6. Alguns fundos já inclusos para seleção com previsualização
7. Sugerir caminho para reverter mudanças

---

### Desafios
0. Isolar ambiente e compilar programa para windows (.exe) e linux (.deb)
- penso depois do MVP

1. Escolha da biblioteca de GUI
- Tkinter e customtkinter -> visual diferente do padrão windows (feio) ✖️
- PyWin32 para chamar apis nativas windows -> complicado complicado ✖️
- Flet -> framework para projeto simples... ✖️
- PySide6 -> biblioteca oficial (licença LGPL) ✔️

2. Normalizar o tamanho da janela para diferentes resoluções ou não? 

3. Validar o local da pasta e preenchimento automático

---

### Estrutura do Projeto

BH-Background-Patcher/
│
├── .venv/                  # Ambiente virtual (isolado)
├── .gitignore              # Ignora .venv, __pycache__, e arquivos temporários
├── requirements.txt        # PySide6, pytest, etc.
├── README.md               # Documentação épica
│
├── src/                    # Código-fonte (Core da aplicação)
│   ├── __init__.py
│   ├── main.py             # Ponto de entrada (Inicia a GUI)
│   ├── logic.py            # O "Cérebro" (Funções de cópia, backup e validação)
│   └── ui/                 # Arquivos de interface (.ui do Designer ou .py)
│       ├── __init__.py
│       └── main_window.py
│
├── tests/                  # Para testes unitarios
│   ├── __init__.py
│   ├── conftest.py         # Configurações globais do PyTest
│   └── test_logic.py       # Testes das funções de arquivo e validação
│
└── assets/                 # Ícones, imagens de exemplo e sons
    └── app_icon.ico

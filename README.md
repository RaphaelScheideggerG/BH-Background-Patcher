# Brawlhalla Background Patcher (BHBP)

### O Problema
No cenário competitivo de Brawlhalla, a clareza visual é fundamental. Muitos jogadores preferem substituir os fundos detalhados dos mapas por imagens minimalistas ou cores sólidas para aumentar o contraste e maximizar a taxa de quadros (FPS). No entanto, o jogo exige que o usuário faça essa substituição manualmente no diretório da Steam, renomeando arquivo por arquivo para corresponder a cada mapa. Esse processo manual se torna extremamente maçante e repetitivo, transformando-se em uma dor de cabeça constante para quem formata o PC com frequência, precisa reinstalar o jogo ou simplesmente gosta de alternar entre diferentes fundos de tela.

### A Solução
O BHBP é uma ferramenta desktop desenvolvida em Python que elimina essa repetição exaustiva. Pensado exatamente para facilitar a manutenção do seu setup visual após formatações ou reinstalações, o software automatiza todo o processo. Com apenas um clique, ele valida o diretório do jogo, realiza o backup das texturas originais e aplica a nova imagem de fundo em todos os mapas selecionados, poupando tempo e garantindo que você volte a jogar rapidamente.

---

### Tech Stack
Linguagem: Python 3.12+
GUI Framework: PySide6 (Qt for Python)
Manipulação de Arquivos: shutil, pathlib
Build Tool: PyInstaller (para o .exe futuro)

### Funcionalidades
1. GUI
2. Validar local da pasta
3. Tentar preenchimento automatico por diretório padrão (Linux, Windows, MacOS)
4. Aceitar varios tipos de imagem se possivel converter para o padrão do brawlhalla (jpg)
5. Opção de modo para seleção especifica ou exceção dos arquivos a serem substituidos
6. Alguns fundos já inclusos para seleção com previsualização
7. Sugerir caminho para reverter mudanças
8. redimensionar imagem caso seja menor que o jogo requer
9. Backup e opção para reverter alterações 
10. Criar executável

---

### Desafios / Decisões
0. Isolar ambiente e compilar programa para windows (.exe) e linux (.deb)
- penso depois do MVP

1. Escolha da biblioteca de GUI
- Tkinter e customtkinter -> visual diferente do padrão windows (feio) ✖️
- PyWin32 para chamar apis nativas windows -> complicado complicado ✖️
- Flet -> framework para projeto simples... ✖️
- PySide6 -> biblioteca oficial (licença LGPL) ✔️

2. Responsividade
- Uso das QVboxes

3. Validar o local da pasta e preenchimento automático
- verificação de existencia do diretório e preenchimento automático para diretórios padrões baseado no sistema operacional

4. Tecnicas de redimensionamento de imagens para os padrões do jogo (fit x fill) e estilo de salvamento da imagem redimensionada como copia.
- 
- tempfile ou salvar na pasta do executável -> tempfile polui menos o ambiente, ideal para um programa de uso simples e direto.

5. Formato de backup dos arquivos originais na pasta.
- Salva arquivos modificados em pasta local no diretório do instalador.

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
│       ├── main_window.py
│       ├── mode_selection.py
│       └── path_selection.py
│
├── tests/                  # Para testes unitários
│   ├── __init__.py
│   ├── conftest.py         # Configurações globais do PyTest
│   └── test_logic.py       # Testes das funções de arquivo e validação
│
└── assets/                 # Ícones, imagens de exemplo e sons
    └── app_icon.ico


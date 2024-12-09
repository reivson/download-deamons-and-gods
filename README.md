# Tales of Demons and Gods Manga Downloader

Um script Python para baixar capítulos do mangá Tales of Demons and Gods.

## Funcionalidades
- Lista os capítulos mais recentes com suas variações
- Baixa todas as imagens dos capítulos selecionados
- Organiza os capítulos em pastas separadas
- Mostra o progresso do download com barras de progresso
- Lida com variações de capítulos (ex: capítulo 487 parte 1, parte 5, etc.)
- Salva os arquivos em um local específico

## Requisitos
Instale os pacotes necessários usando:
```bash
pip install -r requirements.txt
```

## Configuração
O script está configurado para baixar os capítulos em:
```
C:\Users\nieli\Pictures\demonsandgods
```

Para alterar o local de download, modifique a variável `DOWNLOAD_DIR` no arquivo `image_downloader.py`.

## Como Usar
1. Execute o script:
```bash
python image_downloader.py
```

2. O script mostrará uma lista dos capítulos disponíveis
3. Digite o número do capítulo que deseja baixar (ex: "487")
4. Se o capítulo tiver múltiplas partes, selecione a parte desejada
5. O script baixará todas as imagens desse capítulo para o diretório configurado

## Estrutura de Diretórios
Os downloads são organizados da seguinte forma:
```
demonsandgods/
├── chapter_487.0_part_1/
│   ├── page_001.jpg
│   ├── page_002.jpg
│   └── ...
├── chapter_487.0_part_5/
│   ├── page_001.jpg
│   └── ...
└── ...
```

## Observações
- Alguns sites podem bloquear downloads automatizados
- Certifique-se de ter permissão para baixar o conteúdo
- O script inclui vários seletores de imagem para lidar com diferentes layouts de sites
- Se nenhuma imagem for encontrada, informações de depuração serão exibidas

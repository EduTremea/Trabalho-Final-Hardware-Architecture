# Raspberry Pi

São dois programas, que conversam pelo banco SQLite:

- `coletor.py`: lê o Arduino, calcula o risco, controla o relé, atualiza o LCD e grava no banco.
- `web/app.py`: site com o painel, os gráficos e os controles.

## Instalação (Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y python3-venv python3-rpi.gpio git
git clone https://github.com/EduTremea/Trabalho-Final-Hardware-Architecture.git
cd Trabalho-Final-Hardware-Architecture/raspberry
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo usermod -aG dialout,gpio $USER   # acesso à serial e ao GPIO; depois saia e entre de novo
```

## Como rodar

Em dois terminais, com o `.venv` ativado:

```bash
python coletor.py        # terminal 1
python web/app.py        # terminal 2
```

O site abre em `http://<ip-do-raspberry>:5000`. Para descobrir o IP: `hostname -I`.

O gráfico usa o Chart.js pela internet. Se a rede da apresentação não tiver internet, baixe o `chart.umd.min.js` antes e coloque em `web/static/`, trocando o endereço no `index.html`.

## Sem o Arduino

```bash
python coletor.py --simular
```

Gera leituras falsas num ciclo de 3 minutos (tempo bom, céu fechando, chuva forte e melhora).

## Testes

```bash
python -m pytest
```

## Ajuste para a apresentação

Ao soprar o DHT11, a umidade sobe, mas a temperatura também sobe por causa do ar quente. Para a demonstração, desmarque no site a opção "Umidade só conta se a temperatura cair".

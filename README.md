# Furia Challenge

## Visão Geral
Este projeto combina um frontend em Vue.js com um backend em Django REST Framework, utilizando Docker para conteinerização e gerenciamento do ambiente.

## Pré-requisitos
- Docker ([instalação](https://docs.docker.com/get-docker/))
- Docker Compose
- Node.js (opcional para desenvolvimento fora do container)
- Python 3.x (opcional para desenvolvimento fora do container)

## Estrutura do Projeto

- Raiz : furiaproject/
- backend: furiaproject/backend/
- front-end: furiaproject/front-end/chatbotfuria/

## Configuração Inicial
```bash
git clone [URL_DO_REPOSITÓRIO]
cd furiaproject

docker-compose up --build (Antes, faça os passos de criar a .env abaixo e volte aqui) 

Caso queira uma conta de admin, use python manage.py createsuperuser no container do backend
```


## Backend
Crie arquivos .env na raiz de front-end e na raiz de backend para criar as váriaveis de ambiente.


no arquivo back-end, coloque as chaves das API's tanto do twitter quanto da openai 

OPENAI_API_KEY="sua-chave-de-api-aqui"

TWITTER_CLIENT_ID=sua-chave-de-api-aqui

TWITTER_CLIENT_SECRET=sua-chave-de-api-aqui

TWITTER_BEARER_TOKEN=sua-chave-de-api-aqui



no arquivo front-end coloque as URLS locais que você irá utilizar

VITE_API_BASE=http://localhost:8000

DEFAULT_URL=http://localhost:3000



## Acessos
Frontend: http://localhost:3000

Backend: http://localhost:8000

Admin Django: http://localhost:8000/admin


## Projeto

Eu utilizei um formato de chatbot com sistema de autenticação "login e register" para utilizar na 2° parte do challenge.

A aplicação salva históricos de conversações por usuário, podendo ser utilizado na 2° etapa do challenge que é a "Know your fan".

Existem 5 níveis de torcedores:

Iniciante

Fã Casual/Regular

Grande fã

Fanático (garante acesso a uma carteirinha FURIA)

DOIDO POR FURIA! (garante acesso a uma carteirinha FURIA) - nível mais alto.

O bot também avalia suas compras, eventos visitados, interações do twitter (caso conta esteja vinculada) e traz um feedback do seu perfil de torcedor.

 
## Observação importante

A api gratuita do X limita para buscas recentes a cada 15 minutos, portanto, caso comece dar unauthorized nos terminais/consoles, é normal, a cada 15 minutos 1 req pode ser feita.



# MACHINE LEARNING - RECOMENDADOR DE MÚSICAS

## Nomes:

- Gabriel Frigo Petuco - 22280417
- Leonardo Forner - 21100996
- Marco Ames - 17103283

## Procedimentos para executar:

O servidor e o cliente estão disponíveis online pela plataforma Render. Você pode utilizá-los das seguintes formas:

1. Para fazer requisições diretamente ao servidor, utilize: https://spotifyrecommender.onrender.com/recommend.

Obs: Quando o servidor não está em uso por um tempo, ele entra em modo de hibernação. A primeira requisição após esse período pode levar alguns segundos enquanto o servidor "acorda".

2. Alternativamente, pode-se usar o sistema usando o frontend disponível em: https://spotifyrecommender-front.onrender.com. Abrir o servidor antes.

Utilizamos um .env para o client ID e o client secret para integrar com a API do Spotify.

### Exemplo de requisicao POST em formato JSON:

```bash
curl -X POST https://spotifyrecommender.onrender.com/recommend \
-H "Content-Type: application/json" \
-d '{
  "songs": [
    {
      "name": "Without Me",
      "year": 2002,
      "artists": "Eminem"
    }
  ]
}'

```

### Exemplo de resposta do servidor:

```bash
{
   "recommendations": [
       {
           "artists": "Nelly, City Spud",
           "name": "Ride Wit Me",
           "year": 2000
       },
       {
           "artists": "Dr. Dre, Eminem",
           "name": "Forgot About Dre",
           "year": 1999
       },
       {
           "artists": "Snoop Dogg, Kurupt, Warren G, Nate Dogg",
           "name": "Ain't No Fun (If the Homies Cant Have None) (feat. Nate Dogg, Warren G & Kurupt)",
           "year": 1993
       },
       {
           "artists": "Insane Clown Posse",
           "name": "My Axe",
           "year": 2007
       },
       {
           "artists": "Kid Cudi, Eminem",
           "name": "The Adventures of Moon Man & Slim Shady (with Eminem)",
           "year": 2020
       },
       {
           "artists": "KEVVO, J Balvin",
           "name": "Billetes Azules (with J Balvin)",
           "year": 2020
       },
       {
           "artists": "Juvenile, Lil Wayne, Mannie Fresh",
           "name": "Back That Azz Up",
           "year": 1998
       },
       {
           "artists": "Eminem",
           "name": "Just Lose It",
           "year": 2004
       },
       {
           "artists": "Future, Lil Uzi Vert",
           "name": "Moment of Clarity",
           "year": 2020
       },
       {
           "artists": "Ozuna, Doja Cat, Sia",
           "name": "Del Mar",
           "year": 2020
       }
   ]
}
```

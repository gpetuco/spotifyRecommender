from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
import warnings
import os
from dotenv import load_dotenv
from flask_cors import CORS
import ast

# Configurações iniciais
warnings.filterwarnings("ignore")
load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    raise ImportError("Você precisa instalar a biblioteca spotipy com: pip install spotipy")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# App Flask
app = Flask(__name__)
CORS(app)

# Carrega dados
data = pd.read_csv("data/data.csv")

def try_parse_list(x):
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return x

if 'artists' in data.columns:
    data['artists'] = data['artists'].apply(try_parse_list)

numColunas = list(data.select_dtypes(np.number).columns)

# Clustering e escalonamento
clusterSongs = Pipeline([
    ('scaler', StandardScaler()), 
    ('kmeans', KMeans(n_clusters=20, verbose=False))
])
X = data[numColunas]
clusterSongs.fit(X)
data['cluster_label'] = clusterSongs.predict(X)

# Modelo KNN
scaler = clusterSongs.named_steps['scaler']
X_scaled = scaler.transform(X)
knn_model = NearestNeighbors(n_neighbors=30, metric='cosine')
knn_model.fit(X_scaled)

# === Funções utilitárias ===
def findMusics(name, year):
    dataSongs = defaultdict()
    results = sp.search(q=f'track: {name} year: {year}', limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    dataSongs['name'] = [name]
    dataSongs['year'] = [year]
    dataSongs['explicit'] = [int(results['explicit'])]
    dataSongs['duration_ms'] = [results['duration_ms']]
    dataSongs['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        dataSongs[key] = value

    return pd.DataFrame(dataSongs)


def getMusicas(song, spotifyDados):
    matched_song = spotifyDados[(spotifyDados['name'] == song['name']) & (spotifyDados['year'] == song['year'])]
    if not matched_song.empty:
        return matched_song.iloc[0]
    else:
        try:
            return findMusics(song['name'], song['year']).iloc[0]
        except Exception as e:
            print(f"Erro ao buscar {song['name']} ({song['year']}): {e}")
            return None


def getVetor(listaMusicas, spotifyDados):
    vetorMusicas = []
    for song in listaMusicas:
        dataSongs = getMusicas(song, spotifyDados)
        if dataSongs is None:
            print(f"Atenção: {song['name']} não encontrada.")
            continue
        vetorMusicas.append(dataSongs[numColunas].values)

    if len(vetorMusicas) == 0:
        raise ValueError("Nenhuma música válida foi encontrada para gerar recomendação.")

    matrizMusicas = np.array(vetorMusicas)
    return np.mean(matrizMusicas, axis=0)


def flatten_dict_list(dict_list):
    flattened_dict = defaultdict(list)
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
    return flattened_dict


# === Função de recomendação com KNN ===
def recomendar(listaMusicas, spotifyDados, n_songs=10):
    metadata_cols = ['name', 'year', 'artists'] if 'artists' in spotifyDados.columns else ['name', 'year']
    song_dict = flatten_dict_list(listaMusicas)

    song_center = getVetor(listaMusicas, spotifyDados)
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))

    distances, indices = knn_model.kneighbors(scaled_song_center, n_neighbors=n_songs*2)
    index = indices[0]

    rec_songs = spotifyDados.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])].head(n_songs)

    def artists_to_str(a):
        if isinstance(a, list):
            return ", ".join(a)
        elif isinstance(a, str):
            return a
        else:
            return str(a)

    rec_songs['artists'] = rec_songs['artists'].apply(artists_to_str)

    return rec_songs[metadata_cols].to_dict(orient='records')


# === Rota de recomendação ===
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        input_data = request.get_json()
        if not input_data or 'songs' not in input_data:
            return jsonify({'error': 'Requisição inválida. Envie um JSON com a chave "songs".'}), 400
        
        songs = input_data['songs']
        recommendations = recomendar(songs, data)
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# === Início do servidor ===
if __name__ == '__main__':
    app.run(debug=True)

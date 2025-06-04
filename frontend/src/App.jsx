import React, { useEffect, useState, useMemo, useRef } from "react";
import "./spotify.css";

export default function Home() {
  const [tracks, setTracks] = useState([]);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [filteredVisible, setFilteredVisible] = useState(false);
  const debounceTimeout = useRef(null);

  useEffect(() => {
    fetch("/tracks.json")
      .then((res) => res.json())
      .then((data) => setTracks(data))
      .catch((err) => console.error("Erro ao carregar as músicas:", err));
  }, []);

  const handleInputChange = (value) => {
    setQuery(value);
    setFilteredVisible(true);
    setSelectedTrack(null);

    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      setDebouncedQuery(value);
    }, 300);
  };

  const filteredTracks = useMemo(() => {
    if (!debouncedQuery) return [];
    const lower = debouncedQuery.toLowerCase();
    return tracks
      .filter(
        (t) =>
          t.name.toLowerCase().includes(lower) ||
          t.artists.toLowerCase().includes(lower)
      )
      .slice(0, 20);
  }, [debouncedQuery, tracks]);

  const handleSelectTrack = (track) => {
    setSelectedTrack(track);
    setQuery(track.name);
    setFilteredVisible(false);
  };

  const handleRecommend = () => {
    if (!selectedTrack) return;

    // Enviar o formato esperado pelo backend
    fetch("http://localhost:5000/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        songs: [
          {
            name: selectedTrack.name,
            year: selectedTrack.year,
            artists: selectedTrack.artists,
          },
        ],
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setRecommendations(data.recommendations || []);
      })
      .catch((err) => {
        console.error("Erro ao obter recomendações:", err);
        setRecommendations([]);
      });
  };

  return (
    <div className="container">
      <h1>Recomendador de Músicas</h1>

      <div style={{ position: "relative", marginBottom: "1rem" }}>
        <input
          className="spotify-input"
          placeholder="Digite o nome da música ou artista..."
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
        />
        {filteredVisible && filteredTracks.length > 0 && (
          <div
            style={{
              position: "absolute",
              zIndex: 10,
              backgroundColor: "#282828",
              border: "1px solid #1DB954",
              width: "100%",
              borderRadius: "0.5rem",
              marginTop: "0.25rem",
              maxHeight: "300px",
              overflowY: "auto",
            }}
          >
            {filteredTracks.map((track) => (
              <div
                key={track.id}
                onClick={() => handleSelectTrack(track)}
                className="card"
              >
                <p className="name">{track.name}</p>
                <p className="artists">{track.artists}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={handleRecommend}
        className="spotify-button"
        disabled={!selectedTrack}
      >
        Recomendar
      </button>

      {recommendations.length > 0 && (
        <>
          <h2>Recomendações</h2>
          <div className="scroll-area">
            {recommendations.map((track) => (
              <div key={track.id} className="card">
                <p className="name">{track.name}</p>
                <p className="artists">{track.artists}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

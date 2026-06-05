import { useState, useEffect } from 'react'
import api from '../api'

export default function Catalogo() {
  const [peliculas, setPeliculas] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('All')
  const [genresList, setGenresList] = useState([])

  useEffect(() => {
    api.getPeliculas()
      .then(data => {
        setPeliculas(data)
        // Extract unique genres for filter dropdown
        const allGenres = new Set()
        data.forEach(p => {
          if (p.Generos) {
            p.Generos.split(', ').forEach(g => allGenres.add(g))
          }
        })
        setGenresList(Array.from(allGenres))
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filteredMovies = peliculas.filter(p => {
    const matchesSearch = p.Titulo.toLowerCase().includes(search.toLowerCase()) || p.PaisOrigen.toLowerCase().includes(search.toLowerCase())
    const matchesGenre = selectedGenre === 'All' || (p.Generos && p.Generos.split(', ').includes(selectedGenre))
    return matchesSearch && matchesGenre
  })

  return (
    <div className="animate-fade-in">
      {/* Film Festival Hero Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(217, 70, 239, 0.1))',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: '20px',
        padding: '40px 30px',
        marginBottom: 32,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h2 style={{ fontSize: 36, fontWeight: 900, marginBottom: 8, background: 'linear-gradient(135deg, #fff, var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Selección Oficial 2026
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 16, maxWidth: 600, margin: 0 }}>
            Explora las producciones cinematográficas más destacadas e innovadoras de este año, seleccionadas cuidadosamente por nuestro jurado internacional.
          </p>
        </div>
        <div style={{
          position: 'absolute',
          right: '-50px',
          top: '-50px',
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: 'rgba(219, 70, 239, 0.15)',
          filter: 'blur(60px)'
        }}></div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-card" style={{ padding: '16px 24px', marginBottom: 32, display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: 250 }}>
          <input className="input" placeholder="Buscar por título, país de origen..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div style={{ width: 200 }}>
          <select className="select" value={selectedGenre} onChange={e => setSelectedGenre(e.target.value)}>
            <option value="All">Todos los géneros</option>
            {genresList.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: 13, fontWeight: 600 }}>
          {filteredMovies.length} Películas encontradas
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <div style={{ display: 'inline-block', width: 40, height: 40, border: '4px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-purple)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ marginTop: 12, color: 'var(--text-secondary)' }}>Cargando catálogo oficial...</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 24 }}>
          {filteredMovies.map(p => (
            <div key={p.IdPelicula} className="glass-card animate-scale-in" style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '100%',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Highlight ribbon for premiada */}
              {p.Estado === 'Premiada' && (
                <div style={{
                  position: 'absolute',
                  top: 15,
                  right: -30,
                  background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                  color: '#fff',
                  fontSize: 10,
                  fontWeight: 800,
                  padding: '4px 30px',
                  transform: 'rotate(45deg)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Ganadora
                </div>
              )}

              <div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
                  {p.Generos && p.Generos.split(', ').map(g => (
                    <span key={g} style={{
                      fontSize: 10,
                      fontWeight: 700,
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.08)',
                      padding: '3px 8px',
                      borderRadius: 4,
                      color: 'var(--text-secondary)'
                    }}>
                      {g}
                    </span>
                  ))}
                </div>

                <h3 style={{ fontSize: 20, fontWeight: 800, margin: '0 0 6px 0', lineHeight: 1.3 }}>{p.Titulo}</h3>
                
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
                  {p.AnioProd} · {p.PaisOrigen} · {p.Duracion} min
                </p>

                <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 20, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', height: 60, textOverflow: 'ellipsis' }}>
                  {p.Sinopsis || 'Sin sinopsis disponible en esta edición.'}
                </p>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid rgba(255,255,255,0.06)',
                paddingTop: 16,
                marginTop: 'auto'
              }}>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  Clasificación: <strong style={{ color: '#fff' }}>{p.Clasificacion}</strong> · Formato: <strong style={{ color: '#fff' }}>{p.Formato}</strong>
                </div>

                <span className={`badge ${
                  p.Estado === 'Premiada' ? 'badge-premiada' :
                  p.Estado === 'Seleccionada' ? 'badge-seleccionada' :
                  p.Estado === 'Rechazada' ? 'badge-rechazada' : 'badge-postulada'
                }`}>
                  {p.Estado}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Spinner rotation animation */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

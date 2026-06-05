import { useState, useEffect } from 'react'
import api from '../api'

export default function Catalogo() {
  const [peliculas, setPeliculas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getPeliculas().then(data => { setPeliculas(data); setLoading(false) })
  }, [])

  if (loading) return <p>Cargando...</p>

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Catálogo de Películas</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
        {peliculas.map(p => (
          <div key={p.IdPelicula} style={{ background: '#fff', borderRadius: 8, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ margin: '0 0 4px' }}>{p.Titulo}</h3>
            <p style={{ margin: '0 0 4px', color: '#666', fontSize: 13 }}>{p.AnioProd} · {p.PaisOrigen} · {p.Duracion}min</p>
            <p style={{ margin: '0 0 4px', fontSize: 13 }}><strong>Clasificación:</strong> {p.Clasificacion} · <strong>Formato:</strong> {p.Formato}</p>
            <p style={{ margin: '0 0 4px', fontSize: 13 }}><strong>Géneros:</strong> {p.Generos}</p>
            <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: p.Estado === 'Premiada' ? '#ffd700' : '#e0e0e0' }}>{p.Estado}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

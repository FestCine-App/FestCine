import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminPeliculas() {
  const [peliculas, setPeliculas] = useState([])
  const [generos, setGeneros] = useState([])
  const [form, setForm] = useState({ Titulo: '', AnioProd: '', Duracion: '', PaisOrigen: '', Sinopsis: '', Clasificacion: 'PG', Formato: 'Digital', Estado: 'Postulada', generos: [] })
  const [editing, setEditing] = useState(null)
  const [msg, setMsg] = useState('')

  const load = () => api.getPeliculas().then(setPeliculas)
  useEffect(() => { load(); api.getGeneros().then(setGeneros) }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editing) {
        await api.updatePelicula(editing, { ...form, AnioProd: parseInt(form.AnioProd), Duracion: parseInt(form.Duracion) })
      } else {
        await api.createPelicula({ ...form, AnioProd: parseInt(form.AnioProd), Duracion: parseInt(form.Duracion) })
      }
      setMsg('Película guardada exitosamente')
      setForm({ Titulo: '', AnioProd: '', Duracion: '', PaisOrigen: '', Sinopsis: '', Clasificacion: 'PG', Formato: 'Digital', Estado: 'Postulada', generos: [] })
      setEditing(null)
      load()
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const toggleGenero = (id) => {
    setForm(prev => ({
      ...prev,
      generos: prev.generos.includes(id) ? prev.generos.filter(g => g !== id) : [...prev.generos, id]
    }))
  }

  const edit = (p) => {
    setEditing(p.IdPelicula)
    setForm({
      Titulo: p.Titulo, AnioProd: String(p.AnioProd), Duracion: String(p.Duracion),
      PaisOrigen: p.PaisOrigen, Sinopsis: p.Sinopsis || '', Clasificacion: p.Clasificacion,
      Formato: p.Formato, Estado: p.Estado, generos: p.Generos ? p.Generos.split(', ').map(g => generos.find(ge => ge.NombreGenero === g)?.IdGenero).filter(Boolean) : []
    })
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Catálogo de Películas (Administración)</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Edite los metadatos de las producciones postuladas al festival y configure sus géneros.
          </p>
        </div>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: 24, alignItems: 'start' }}>
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editing ? 'Editar Película' : 'Registrar Nueva Película'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Título *</label>
              <input placeholder="Ej. El Gran Laberinto" className="input" value={form.Titulo} onChange={e => setForm({ ...form, Titulo: e.target.value })} required />
            </div>

            <div className="grid-2" style={{ marginBottom: 16 }}>
              <div>
                <label className="form-label">Año Producción *</label>
                <input placeholder="Ej. 2026" type="number" className="input" value={form.AnioProd} onChange={e => setForm({ ...form, AnioProd: e.target.value })} required />
              </div>
              <div>
                <label className="form-label">Duración (min) *</label>
                <input placeholder="Ej. 120" type="number" className="input" value={form.Duracion} onChange={e => setForm({ ...form, Duracion: e.target.value })} required />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">País de Origen *</label>
              <input placeholder="Ej. Bolivia" className="input" value={form.PaisOrigen} onChange={e => setForm({ ...form, PaisOrigen: e.target.value })} required />
            </div>

            <div className="grid-3" style={{ marginBottom: 16 }}>
              <div>
                <label className="form-label">Clasif. *</label>
                <select className="select" value={form.Clasificacion} onChange={e => setForm({ ...form, Clasificacion: e.target.value })}>
                  {['G','PG','PG-13','R','NC-17','ATP'].map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="form-label">Formato *</label>
                <select className="select" value={form.Formato} onChange={e => setForm({ ...form, Formato: e.target.value })}>
                  {['Digital','35mm','IMAX'].map(f => <option key={f}>{f}</option>)}
                </select>
              </div>
              <div>
                <label className="form-label">Estado *</label>
                <select className="select" value={form.Estado} onChange={e => setForm({ ...form, Estado: e.target.value })}>
                  {['Postulada','Seleccionada','Rechazada','Premiada'].map(e => <option key={e}>{e}</option>)}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Sinopsis</label>
              <textarea placeholder="Resumen argumental de la película..." rows={3} className="textarea" value={form.Sinopsis} onChange={e => setForm({ ...form, Sinopsis: e.target.value })} />
            </div>

            <div className="form-group">
              <label className="form-label">Géneros Cinemáticos</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, background: 'rgba(0,0,0,0.2)', padding: 12, borderRadius: 8, border: '1px solid rgba(255,255,255,0.04)' }}>
                {generos.map(g => (
                  <label key={g.IdGenero} style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', color: 'var(--text-secondary)' }}>
                    <input type="checkbox" checked={form.generos.includes(g.IdGenero)} onChange={() => toggleGenero(g.IdGenero)} style={{ accentColor: 'var(--accent-purple)' }} />
                    {g.NombreGenero}
                  </label>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editing ? 'Actualizar' : 'Crear Película'}</button>
              {editing && (
                <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ Titulo: '', AnioProd: '', Duracion: '', PaisOrigen: '', Sinopsis: '', Clasificacion: 'PG', Formato: 'Digital', Estado: 'Postulada', generos: [] }) }}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Título</th>
                <th>Origen</th>
                <th>Detalles</th>
                <th>Estado</th>
                <th style={{ textAlign: 'right' }}>Acción</th>
              </tr>
            </thead>
            <tbody>
              {peliculas.map(p => (
                <tr key={p.IdPelicula}>
                  <td style={{ fontWeight: 600 }}>{p.Titulo}</td>
                  <td>{p.PaisOrigen} ({p.AnioProd})</td>
                  <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                    <div>{p.Duracion} min | {p.Clasificacion}</div>
                    <div>{p.Formato}</div>
                  </td>
                  <td>
                    <span className={`badge ${
                      p.Estado === 'Premiada' ? 'badge-premiada' :
                      p.Estado === 'Seleccionada' ? 'badge-seleccionada' :
                      p.Estado === 'Rechazada' ? 'badge-rechazada' : 'badge-postulada'
                    }`}>
                      {p.Estado}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button onClick={() => edit(p)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


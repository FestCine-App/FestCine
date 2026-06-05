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
      setMsg('Guardado exitosamente')
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
    <div>
      <h2 style={{ marginTop: 0 }}>{editing ? 'Editar' : 'Registrar'} Película</h2>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <input placeholder="Título" style={inp} value={form.Titulo} onChange={e => setForm({ ...form, Titulo: e.target.value })} required />
          <input placeholder="Año" type="number" style={inp} value={form.AnioProd} onChange={e => setForm({ ...form, AnioProd: e.target.value })} required />
          <input placeholder="Duración (min)" type="number" style={inp} value={form.Duracion} onChange={e => setForm({ ...form, Duracion: e.target.value })} required />
          <input placeholder="País de Origen" style={inp} value={form.PaisOrigen} onChange={e => setForm({ ...form, PaisOrigen: e.target.value })} required />
          <select style={inp} value={form.Clasificacion} onChange={e => setForm({ ...form, Clasificacion: e.target.value })}>
            {['G','PG','PG-13','R','NC-17','ATP'].map(c => <option key={c}>{c}</option>)}
          </select>
          <select style={inp} value={form.Formato} onChange={e => setForm({ ...form, Formato: e.target.value })}>
            {['Digital','35mm','IMAX'].map(f => <option key={f}>{f}</option>)}
          </select>
          <select style={inp} value={form.Estado} onChange={e => setForm({ ...form, Estado: e.target.value })}>
            {['Postulada','Seleccionada','Rechazada','Premiada'].map(e => <option key={e}>{e}</option>)}
          </select>
        </div>
        <textarea placeholder="Sinopsis" rows={3} style={{ ...inp, marginTop: 12, width: '100%', resize: 'vertical' }} value={form.Sinopsis} onChange={e => setForm({ ...form, Sinopsis: e.target.value })} />
        <div style={{ marginTop: 12 }}>
          <label style={{ fontSize: 13, fontWeight: 600, display: 'block', marginBottom: 4 }}>Géneros</label>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {generos.map(g => (
              <label key={g.IdGenero} style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
                <input type="checkbox" checked={form.generos.includes(g.IdGenero)} onChange={() => toggleGenero(g.IdGenero)} />
                {g.NombreGenero}
              </label>
            ))}
          </div>
        </div>
        <button type="submit" style={{ ...btn, marginTop: 16 }}>{editing ? 'Actualizar' : 'Crear'} Película</button>
        {editing && <button type="button" style={{ ...btn, marginTop: 16, marginLeft: 8, background: '#666' }} onClick={() => { setEditing(null); setForm({ Titulo: '', AnioProd: '', Duracion: '', PaisOrigen: '', Sinopsis: '', Clasificacion: 'PG', Formato: 'Digital', Estado: 'Postulada', generos: [] }) }}>Cancelar</button>}
        {msg && <p style={{ fontSize: 13, marginTop: 8 }}>{msg}</p>}
      </form>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead style={{ background: '#1a1a2e', color: '#fff' }}>
          <tr><th style={th}>Título</th><th style={th}>Año</th><th style={th}>Duración</th><th style={th}>Estado</th><th style={th}>Acción</th></tr>
        </thead>
        <tbody>
          {peliculas.map(p => (
            <tr key={p.IdPelicula} style={{ borderBottom: '1px solid #eee' }}>
              <td style={td}>{p.Titulo}</td><td style={td}>{p.AnioProd}</td><td style={td}>{p.Duracion}min</td><td style={td}>{p.Estado}</td>
              <td style={td}><button onClick={() => edit(p)} style={{ padding: '4px 12px', fontSize: 12, cursor: 'pointer' }}>Editar</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const inp = { padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btn = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
const th = { padding: '8px 12px', textAlign: 'left', fontSize: 13 }
const td = { padding: '8px 12px', fontSize: 13 }

import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminJurados() {
  const [jurados, setJurados] = useState([])
  const [categorias, setCategorias] = useState([])
  const [peliculas, setPeliculas] = useState([])
  const [evaluaciones, setEvaluaciones] = useState([])
  const [premios, setPremios] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [tab, setTab] = useState('jurados')
  const [formJ, setFormJ] = useState({ Nombre: '', Profesion: '', Pais: '', Email: '' })
  const [formEval, setFormEval] = useState({ IdMiembro: '', IdPelicula: '', IdCategoria: '', IdEdicion: '', Puntuacion: '5', Comentario: '' })
  const [formPremio, setFormPremio] = useState({ IdCategoria: '', IdPelicula: '', IdEdicion: '' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all([
      api.getJurados(), api.getCategorias(), api.getPeliculas(),
      api.getEvaluaciones(), api.getPremios(), api.getEdiciones()
    ]).then(([j, c, p, ev, pr, ed]) => { setJurados(j); setCategorias(c); setPeliculas(p); setEvaluaciones(ev); setPremios(pr); setEdiciones(ed) })
  }, [])

  const crearJurado = async (e) => {
    e.preventDefault()
    try { const r = await api.createJurado?.(formJ) || await (await fetch('/api/jurados', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formJ) })).json(); setMsg('Jurado creado'); setFormJ({ Nombre: '', Profesion: '', Pais: '', Email: '' }); api.getJurados().then(setJurados) }
    catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearEvaluacion = async (e) => {
    e.preventDefault()
    try {
      const res = await api.createEvaluacion({ ...formEval, IdMiembro: parseInt(formEval.IdMiembro), IdPelicula: parseInt(formEval.IdPelicula), IdCategoria: parseInt(formEval.IdCategoria), IdEdicion: parseInt(formEval.IdEdicion), Puntuacion: parseInt(formEval.Puntuacion) })
      setMsg('Evaluación registrada'); setFormEval({ IdMiembro: '', IdPelicula: '', IdCategoria: '', Puntuacion: '5', Comentario: '' })
      api.getEvaluaciones().then(setEvaluaciones)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearPremio = async (e) => {
    e.preventDefault()
    try {
      const res = await api.createPremio({ ...formPremio, IdCategoria: parseInt(formPremio.IdCategoria), IdPelicula: parseInt(formPremio.IdPelicula), IdEdicion: parseInt(formPremio.IdEdicion) })
      setMsg('Premio registrado'); setFormPremio({ IdCategoria: '', IdPelicula: '', IdEdicion: '' })
      api.getPremios().then(setPremios)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const tabs = [
    { key: 'jurados', label: 'Jurados' },
    { key: 'evaluaciones', label: 'Evaluaciones' },
    { key: 'premios', label: 'Premios' },
  ]

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Jurados, Evaluaciones y Premios</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            style={{ padding: '8px 16px', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 13, background: tab === t.key ? '#1a1a2e' : '#e0e0e0', color: tab === t.key ? '#fff' : '#333' }}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'jurados' && (
        <div>
          <form onSubmit={crearJurado} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <input placeholder="Nombre" style={inp} value={formJ.Nombre} onChange={e => setFormJ({ ...formJ, Nombre: e.target.value })} required />
              <input placeholder="Profesión" style={inp} value={formJ.Profesion} onChange={e => setFormJ({ ...formJ, Profesion: e.target.value })} />
              <input placeholder="País" style={inp} value={formJ.Pais} onChange={e => setFormJ({ ...formJ, Pais: e.target.value })} />
              <input placeholder="Email" type="email" style={inp} value={formJ.Email} onChange={e => setFormJ({ ...formJ, Email: e.target.value })} />
            </div>
            <button type="submit" style={{ ...btn, marginTop: 12 }}>Registrar Jurado</button>
          </form>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <thead style={{ background: '#1a1a2e', color: '#fff' }}>
              <tr><th style={th}>Nombre</th><th style={th}>Profesión</th><th style={th}>País</th></tr>
            </thead>
            <tbody>
              {jurados.map(j => (
                <tr key={j.IdMiembro} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={td}>{j.Nombre}</td><td style={td}>{j.Profesion}</td><td style={td}>{j.Pais}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'evaluaciones' && (
        <div>
          <form onSubmit={crearEvaluacion} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formEval.IdMiembro} onChange={e => setFormEval({ ...formEval, IdMiembro: e.target.value })} required>
                <option value="">Jurado</option>
                {jurados.map(j => <option key={j.IdMiembro} value={j.IdMiembro}>{j.Nombre}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formEval.IdPelicula} onChange={e => setFormEval({ ...formEval, IdPelicula: e.target.value })} required>
                <option value="">Película</option>
                {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formEval.IdCategoria} onChange={e => setFormEval({ ...formEval, IdCategoria: e.target.value })} required>
                <option value="">Categoría</option>
                {categorias.map(c => <option key={c.IdCategoria} value={c.IdCategoria}>{c.NombreCategoria}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formEval.IdEdicion} onChange={e => setFormEval({ ...formEval, IdEdicion: e.target.value })} required>
                <option value="">Edición</option>
                {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <input type="number" min="1" max="10" placeholder="Puntuación (1-10)" style={inp} value={formEval.Puntuacion} onChange={e => setFormEval({ ...formEval, Puntuacion: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 12 }}>
              <textarea placeholder="Comentario (opcional)" rows={2} style={{ ...inp, resize: 'vertical' }} value={formEval.Comentario} onChange={e => setFormEval({ ...formEval, Comentario: e.target.value })} />
            </div>
            <button type="submit" style={btn}>Registrar Evaluación</button>
          </form>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <thead style={{ background: '#1a1a2e', color: '#fff' }}>
              <tr><th style={th}>Jurado</th><th style={th}>Película</th><th style={th}>Categoría</th><th style={th}>Edición</th><th style={th}>Punt.</th></tr>
            </thead>
            <tbody>
              {evaluaciones.map(e => (
                <tr key={e.IdEvaluacion} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={td}>{e.Jurado}</td><td style={td}>{e.Pelicula}</td><td style={td}>{e.Categoria}</td><td style={td}>{e.NombreEdicion}</td><td style={td}>{e.Puntuacion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'premios' && (
        <div>
          <form onSubmit={crearPremio} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPremio.IdCategoria} onChange={e => setFormPremio({ ...formPremio, IdCategoria: e.target.value })} required>
                <option value="">Categoría</option>
                {categorias.map(c => <option key={c.IdCategoria} value={c.IdCategoria}>{c.NombreCategoria}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPremio.IdPelicula} onChange={e => setFormPremio({ ...formPremio, IdPelicula: e.target.value })} required>
                <option value="">Película Ganadora</option>
                {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPremio.IdEdicion} onChange={e => setFormPremio({ ...formPremio, IdEdicion: e.target.value })} required>
                <option value="">Edición</option>
                {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
              </select>
            </div>
            <button type="submit" style={btn}>Registrar Premio</button>
          </form>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <thead style={{ background: '#1a1a2e', color: '#fff' }}>
              <tr><th style={th}>Categoría</th><th style={th}>Película</th><th style={th}>Edición</th></tr>
            </thead>
            <tbody>
              {premios.map(p => (
                <tr key={p.IdPremio} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={td}>{p.NombreCategoria}</td><td style={td}>{p.Pelicula}</td><td style={td}>{p.NombreEdicion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {msg && <p style={{ fontSize: 13, marginTop: 8 }}>{msg}</p>}
    </div>
  )
}

const inp = { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btn = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
const th = { padding: '8px 12px', textAlign: 'left', fontSize: 13 }
const td = { padding: '8px 12px', fontSize: 13 }

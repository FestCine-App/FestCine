import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminPatrocinadores() {
  const [patrocinadores, setPatrocinadores] = useState([])
  const [patrocinios, setPatrocinios] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [tab, setTab] = useState('patrocinadores')
  const [formP, setFormP] = useState({ NombreEmpresa: '', Contacto: '', Email: '', RedesSociales: '' })
  const [formPE, setFormPE] = useState({ IdPatrocinador: '', IdEdicion: '', TipoAporte: 'Economico', Monto: '', DescripcionAporte: '' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all([api.getPatrocinadores(), api.getPatrocinios(), api.getEdiciones()])
      .then(([p, pe, e]) => { setPatrocinadores(p); setPatrocinios(pe); setEdiciones(e) })
  }, [])

  const crearPatrocinador = async (e) => {
    e.preventDefault()
    try { await api.createPatrocinador(formP); setMsg('Patrocinador creado'); setFormP({ NombreEmpresa: '', Contacto: '', Email: '', RedesSociales: '' }); api.getPatrocinadores().then(setPatrocinadores) }
    catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearPatrocinio = async (e) => {
    e.preventDefault()
    try {
      await api.createPatrocinio({ ...formPE, IdPatrocinador: parseInt(formPE.IdPatrocinador), IdEdicion: parseInt(formPE.IdEdicion), Monto: formPE.Monto ? parseFloat(formPE.Monto) : null })
      setMsg('Patrocinio registrado'); setFormPE({ IdPatrocinador: '', IdEdicion: '', TipoAporte: 'Economico', Monto: '', DescripcionAporte: '' })
      api.getPatrocinios().then(setPatrocinios)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Patrocinadores</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button onClick={() => setTab('patrocinadores')} style={{ padding: '8px 16px', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 13, background: tab === 'patrocinadores' ? '#1a1a2e' : '#e0e0e0', color: tab === 'patrocinadores' ? '#fff' : '#333' }}>Patrocinadores</button>
        <button onClick={() => setTab('patrocinios')} style={{ padding: '8px 16px', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 13, background: tab === 'patrocinios' ? '#1a1a2e' : '#e0e0e0', color: tab === 'patrocinios' ? '#fff' : '#333' }}>Patrocinios por Edición</button>
      </div>

      {tab === 'patrocinadores' && (
        <div>
          <form onSubmit={crearPatrocinador} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <input placeholder="Empresa" style={inp} value={formP.NombreEmpresa} onChange={e => setFormP({ ...formP, NombreEmpresa: e.target.value })} required />
              <input placeholder="Contacto" style={inp} value={formP.Contacto} onChange={e => setFormP({ ...formP, Contacto: e.target.value })} />
              <input placeholder="Email" type="email" style={inp} value={formP.Email} onChange={e => setFormP({ ...formP, Email: e.target.value })} />
              <input placeholder="Redes Sociales" style={inp} value={formP.RedesSociales} onChange={e => setFormP({ ...formP, RedesSociales: e.target.value })} />
            </div>
            <button type="submit" style={{ ...btn, marginTop: 12 }}>Registrar Patrocinador</button>
          </form>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <thead style={{ background: '#1a1a2e', color: '#fff' }}>
              <tr><th style={th}>Empresa</th><th style={th}>Contacto</th><th style={th}>Email</th></tr>
            </thead>
            <tbody>
              {patrocinadores.map(p => (
                <tr key={p.IdPatrocinador} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={td}>{p.NombreEmpresa}</td><td style={td}>{p.Contacto}</td><td style={td}>{p.Email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'patrocinios' && (
        <div>
          <form onSubmit={crearPatrocinio} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPE.IdPatrocinador} onChange={e => setFormPE({ ...formPE, IdPatrocinador: e.target.value })} required>
                <option value="">Patrocinador</option>
                {patrocinadores.map(p => <option key={p.IdPatrocinador} value={p.IdPatrocinador}>{p.NombreEmpresa}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPE.IdEdicion} onChange={e => setFormPE({ ...formPE, IdEdicion: e.target.value })} required>
                <option value="">Edición</option>
                {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formPE.TipoAporte} onChange={e => setFormPE({ ...formPE, TipoAporte: e.target.value })}>
                <option value="Economico">Económico</option>
                <option value="Especie">Especie</option>
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Monto (si es económico)" type="number" step="0.01" style={inp} value={formPE.Monto} onChange={e => setFormPE({ ...formPE, Monto: e.target.value })} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <textarea placeholder="Descripción del aporte" rows={2} style={{ ...inp, resize: 'vertical' }} value={formPE.DescripcionAporte} onChange={e => setFormPE({ ...formPE, DescripcionAporte: e.target.value })} />
            </div>
            <button type="submit" style={btn}>Registrar Patrocinio</button>
          </form>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <thead style={{ background: '#1a1a2e', color: '#fff' }}>
              <tr><th style={th}>Empresa</th><th style={th}>Edición</th><th style={th}>Tipo</th><th style={th}>Monto</th></tr>
            </thead>
            <tbody>
              {patrocinios.map(p => (
                <tr key={p.IdPatrocinio} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={td}>{p.NombreEmpresa}</td><td style={td}>{p.NombreEdicion}</td>
                  <td style={td}>{p.TipoAporte}</td><td style={td}>{p.Monto ? `Bs. ${p.Monto}` : '-'}</td>
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

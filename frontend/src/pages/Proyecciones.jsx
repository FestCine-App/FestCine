import { useState, useEffect } from 'react'
import api from '../api'

export default function Proyecciones() {
  const [proyecciones, setProyecciones] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getProyecciones().then(data => { setProyecciones(data); setLoading(false) })
  }, [])

  if (loading) return <p>Cargando...</p>

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Proyecciones Disponibles</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead style={{ background: '#1a1a2e', color: '#fff' }}>
          <tr>
            <th style={thStyle}>Película</th>
            <th style={thStyle}>Sala</th>
            <th style={thStyle}>Sede</th>
            <th style={thStyle}>Fecha/Hora</th>
            <th style={thStyle}>Aforo</th>
            <th style={thStyle}>Q&A</th>
          </tr>
        </thead>
        <tbody>
          {proyecciones.map(p => (
            <tr key={p.IdProyeccion} style={{ borderBottom: '1px solid #eee' }}>
              <td style={tdStyle}>{p.Titulo}</td>
              <td style={tdStyle}>{p.NombreSala}</td>
              <td style={tdStyle}>{p.NombreSede}</td>
              <td style={tdStyle}>{new Date(p.FechaHora).toLocaleString('es-BO')}</td>
              <td style={tdStyle}>{p.AforoDisponible}/{p.Capacidad}</td>
              <td style={tdStyle}>{p.TieneQA ? 'Sí' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const thStyle = { padding: '10px 12px', textAlign: 'left', fontSize: 13, fontWeight: 600 }
const tdStyle = { padding: '10px 12px', fontSize: 13 }

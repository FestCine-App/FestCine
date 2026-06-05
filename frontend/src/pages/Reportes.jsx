import { useState, useEffect } from 'react'
import api from '../api'

export default function Reportes() {
  const [tab, setTab] = useState('ranking')
  const [ediciones, setEdiciones] = useState([])
  const [idEdicion, setIdEdicion] = useState('')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getEdiciones().then(e => {
      setEdiciones(e)
      if (e.length > 0) setIdEdicion(e[0].IdEdicion.toString())
    })
  }, [])

  useEffect(() => {
    setLoading(true)
    const ed = idEdicion ? parseInt(idEdicion) : null
    const fetchers = {
      ranking: () => api.getRanking(ed),
      premiacion: () => api.getPremiacion(ed),
      financiero: () => api.getFinanciero(ed),
      ocupacion: () => api.getOcupacionSalas(),
    }
    fetchers[tab]().then(d => { setData(d); setLoading(false) })
  }, [tab, idEdicion])

  const tabs = [
    { key: 'ranking', label: 'Ranking Películas' },
    { key: 'premiacion', label: 'Acta Premiación' },
    { key: 'financiero', label: 'Informe Financiero' },
    { key: 'ocupacion', label: 'Ocupación Salas' },
  ]

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Reportes</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            style={{ padding: '8px 16px', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 13, background: tab === t.key ? '#1a1a2e' : '#e0e0e0', color: tab === t.key ? '#fff' : '#333' }}>
            {t.label}
          </button>
        ))}
        {tab !== 'ocupacion' && (
          <select value={idEdicion} onChange={e => setIdEdicion(e.target.value)} style={{ marginLeft: 'auto', padding: '6px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 13 }}>
            <option value="">Todas las ediciones</option>
            {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
          </select>
        )}
      </div>
      {loading ? <p>Cargando...</p> : (
        <div style={{ background: '#fff', borderRadius: 8, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          {tab === 'ranking' && <RankingTable data={data} />}
          {tab === 'premiacion' && <PremiacionTable data={data} />}
          {tab === 'financiero' && <FinancieroTable data={data} />}
          {tab === 'ocupacion' && <OcupacionTable data={data} />}
        </div>
      )}
    </div>
  )
}

function RankingTable({ data }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead><tr style={{ borderBottom: '2px solid #1a1a2e' }}>
        <th style={th}>Película</th><th style={th}>Asistentes</th><th style={th}>Capacidad Total</th><th style={th}>Ocupación</th>
      </tr></thead>
      <tbody>
        {data.map((r, i) => (
          <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
            <td style={td}>{r.Titulo}</td><td style={td}>{r.Asistentes}</td><td style={td}>{r.CapacidadTotal}</td>
            <td style={td}>{r.PctOcupacion}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function PremiacionTable({ data }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead><tr style={{ borderBottom: '2px solid #1a1a2e' }}>
        <th style={th}>Categoría</th><th style={th}>Película Ganadora</th><th style={th}>Promedio Jurado</th><th style={th}>Año</th>
      </tr></thead>
      <tbody>
        {data.map((r, i) => (
          <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
            <td style={td}>{r.NombreCategoria}</td><td style={td}>{r.PeliculaGanadora}</td>
            <td style={td}>{r.PromedioJurado}</td><td style={td}>{r.Anio}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function FinancieroTable({ data }) {
  const total = data.reduce((s, r) => s + parseFloat(r.Subtotal || 0), 0)
  return (
    <div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead><tr style={{ borderBottom: '2px solid #1a1a2e' }}>
          <th style={th}>Tarifa</th><th style={th}>Cantidad</th><th style={th}>Total</th>
        </tr></thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
              <td style={td}>{r.NombreTarifa}</td>
              <td style={td}>{r.Cantidad}</td><td style={td}>Bs. {parseFloat(r.Subtotal).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{ textAlign: 'right', fontWeight: 700, marginTop: 12 }}>TOTAL GENERAL: Bs. {total.toFixed(2)}</p>
    </div>
  )
}

function OcupacionTable({ data }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead><tr style={{ borderBottom: '2px solid #1a1a2e' }}>
        <th style={th}>Sala</th><th style={th}>Sede</th><th style={th}>Capacidad</th><th style={th}>Entradas</th><th style={th}>Ocupación</th>
      </tr></thead>
      <tbody>
        {data.map((r, i) => (
          <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
            <td style={td}>{r.NombreSala}</td><td style={td}>{r.NombreSede}</td>
            <td style={td}>{r.Capacidad}</td><td style={td}>{r.EntradasVendidas}</td>
            <td style={td}>{r.PorcentajeOcupacion}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

const th = { padding: '8px 12px', textAlign: 'left', fontSize: 13 }
const td = { padding: '8px 12px', fontSize: 13 }

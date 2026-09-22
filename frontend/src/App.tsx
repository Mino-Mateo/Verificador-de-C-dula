import { useEffect, useState, type FormEvent } from 'react'
import { listarPaises, validar } from './api'
import type { ValidateResponse } from './api'
import './App.css'

const NOMBRES: Record<string, string> = {
  EC: 'Ecuador',
  CL: 'Chile',
  MX: 'México',
}

function App() {
  const [paises, setPaises] = useState<string[]>([])
  const [pais, setPais] = useState('')
  const [valorInput, setValorInput] = useState('')
  const [resultado, setResultado] = useState<ValidateResponse | null>(null)

  useEffect(() => {
    listarPaises().then((lista) => {
      setPaises(lista)
      if (lista.length > 0) setPais(lista[0])
    })
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const r = await validar(pais, valorInput)
    setResultado(r)
  }

  return (
    <div className="container">
      <h1>Verificador de Cédula</h1>
      <form onSubmit={handleSubmit}>
        <select value={pais} onChange={(e) => setPais(e.target.value)}>
          {paises.map((p) => (
            <option key={p} value={p}>
              {NOMBRES[p] ?? p}
            </option>
          ))}
        </select>
        <input
          type="text"
          value={valorInput}
          onChange={(e) => setValorInput(e.target.value)}
          placeholder="Ingresá el número"
        />
        <button type="submit">Verificar</button>
      </form>
      {resultado && (
        <p className={resultado.valido ? 'ok' : 'fail'}>
          {resultado.mensaje ?? resultado.error}
        </p>
      )}
    </div>
  )
}

export default App

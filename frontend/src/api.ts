export interface ValidateResponse {
  valido?: boolean
  mensaje?: string
  error?: string
}

export async function listarPaises(): Promise<string[]> {
  const res = await fetch('/api/paises')
  return res.json()
}

export async function validar(pais: string, valor: string): Promise<ValidateResponse> {
  const res = await fetch('/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pais, valor }),
  })
  return res.json()
}

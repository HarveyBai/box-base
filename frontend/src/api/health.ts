export interface HealthResponse {
  status: 'ok'
  version: string
  service: 'boxbase'
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch('/api/health')

  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`)
  }

  return (await res.json()) as HealthResponse
}

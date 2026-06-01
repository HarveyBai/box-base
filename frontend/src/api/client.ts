/**
 * fetch wrapper — 自动注入 access token + 401 静默 refresh rotation。
 *
 * - 请求拦截：自动附带 Authorization: Bearer <access>
 * - 响应拦截：遇 401 用 localStorage 的 refresh 调 /api/auth/refresh 换发新 access，重放原请求
 * - refresh rotation：换发后必须用新 refresh 覆盖 localStorage 旧值
 * - refresh 也失败时清空状态，抛出错误由上层跳 /login
 */

let accessToken: string | null = null
let onAuthExpired: (() => void) | null = null

/** 由 AuthContext 设置 access token（内存，不落盘） */
export function setAccessToken(token: string | null): void {
  accessToken = token
}

/** 由 AuthContext 读取当前 access token */
export function getAccessToken(): string | null {
  return accessToken
}

/** 由 AuthContext 设置 refresh token */
export function setRefreshToken(token: string | null): void {
  if (token) {
    localStorage.setItem('refresh_token', token)
  } else {
    localStorage.removeItem('refresh_token')
  }
}

/** 从 localStorage 恢复 refresh token */
export function getStoredRefreshToken(): string | null {
  return localStorage.getItem('refresh_token')
}

/** 注册认证过期回调（清空状态 + 跳 /login） */
export function setOnAuthExpired(cb: (() => void) | null): void {
  onAuthExpired = cb
}

interface ErrorDetail {
  detail: { code: string; message: string }
}

/** 后端错误格式 { detail: { code, message } } */
export class ApiError extends Error {
  code: string
  status: number

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

/** refresh 换发结果的完整 token 对，供 init / 401 拦截器复用 */
export interface TokenRefreshResult {
  access_token: string
  refresh_token: string
  active_tenant_id: string
}

/**
 * 执行一次 /api/auth/refresh 调用并更新模块级 token。
 * 成功后自动更新 accessToken（内存）+ refresh_token（localStorage）。
 *
 * @returns 完整 TokenRefreshResult，失败返回 null
 */
async function doRefresh(): Promise<TokenRefreshResult | null> {
  const stored = getStoredRefreshToken()
  if (!stored) return null

  try {
    const res = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: stored }),
    })

    if (!res.ok) {
      // refresh 失败 — 清空所有 token
      accessToken = null
      localStorage.removeItem('refresh_token')
      if (onAuthExpired) onAuthExpired()
      return null
    }

    const data = (await res.json()) as TokenRefreshResult

    accessToken = data.access_token
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  } catch {
    accessToken = null
    localStorage.removeItem('refresh_token')
    if (onAuthExpired) onAuthExpired()
    return null
  }
}

/** 正在换发中的 Promise，防止同一标签页内并发 refresh */
let refreshPromise: Promise<TokenRefreshResult | null> | null = null

/**
 * 单飞锁包裹的 refresh 入口。同一标签页内任意时刻只有一个 refresh 在途，
 * 重复调用返回同一个 Promise。AuthContext init 和 401 拦截器都走这个入口。
 */
export function refreshAccessToken(): Promise<TokenRefreshResult | null> {
  if (!refreshPromise) {
    refreshPromise = doRefresh().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

type RequestOptions = Omit<RequestInit, 'body' | 'headers'> & {
  body?: unknown
  headers?: Record<string, string>
  /** 跳过 401 自动 refresh（用于 login/register 等无需刷新场景） */
  skipAuth?: boolean
}

/**
 * 带认证的 fetch 封装。
 *
 * 自动注入 Authorization header；遇 401 自动 refresh 后重试一次。
 */
export async function authFetch<T = unknown>(
  url: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, headers: customHeaders, skipAuth = false, ...rest } = options

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...customHeaders,
  }

  // 请求拦截器：自动注入 access token
  if (!skipAuth && accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  const fetchOptions: RequestInit = {
    ...rest,
    headers,
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  }

  let res = await fetch(url, fetchOptions)

  // 响应拦截器：遇 401 自动 refresh 后重试一次
  if (!skipAuth && res.status === 401 && accessToken) {
    const result = await refreshAccessToken()
    if (result) {
      headers['Authorization'] = `Bearer ${result.access_token}`
      res = await fetch(url, { ...fetchOptions, headers })
    }
  }

  if (!res.ok) {
    let errDetail: ErrorDetail | null = null
    try {
      errDetail = (await res.json()) as ErrorDetail
    } catch {
      // body 不是 JSON，使用默认 message
    }

    const code = errDetail?.detail?.code ?? 'UNKNOWN_ERROR'
    const message = errDetail?.detail?.message ?? `Request failed with status ${res.status}`
    throw new ApiError(res.status, code, message)
  }

  // 204 No Content 无 body
  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

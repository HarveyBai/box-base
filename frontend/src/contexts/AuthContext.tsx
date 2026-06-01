import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import {
  authFetch,
  refreshAccessToken,
  setAccessToken,
  setRefreshToken,
  getStoredRefreshToken,
  setOnAuthExpired,
} from '@/api/client'

/** 后端 /api/auth/login 返回体 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  active_tenant_id: string
}

/** 后端 /api/users/me 返回体 */
export interface UserMe {
  id: string
  username: string
  email: string
  phone: string | null
  is_active: boolean
  active_tenant_id: string | null
  is_superadmin: boolean
  created_at: string
}

/** 注册入参 */
export interface RegisterPayload {
  username: string
  email: string
  phone?: string
  password: string
}

/** 登录入参 */
export interface LoginPayload {
  username: string
  password: string
}

interface AuthState {
  /** 当前是否已认证 */
  isAuthenticated: boolean
  /** 正在初始化（静默换发中） */
  isInitializing: boolean
  /** 当前用户信息 */
  user: UserMe | null
  /** 当前活跃租户 ID */
  activeTenantId: string | null
  /** 登录：调 POST /api/auth/login，成功后自动拉取 /api/users/me */
  login: (payload: LoginPayload) => Promise<void>
  /** 注册：调 POST /api/auth/register（201 则成功，不自动登录） */
  register: (payload: RegisterPayload) => Promise<void>
  /** 登出：调 POST /api/auth/logout，清空所有状态 */
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

/**
 * 获取认证上下文。必须在 <AuthProvider> 内部使用，否则抛错。
 */
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within <AuthProvider>')
  }
  return ctx
}

/**
 * AuthProvider — 认证状态管理。
 *
 * - access token 存内存（不落盘），刷新页面后清空属正常
 * - refresh token 存 localStorage（对应后端 7 天有效期）
 * - 应用启动时：若内存无 access 但 localStorage 有 refresh，自动静默换发
 * - 所有 API 调用通过 authFetch 自动处理 401 自动 refresh
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [isInitializing, setIsInitializing] = useState(true)
  const [user, setUser] = useState<UserMe | null>(null)
  const [activeTenantId, setActiveTenantId] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // 清空所有认证状态
  const clearAuth = useCallback(() => {
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
    setActiveTenantId(null)
    setIsAuthenticated(false)
    navigate('/login', { replace: true })
  }, [navigate])

  // 注册认证过期回调
  useEffect(() => {
    setOnAuthExpired(() => {
      clearAuth()
    })
    return () => setOnAuthExpired(null)
  }, [clearAuth])

  // 应用启动时：静默换发恢复登录态
  // useRef 标记避免 StrictMode 双挂载重复执行 setup 逻辑；
  // refreshAccessToken 内置单飞锁，保证同一标签页内只有一个 refresh 在途。
  /* eslint-disable react-hooks/set-state-in-effect */
  const initRan = useRef(false)
  useEffect(() => {
    initRan.current = true

    const storedRefresh = getStoredRefreshToken()
    if (!storedRefresh) {
      setIsInitializing(false)
      return
    }

    // 恢复 refresh token 到模块级
    setRefreshToken(storedRefresh)

    // 通过单飞锁换发（与 401 拦截器共享同一把锁）
    refreshAccessToken()
      .then(async (data) => {
        if (!data) {
          clearAuth()
          return
        }
        setAccessToken(data.access_token)
        setRefreshToken(data.refresh_token)
        setActiveTenantId(data.active_tenant_id)

        // 获取当前用户信息
        try {
          const userData = await authFetch<UserMe>('/api/users/me')
          setUser(userData)
          setIsAuthenticated(true)
        } catch {
          clearAuth()
        }
      })
      .catch(() => {
        clearAuth()
      })
      .finally(() => {
        setIsInitializing(false)
      })
  }, [clearAuth])
  /* eslint-enable react-hooks/set-state-in-effect */

  const login = useCallback(async (payload: LoginPayload) => {
    // skipAuth=true：login 本身不需要 access token
    const tokenData = await authFetch<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: payload,
      skipAuth: true,
    })

    setAccessToken(tokenData.access_token)
    setRefreshToken(tokenData.refresh_token)
    setActiveTenantId(tokenData.active_tenant_id)

    // 获取当前用户信息
    const userData = await authFetch<UserMe>('/api/users/me')
    setUser(userData)
    setIsAuthenticated(true)
  }, [])

  const register = useCallback(async (payload: RegisterPayload) => {
    // skipAuth=true：注册是公开接口
    await authFetch('/api/auth/register', {
      method: 'POST',
      body: payload,
      skipAuth: true,
    })
    // 注册成功不自动登录，由页面跳转 /login
  }, [])

  const logout = useCallback(async () => {
    const storedRefresh = getStoredRefreshToken()
    try {
      await authFetch('/api/auth/logout', {
        method: 'POST',
        body: { refresh_token: storedRefresh ?? '' },
      })
    } catch {
      // logout 失败也清空本地状态（服务端可能已吊销）
    }
    clearAuth()
  }, [clearAuth])

  const value = useMemo<AuthState>(
    () => ({
      isAuthenticated,
      isInitializing,
      user,
      activeTenantId,
      login,
      register,
      logout,
    }),
    [isAuthenticated, isInitializing, user, activeTenantId, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// ApiError 从 @/api/client 直接导入，避免 react-refresh 警告

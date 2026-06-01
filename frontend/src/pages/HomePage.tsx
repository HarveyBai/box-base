import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

/**
 * 根路径 "/"：根据认证状态重定向。
 * 已登录 → /dashboard，未登录 → /login。
 */
function HomePage() {
  const { isAuthenticated, isInitializing } = useAuth()

  if (isInitializing) return null

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Navigate to="/login" replace />
}

export default HomePage

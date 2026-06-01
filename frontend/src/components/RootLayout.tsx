import { AuthProvider } from '@/contexts/AuthContext'
import App from '@/App'

/**
 * 根布局：将 AuthProvider 注入到路由树内部，
 * 确保 AuthProvider 内部可用 useNavigate() 等路由 hook。
 */
export default function RootLayout() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  )
}

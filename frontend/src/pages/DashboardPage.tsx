import { useEffect, useState } from 'react'
import { Button, Card, Descriptions, Result, Space, Spin } from 'antd'
import { LogoutOutlined, LoadingOutlined } from '@ant-design/icons'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { authFetch } from '@/api/client'

interface TenantInfo {
  tenant_id: string
  tenant_name: string | null
  tenant_slug: string | null
}

function DashboardPage() {
  const { isAuthenticated, isInitializing, user, activeTenantId, logout } = useAuth()
  const [tenantName, setTenantName] = useState<string | null>(null)

  // 获取租户名称
  useEffect(() => {
    if (!isAuthenticated || !activeTenantId) return

    let cancelled = false
    authFetch<TenantInfo[]>('/api/auth/tenants')
      .then((tenants) => {
        if (cancelled) return
        const matched = tenants.find((t) => t.tenant_id === activeTenantId)
        if (matched) {
          setTenantName(matched.tenant_name ?? matched.tenant_slug ?? activeTenantId)
        } else {
          setTenantName(activeTenantId)
        }
      })
      .catch(() => {
        if (!cancelled) setTenantName(activeTenantId)
      })

    return () => {
      cancelled = true
    }
  }, [isAuthenticated, activeTenantId])

  // 初始化中，显示 loading
  if (isInitializing) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 'calc(100vh - 64px - 96px)',
        }}
      >
        <Spin indicator={<LoadingOutlined spin />} size="large" />
      </div>
    )
  }

  // 未认证（初始化完成但无 access），跳 /login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <Result
        status="success"
        title={`欢迎回来，${user?.username ?? '--'}`}
        subTitle="你已成功登录 BoxBase"
      />

      <Card title="账户信息" style={{ marginTop: 24 }}>
        {user && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{user.email}</Descriptions.Item>
            <Descriptions.Item label="手机号">{user.phone ?? '未设置'}</Descriptions.Item>
            <Descriptions.Item label="活跃租户">{tenantName ?? '加载中...'}</Descriptions.Item>
            <Descriptions.Item label="超管">{user.is_superadmin ? '是' : '否'}</Descriptions.Item>
          </Descriptions>
        )}
        <Space style={{ marginTop: 16 }}>
          <Button
            type="primary"
            danger
            icon={<LogoutOutlined />}
            onClick={() => void handleLogout()}
          >
            登出
          </Button>
        </Space>
      </Card>
    </div>
  )
}

export default DashboardPage

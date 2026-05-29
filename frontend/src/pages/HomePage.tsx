import { useEffect, useState } from 'react'
import { Alert, Button, Card, Descriptions, Space, Spin, Tag, Typography } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { fetchHealth, type HealthResponse } from '@/api/health'

const { Title, Paragraph } = Typography

function HomePage() {
  const navigate = useNavigate()
  const [status, setStatus] = useState<'loading' | 'ok' | 'error'>('loading')
  const [data, setData] = useState<HealthResponse | null>(null)
  const [errorMsg, setErrorMsg] = useState<string>('')

  useEffect(() => {
    async function check() {
      try {
        const result = await fetchHealth()
        setData(result)
        setStatus('ok')
      } catch (err: unknown) {
        setErrorMsg(err instanceof Error ? err.message : String(err))
        setStatus('error')
      }
    }
    void check()
  }, [])

  return (
    <>
      <Title>Hello, BoxBase</Title>
      <Paragraph>Welcome to BoxBase v1.0 — Lightweight multi-tenant SaaS framework.</Paragraph>

      <Card title="Backend Health Check" style={{ maxWidth: 500, marginTop: 16 }}>
        {status === 'loading' && (
          <Spin indicator={<LoadingOutlined spin />} description="Checking backend...">
            {/* Spin 需要子元素才能正确渲染 description */}
            <div style={{ padding: 40 }} />
          </Spin>
        )}
        {status === 'ok' && data && (
          <>
            <Tag icon={<CheckCircleOutlined />} color="success">
              Healthy
            </Tag>
            <Descriptions column={1} style={{ marginTop: 16 }}>
              <Descriptions.Item label="Status">{data.status}</Descriptions.Item>
              <Descriptions.Item label="Service">{data.service}</Descriptions.Item>
              <Descriptions.Item label="Version">{data.version}</Descriptions.Item>
            </Descriptions>
          </>
        )}
        {status === 'error' && (
          <Alert
            type="error"
            icon={<CloseCircleOutlined />}
            title="Backend unreachable"
            description={errorMsg}
          />
        )}
      </Card>

      <Paragraph style={{ marginTop: 16 }}>
        <Link to="/no-such-page">Test 404</Link>
      </Paragraph>
      <Space style={{ marginTop: 16 }}>
        <Button onClick={() => navigate('/login')}>Go Login</Button>
        <Button onClick={() => navigate('/dashboard')}>Go Dashboard</Button>
      </Space>
    </>
  )
}

export default HomePage

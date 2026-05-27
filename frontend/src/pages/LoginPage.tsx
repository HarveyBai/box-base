import { useState } from 'react'
import { Button, Card, Checkbox, Form, Input, Space, Typography } from 'antd'
import { Link } from 'react-router-dom'

const { Title } = Typography

interface LoginFormValues {
  username: string
  password: string
  remember: boolean
}

function LoginPage() {
  const [form] = Form.useForm<LoginFormValues>()
  const [loading, setLoading] = useState(false)

  const handleSubmit = (values: LoginFormValues) => {
    // 暂时只打印到 console，不接后端 API（Week 2 接 FastAPI Users）
    console.log('登录表单提交:', values)
    setLoading(true)
    // 模拟 loading 效果，Week 2 替换为真实 API 调用
    setTimeout(() => {
      setLoading(false)
    }, 1000)
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 64px - 96px)',
      }}
    >
      <Card style={{ width: 400 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={3} style={{ textAlign: 'center', margin: 0 }}>
            BoxBase 登录
          </Title>
          <Form form={form} onFinish={handleSubmit} layout="vertical">
            <Form.Item
              label="用户名"
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input placeholder="请输入用户名" />
            </Form.Item>
            <Form.Item
              label="密码"
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码长度不能少于 6 位' },
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
            <Form.Item name="remember" valuePropName="checked">
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                登录
              </Button>
            </Form.Item>
          </Form>
          <div style={{ textAlign: 'center' }}>
            <Link to="/register">还没有账号？立即注册</Link>
          </div>
        </Space>
      </Card>
    </div>
  )
}

export default LoginPage

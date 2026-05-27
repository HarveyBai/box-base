import { Button, Space, Typography } from 'antd'
import { SmileOutlined, RocketOutlined } from '@ant-design/icons'
import { Link } from 'react-router-dom'

const { Title, Paragraph } = Typography

function HomePage() {
  return (
    <>
      <Title>BoxBase Frontend Boot Check</Title>
      <Paragraph>
        如果你能看到这段文字、下面两个按钮和图标，说明 React 19.2 + Vite 8 + AntD 6 + Icons 6
        的渲染链路全部通畅。
      </Paragraph>
      <Paragraph>路由系统已就位（react-router-dom v7）</Paragraph>
      <Space>
        <Button type="primary" icon={<SmileOutlined />}>
          Primary Button
        </Button>
        <Button icon={<RocketOutlined />}>Default Button</Button>
      </Space>
      <Paragraph style={{ marginTop: 16 }}>
        <Link to="/non-existent">测试 404 路径</Link>
      </Paragraph>
      <Space style={{ marginTop: 16 }}>
        <Link to="/login">
          <Button>登录页</Button>
        </Link>
        <Link to="/dashboard">
          <Button>Dashboard</Button>
        </Link>
      </Space>
    </>
  )
}

export default HomePage

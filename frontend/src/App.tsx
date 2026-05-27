// import type {} from '@/App'

import { ConfigProvider, Layout, Typography, Button, Space } from 'antd'
import { SmileOutlined, RocketOutlined } from '@ant-design/icons'

const { Header, Content } = Layout
const { Title, Paragraph } = Typography

function App() {
  return (
    <ConfigProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center' }}>
          <Title level={3} style={{ color: '#fff', margin: 0 }}>
            BoxBase v1.0 — Frontend Boot Check
          </Title>
        </Header>
        <Content style={{ padding: '48px' }}>
          <Paragraph>
            如果你能看到这段文字、下面两个按钮和图标，说明 React 19.2 + Vite 8 + AntD 6 + Icons 6
            的渲染链路全部通畅。
          </Paragraph>
          <Space>
            <Button type="primary" icon={<SmileOutlined />}>
              Primary Button
            </Button>
            <Button icon={<RocketOutlined />}>Default Button</Button>
          </Space>
        </Content>
      </Layout>
    </ConfigProvider>
  )
}

export default App

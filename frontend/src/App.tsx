import { Outlet } from 'react-router-dom'
import { ConfigProvider, Layout, Typography } from 'antd'

const { Header, Content } = Layout
const { Title } = Typography

function App() {
  return (
    <ConfigProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center' }}>
          <Title level={3} style={{ color: '#fff', margin: 0 }}>
            BoxBase v1.0
          </Title>
        </Header>
        <Content style={{ padding: '48px' }}>
          <Outlet />
        </Content>
      </Layout>
    </ConfigProvider>
  )
}

export default App

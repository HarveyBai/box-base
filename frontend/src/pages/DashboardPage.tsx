import { Button, Result } from 'antd'
import { Link } from 'react-router-dom'

function DashboardPage() {
  return (
    <Result
      status="success"
      title="登录成功（占位）"
      subTitle="Week 2 接 FastAPI Users 后接入真实认证"
      extra={
        <Link to="/">
          <Button type="primary">返回首页</Button>
        </Link>
      }
    />
  )
}

export default DashboardPage

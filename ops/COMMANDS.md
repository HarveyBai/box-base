# COMMANDS.md — 常用命令备忘


## 项目相关命令

```bash
mise run dev	        # 前端 5173 + 后端 8000 同时启动，两方日志可见
mise run dev:frontend	# 仅启动前端 Vite dev server
mise run dev:backend	# 仅启动后端 Uvicorn

```


## git仓库

### ssh agent配置，解决每次push都输入密码的问题

```bash
Get-Service ssh-agent     # 确认服务状态是 Running
Start-Service ssh-agent   # 启动服务
# Set-Service -Name ssh-agent -StartupType Automatic

ssh-add -l
ssh-add $env:USERPROFILE\.ssh\id_rsa_320312396
```


### 清理node进程

```powershell
# 查看所有 node 相关进程
Get-Process | Where-Object { $_.ProcessName -like "*node*" } | Format-Table Id, ProcessName, StartTime

# 如果看到多个 node.exe,挑老的那个杀掉(替换 PID)
Stop-Process -Id <老进程的PID> -Force
```


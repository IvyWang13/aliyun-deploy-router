# 阿里云部署路由 · Aliyun Deploy Router

一个面向 AI 编程新手的 Agent Skill。说“帮我把这个项目部署到阿里云”，由 Agent 分析项目、选择部署 Skill，遇到问题主动搜索 GitHub issues、核对修复方案并重新验证。

**当前为早期版本：检索脚本和安装检查有自动测试，完整云部署与自动修复尚未完成端到端实测。** 本项目是社区项目，与阿里云无官方隶属关系。

## 能做什么

- 从代码判断静态网站、服务端运行、数据库和文件存储需求。
- 协调适合的部署 Skill，优先复用已有部署和资源。
- 在创建资源前检查配置与费用，按用户授权执行。
- 安装、构建、部署或验收失败时，自动检索对应上游 GitHub issues。
- 核对系统和版本、已合并与已发布的修复，做最小改动并验证。
- 输出访问地址、实际检查结果、更新方式及资源清理说明。

这是供支持 Skills 的 AI Agent 执行的工作流程，不是独立运行的云部署服务。自动排错是默认行为，无需用户另行要求；并非所有错误都能自动解决。

## 安装

在支持 Agent Skills 的客户端中安装。以 Codex 为例，需要 Node.js/npm 才能使用以下安装器：

```bash
npx skills add IvyWang13/aliyun-deploy-router --skill aliyun-deploy-router --agent codex
```

也可以克隆仓库，将完整的 `skills/aliyun-deploy-router/` 目录复制到客户端的 Skills 目录。Codex 的本地目录通常是 `~/.codex/skills/`；配置了 `CODEX_HOME` 时使用对应目录。已有同名 Skill 时先备份自己的修改。不要只复制 SKILL.md。

安装后新建会话；如仍未被识别，重启客户端。检查实际安装位置的文件完整性：

```bash
python3 /path/to/aliyun-deploy-router/scripts/check_install.py
```

本 Skill 的辅助脚本只使用 Python 标准库，需要 Python 3.9 或更高版本。Agent 还需要读取项目、运行命令和访问 GitHub/官方文档的能力；实际部署所需的云工具、账号授权与其他 Skills 由选中的部署路线决定，并未打包在本仓库里。

## 使用

在你的 Web App 项目中告诉 Agent：

> 用 $aliyun-deploy-router 帮我把这个项目部署到阿里云。

也支持：

> 帮我更新现有的阿里云部署，保留当前数据和访问地址。

> 部署失败了，帮我定位问题并修复。

可补充预算、区域和已有服务器。Agent 应根据现有上下文工作，仅询问阻塞执行的必要信息。不要把 AccessKey、数据库密码等秘密贴进聊天或 GitHub issue。

## 一个简单的例子：把 AI 写的网页发给朋友

你用 AI 做了一个待办事项 Web App，在自己电脑上能打开，但朋友无法访问你的 `localhost` 链接。你想把它部署到阿里云，又不知道该选哪些服务。

安装本 Skill 后，在项目目录中告诉 Agent：

> 用 $aliyun-deploy-router 帮我把这个待办事项 App 部署到阿里云，让朋友能打开试用。先告诉我要用哪些服务、大概多少钱。

Skill 会按下面的流程处理：

1. **看项目**：检查代码和启动方式，判断是否需要后端、数据库，还是只需托管静态网页。
2. **选部署方案**：选择合适的部署 Skill，说明所需服务和预计费用；缺少账号授权时引导你完成配置。
3. **执行部署**：在费用和操作得到授权后，把应用部署上去。
4. **遇错自动排查**：读取错误，搜索相关 GitHub issues，核对版本后尝试修复，再重新验证。你不用额外说“帮我查 issues”。
5. **交付结果**：验证成功后给你可分享的访问链接，并说明怎么更新应用、怎么释放不用的资源。

这是预期使用流程示例，并非已完成的部署实测。如果某一步无法继续，Skill 会说明卡在哪里、需要你补充什么，以及是否已有资源产生费用。

## 部署候选

| 候选 | 定位 |
|---|---|
| [阿里云官方 ECS Skill](https://github.com/aliyun/alibabacloud-aiops-skills) | 需要 ECS 的应用部署 |
| [qianwenai-deploy](https://github.com/QianWen-AI/qianwenai-deploy) | 全栈部署、更新与资源管理 |
| [社区 aliyun-skills](https://github.com/shigzz/aliyun-skills) | 前端、OSS、域名及 CDN 编排 |

这些是外部依赖候选，未复制到本仓库；使用前需重新核验其当前能力、许可和安装方式。路由不会默认给每个项目购买服务器或数据库。

## GitHub 检索

也可以单独运行只读的公共 issue 搜索：

```bash
python3 skills/aliyun-deploy-router/scripts/search_issues.py \
  --repo aliyun/alibabacloud-aiops-skills \
  --query '"missing port in address"'
```

查询前请移除日志中的秘密和个人信息。脚本不读取登录凭证，但不会替你自动脱敏。公开 GitHub API 有限流，失败时 Agent 应改用可用的 GitHub 工具或网页查询。

- 返回码 `0`：查询成功；`truncated` 表示仅展示部分匹配条目。
- 返回码 `1`：API、网络或响应异常。
- 返回码 `2`：输入参数错误。
- 返回码 `3`：GitHub 返回不完整搜索结果，不能据此断言不存在相关问题。

## 验证与开发

```bash
python3 skills/aliyun-deploy-router/scripts/check_install.py
python3 -B -m unittest discover -s skills/aliyun-deploy-router/tests -v
```

测试覆盖缺失文件、失效/循环链接、有效链接、限流、断网、异常响应、查询范围以及不完整结果处理。CI 在 Linux 和 macOS 上运行。Windows 云工具兼容性与真实收费资源部署不在这些测试覆盖范围内。

- [Skill 入口](skills/aliyun-deploy-router/SKILL.md)
- [路由规则](skills/aliyun-deploy-router/references/routes.md)
- [自动排错流程](skills/aliyun-deploy-router/references/issue-repair.md)
- [已知问题及防护](skills/aliyun-deploy-router/references/known-issues.md)

欢迎提交可复现的问题和 PR。报告时提供系统、工具版本、失败阶段、脱敏后的错误及最小复现；不要上传云凭证、私人项目源码或完整未脱敏日志。

## License

[MIT](LICENSE)。第三方 Skills 与工具遵循各自的许可证。

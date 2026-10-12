# 部署路径与候选目录

此文件是候选起点，不是实时能力保证。使用前核验仓库当前内容、适用地区/账号、支持项目和授权方式。候选记录核对日期：2026-10-11。

## 先判断运行需求

| 项目证据 | 优先考虑 | 判断边界 |
|---|---|---|
| 构建产物只有 HTML/CSS/JS/静态文件，无运行时服务端需求 | 静态托管或 OSS 静态站点路线 | 不能将含服务端 API、SSR、私密密钥的应用当纯静态站点；核验访问域名及 HTTPS 条件 |
| 需要 Node/Python/Java 等服务进程 | 应用托管或 ECS | 依据运行时、长连接、后台任务、持久化及用户管理偏好选择；不要自动认为所有项目都需要 ECS |
| 前后端加数据库 | 能覆盖应用与数据库的部署路径 | 先复用适合的已有数据库；不要仅凭依赖名就买 RDS |
| 已有部署且要求更新 | 原部署 Skill/工具 | 先读取状态，不切换工具新建一套 |

仅给服务端使用的环境变量不应进入前端构建产物。对象存储不能替代数据库，服务器临时文件也不能默认作为可靠的上传存储。

## 已核验的候选

### 官方 ECS：alibabacloud-ecs-code-deploy

- 仓库：https://github.com/aliyun/alibabacloud-aiops-skills
- 入口：`skills/computing/computenest/alibabacloud-ecs-code-deploy/SKILL.md`
- 基于 `aliyun appmanager`，覆盖预检、报价、新建/已有 ECS、部署与日志验证。
- 适用于确定需要 ECS 的项目；不是所有应用的默认最低成本方案。
- 错误可能来自其依赖 CLI，先定位再查对应仓库。该集合包含大量非部署 Skill。

### 全栈编排：qianwenai-deploy

- 仓库：https://github.com/QianWen-AI/qianwenai-deploy
- 阅读当前 README 和 `skills/` 中实际入口，不猜测 Skill 名称或文件布局。
- README 描述支持阿里云国内站、本地/Git 项目、ECS、可选 RDS、更新和资源清理。
- 若已有 `.qianwenai-deploy` 状态，优先沿用；不要让另一工具重建同一应用。

### 社区前端：aliyun-deploy

- 仓库：https://github.com/shigzz/aliyun-skills
- 入口：`deploy/SKILL.md`
- 描述覆盖域名、DNS、OSS、CDN 前端部署编排。使用前核验所需子 Skills 和脚本，以及是否会操作已有域名。
- 是社区维护候选，不称作阿里云官方产品。

若现有候选不适配（例如用户需要应用托管而非 ECS），通过 https://skills.aliyun.com/ 或官方仓库发现合适入口，再读真实文件。不要为了用候选而改变用户需求。无适配 Skill 时可用官方文档/CLI 完成授权任务，但明确说明这是工具级回退。

安装方式优先遵循环境 skill-installer；需要通用 CLI 时核验官方当前说明：
https://help.aliyun.com/zh/skillsportal/quickly-use-alibaba-cloud-skills

## 先说明的部署决策

以实际检查结果填写，不套用固定默认值：
“项目需要 ___，所以选 ___；会用到 ___，暂时不需要 ___。已有资源 ___。预计费用 ___（周期/包含项/不包含项）。还需要确定 ___。”

只询问实际影响部署且无法推断的信息，例如新建还是已有服务器、目标区域、预算。已明确的选项不要重复问。

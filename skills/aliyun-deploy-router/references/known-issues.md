# 已知问题与部署前检查

核对日期：2026-10-11。以下是上游反馈和本包防护，不是对所有版本的缺陷判定。执行时重新核对状态、适用版本和实际环境。无需为不涉及的组件安装依赖。

| 来源 | 症状及证据范围 | 本入口如何处理 |
|---|---|---|
| [aliyun #4](https://github.com/aliyun/alibabacloud-aiops-skills/issues/4)、[skills #747](https://github.com/vercel-labs/skills/issues/747)（均已关闭） | 找不到 Skill；历史安装器深层目录发现不足 | 查当前实际文件路径和 frontmatter 名称；按当前安装器支持的精确子目录安装，必要时按文档用 full-depth；不能把旧 bug 当成所有最新版的缺陷 |
| [skills #456](https://github.com/vercel-labs/skills/issues/456)、[#1199](https://github.com/vercel-labs/skills/issues/1199)（开放） | 链接目录中的相对软链接失效；更新后 copy 变 symlink | 更新前记录/备份用户修改和安装模式，更新后验证 realpath 和引用文件；优先使用环境安装器的目录复制方式，不盲目覆盖/删除现有目录 |
| [skills #1517](https://github.com/vercel-labs/skills/issues/1517)（已关闭） | 1.5.13 的仓库根级 Skill 安装/更新可能只留下 SKILL.md | 检查 references/scripts 完整性。本包发布时放在 `skills/aliyun-deploy-router/`，不要只发布或复制入口文件；检查所用版本，不宣称该 bug 仍存在于全部最新版 |
| [aliyun #7](https://github.com/aliyun/alibabacloud-aiops-skills/issues/7)（开放） | Windows 工具安装脚本把多个 CPU 查询结果直接转整数失败 | 仅 Windows 且相关安装器时核对脚本/版本，采用经过核实的上游修复；不把本地 macOS 测试算作 Windows 测试 |
| [aliyun #8](https://github.com/aliyun/alibabacloud-aiops-skills/issues/8)（开放） | Windows Workbench v1.0.0 能列实例但远程 exec 失败 | 仅走 Workbench 路线时，在已有目标实例做无副作用远程执行探测；不能用“能列实例”证明可部署。不把它当作所有 appmanager 部署都受影响 |
| [aliyun #9](https://github.com/aliyun/alibabacloud-aiops-skills/issues/9)、[#6](https://github.com/aliyun/alibabacloud-aiops-skills/issues/6)（开放） | 安全工具拦截；报告者认为是误报 | 检查具体文件、规则和可信来源，区分用户判断与维护者确认；不关闭扫描、不强行绕过拦截，不保证本包通过所有扫描器 |
| [ECS lessons-learned](https://github.com/aliyun/alibabacloud-aiops-skills/blob/master/skills/computing/computenest/alibabacloud-ecs-code-deploy/references/lessons-learned.md) | Java 默认脚本找不到 JAR，低配置上构建可能超时/内存不足 | 核对构建产物与启动命令；有可信兼容的已发布产物时考虑直接使用；不要对所有 Java 项目套用固定内存值 |

## 检索脚本自身的边界

- 无额外 Python 包依赖，需 Python 3；无法运行时用已有 GitHub 工具/网页，不为检索安装整套云 CLI。
- API 限流、断网、异常响应应返回明确错误；部分结果显式标记，不将检索失败说成“没找到”。
- 查询前由 Agent 脱敏。脚本不读凭据，但这不代表任意输入都适合公开搜索。
- 摘要只是定位用；采用方案前打开全文、评论和发布记录。

本包自动回归：`python3 -B -m unittest discover -s <skill-dir>/tests -v`。
本包安装检查：`python3 <skill-dir>/scripts/check_install.py`。
这些检查验证脚本与安装结构，不证明云端部署、模型路由决策或修复建议必然正确。

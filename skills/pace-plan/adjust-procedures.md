# 迭代范围调整详细规程

> **职责**：迭代中途范围调整的详细处理流程（Step 2.5）。

## Step 2.5：迭代中途范围调整（adjust 模式）

**与 /pace-change 的边界**：change 管 PF 级需求变更（add/pause/resume/modify），adjust 管迭代范围级调整（本迭代纳入/移出哪些 PF）。

1. 读取 `.devpace/iterations/current.md`（不存在则提示"无活跃迭代，请先 `/pace-plan next`"）
2. 展示当前迭代状态（复用 Step 1 逻辑）：目标、PF 列表（含完成状态）、剩余容量
3. 使用 `AskUserQuestion` 询问调整意图，支持操作：
   - **增加 PF**：从 project.md 待做 PF 中选择纳入，附带工作量估算
   - **移除 PF**：将未开始的 PF 移回待做池（已开始的建议用 `/pace-change pause`）
   - **调整优先级**：重排本迭代 PF 的 P0/P1/P2 优先级
4. 每次操作后重算容量：
   - 汇总当前迭代所有 PF 的预估工作量
   - 与迭代周期（如有）对比
   - 容量超出 → 警告："调整后预估工作量 X 会话，超出剩余容量 Y 会话，建议移除低优先级 PF"
5. 确认后更新 `iterations/current.md`（PF 列表 + 优先级 + 变更记录追加调整原因）
6. 不关闭迭代，不归档

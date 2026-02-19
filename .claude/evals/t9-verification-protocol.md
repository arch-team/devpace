# T9 交互验证方案

> V2.3（跨会话恢复）+ V2.4（质量检查拦截）+ V2.11（会话结束保存）
> 目标项目：diagnostic-agent-framework

## 前置条件

```bash
cd /Users/jinhuasu/Project_Workspace/Anker-Projects/diagnostic-agent-framework
claude --plugin-dir ../ml-platform-research/llm-platform-solution/claude-code-forge/devpace
```

确认：Claude 读取 state.md 后报告"上次停在 PF-2（knowledge.md 分离），继续推进？"（或类似自然语言）

---

## Test 1: V2.11 — 会话结束保存（先测，为 V2.3 准备断点）

### Step 1a: 进入推进模式

对 Claude 说：

> 帮我做 PF-2（knowledge.md 分离），开始吧

**预期**：Claude 进入推进模式，创建 CR-002 或绑定已有 CR，开始意图检查点

### Step 1b: 做一些有意义的工作

让 Claude 完成 Phase A（标注分析），至少产出一些工作成果。

### Step 1c: 触发会话结束

对 Claude 说：

> 先到这

**检查项**（E-WF-08）：
- [ ] state.md 已更新：进行中 = CR-002 的当前阶段，下一步 = 具体建议
- [ ] CR-002.md 已更新：事件表追加本次事件，质量检查 checkbox 反映最新
- [ ] Claude 输出 3-5 行会话总结（做了什么 + 质量检查 + 下一步）
- [ ] state.md ≤ 15 行

验证命令（会话结束后在终端执行）：
```bash
cat .devpace/state.md          # 检查更新
cat .devpace/backlog/CR-002.md # 检查事件表
wc -l .devpace/state.md        # 检查 ≤ 15 行
```

---

## Test 2: V2.3 — 跨会话恢复（第 1 次中断）

### Step 2a: 启动新会话

```bash
claude --plugin-dir ../ml-platform-research/llm-platform-solution/claude-code-forge/devpace
```

**检查项**（E-WF-06 第 1 次）：
- [ ] Claude 自动读取 state.md
- [ ] Claude 用 1 句自然语言报告状态（不暴露 ID、不说 "developing"）
- [ ] 报告内容与 Test 1 结束时的工作一致
- [ ] Claude 等待用户指令（不自作主张开始工作）
- [ ] 用户无需解释上次做了什么（零手动解释）

### Step 2b: 继续工作

对 Claude 说：

> 继续

**预期**：Claude 从断点恢复，继续 CR-002 的工作

### Step 2c: 做更多工作后再次中断

让 Claude 推进到下一阶段（如完成 Phase B），然后说：

> 结束

（重复 Test 1c 的检查项）

---

## Test 3: V2.3 — 跨会话恢复（第 2 次中断）

重复 Test 2 的流程。这次让 Claude 推进到 developing → verifying 转换（触发质量门禁）。

**额外检查项**：
- [ ] developing → verifying 转换前自动运行 checks.md 中的检查
- [ ] 质量检查结果记录在 CR 文件中

---

## Test 4: V2.3 — 跨会话恢复（第 3 次中断）

重复 Test 2 的流程。验证第 3 次恢复仍然准确。

**累计检查项**（3 次中断后）：
- [ ] 3 次新会话均自动恢复，零手动解释
- [ ] state.md 每次会话结束都被正确更新
- [ ] CR 事件表记录了完整的工作历史

---

## Test 5: V2.4 — 质量检查拦截

### Step 5a: 在 verifying 阶段故意引入问题

如果 CR-002 在 verifying 阶段，手动编辑代码引入一个语法错误：

```bash
# 故意引入错误（以 Python 为例）
echo "def broken(:" >> packages/framework/some_file.py
```

### Step 5b: 触发质量检查

对 Claude 说：

> 继续推进，准备提交 review

**检查项**（E-WF-09）：
- [ ] Claude 运行 checks.md 中的质量检查
- [ ] 检查发现语法错误
- [ ] Claude 自行修复错误（不请示用户）
- [ ] 修复后重新运行质量检查
- [ ] 质量检查通过后才推进到 in_review
- [ ] Claude 不会跳过或忽略质量检查

### Step 5c: 清理

```bash
# 恢复故意引入的错误（如果 Claude 没有修复）
git checkout packages/framework/some_file.py
```

---

## 结果记录模板

```
V2.3  跨会话恢复:  [ ] PASS / [ ] FAIL — 3/3 次恢复均零手动解释
V2.4  质量检查拦截: [ ] PASS / [ ] FAIL — 检查拦截 + 自行修复 + 不跳过
V2.11 会话结束保存: [ ] PASS / [ ] FAIL — state.md 更新 + CR 更新 + 3-5 行总结

备注：
```

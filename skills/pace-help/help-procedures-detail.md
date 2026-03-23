# help-procedures-detail — 特定命令用法详解

> 由 SKILL.md 路由表加载。`<command-name>` 子命令时读取。

## Step 1：识别命令名

从 $ARGUMENTS 中提取命令名，规范化处理：

| 用户输入 | 规范化结果 |
|---------|-----------|
| `dev` | `pace-dev` |
| `pace-dev` | `pace-dev` |
| `/pace-dev` | `pace-dev` |
| `pace-dev-workspace` | `pace-dev`（去掉 workspace 后缀） |

## Step 2：读取 SKILL.md

读取 `skills/<规范化命令名>/SKILL.md` 全文。

如果文件不存在 → 输出：
```
未找到命令 "<用户输入>"。输入 `/pace-help commands` 查看所有可用命令。
```
结束。

## Step 3：提取并格式化

从 SKILL.md 全文中提取以下信息，格式化输出：

### 3.1 用途（1 句话）

从标题行（`# /pace-xxx —`）后的第一段提取。

### 3.2 子命令列表

从"执行路由"表中提取所有子命令及其对应的简要说明。格式：

```
子命令：
  (空)       — [说明]
  detail     — [说明]
  why        — [说明]
  ...
```

如果 SKILL.md 中无路由表（无子命令），跳过此节。

### 3.3 常用触发方式

从 frontmatter `description` 中提取中文触发关键词。格式：

```
触发方式：
  直接调用：/pace-xxx [子命令]
  自然语言："[关键词1]" "[关键词2]" "[关键词3]"
```

### 3.4 相关命令

从 description 的 `NOT for` 部分提取相关命令。格式：

```
相关命令：
  /pace-yyy — [NOT-for 中提到的用途]
  /pace-zzz — [NOT-for 中提到的用途]
```

## Step 4：导航提示

末尾附：`查看所有命令：/pace-help commands`

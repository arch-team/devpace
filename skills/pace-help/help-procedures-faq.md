# help-procedures-faq — 常见操作问题

> 由 SKILL.md 路由表加载。`faq` 子命令时读取。

## Step 1：读取 FAQ 数据源

读取 `knowledge/_guides/help-faq.md`。

## Step 2：输出 FAQ

按数据源中的分类逐条输出。每条格式：

```
Q: [问题]
A: [简明回答] → /pace-xxx [子命令]
```

## Step 3：导航提示

末尾附：

```
找不到答案？
  了解概念：/pace-theory <概念名>
  查看命令用法：/pace-help <命令名>
  或直接描述你的问题，Claude 会帮你找到对应功能。
```

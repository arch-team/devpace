#!/usr/bin/env node
/**
 * devpace UserPromptSubmit hook — Forced Skill Evaluation (A+B combined)
 *
 * Purpose: Improve skill activation reliability from ~50% (baseline) to ~100%.
 * Based on Scott Spence's "Commitment Mechanism" research, adapted for devpace's
 * 19-skill ecosystem.
 *
 * Strategy:
 *   Path A — keyword match: high-confidence phrases → direct route suggestion
 *   Path B — forced eval:   zero/multi match → commitment mechanism prompt
 *
 * Subsumes intent-detect.mjs (change management detection is included).
 *
 * Communication: stdout advisory (exit 0), never blocking.
 * Architecture: no Markdown parsing, only stdin JSON + .devpace/ existence check.
 */

import { existsSync } from 'node:fs';
import { readStdinJson, getProjectDir } from './lib/utils.mjs';

const input = await readStdinJson();
const projectDir = getProjectDir();

// Gate 1: only act if .devpace is initialized
if (!existsSync(`${projectDir}/.devpace/state.md`)) {
  process.exit(0);
}

const userPrompt = input?.content ?? '';
if (!userPrompt.trim()) {
  process.exit(0);
}

// Gate 2: explicit slash command — user already chose a skill, skip evaluation
if (/^\s*\/pace-/.test(userPrompt)) {
  process.exit(0);
}

// Gate 3: pure technical operations unrelated to devpace workflows
const techPattern = /^(git\s|npm\s|yarn\s|pnpm\s|bun\s|make\s|cd\s|ls\s|cat\s|grep\s|find\s|docker\s|kubectl\s)/;
if (techPattern.test(userPrompt.trim())) {
  process.exit(0);
}

// ---------------------------------------------------------------------------
// Path A: Keyword routing table
//
// Each skill maps to an array of high-confidence trigger patterns.
// Patterns are multi-word phrases or specific terms unlikely to collide.
// Source of truth: each SKILL.md description field.
// ---------------------------------------------------------------------------

const SKILL_ROUTES = {
  'pace-init': [
    /初始化/, /pace-init/, /开始追踪/, /初始化研发/, /set up devpace/,
    /健康检查\s*devpace/, /重置\s*devpace/, /预览初始化/,
  ],
  'pace-dev': [
    /开始做/, /帮我改(?!需求|验收)/, /继续推进/, /编码/, /写代码/,
    /\bimplement\b/, /\brefactor\b/, /\bcoding\b/,
  ],
  'pace-status': [
    /进度怎样/, /做到哪了/, /项目状态/, /当前状态/, /看看进度/,
    /\bdashboard\b/, /pace-status/,
  ],
  'pace-change': [
    /不做了/, /先不搞/, /加一个/, /加需求/, /改一下/, /改需求/,
    /优先级调/, /砍掉/, /搁置/, /放一放/, /不要这个功能/,
    /新增需求/, /先做这个/, /恢复之前/, /需求变了/, /停掉/,
    /捡回来/, /排到前面/, /追加/, /补一个/, /范围变了/,
    /\bdrop\b/, /\bshelve\b/, /\breprioritize\b/,
  ],
  'pace-review': [
    /代码审查/, /提交审核/, /提交审批/, /Gate\s*2/i,
    /pace-review/,
  ],
  'pace-next': [
    /下一步做什么/, /接下来做什么/, /该做什么/, /什么最重要/,
    /应该先做哪个/, /推荐做什么/, /为什么推荐这个/,
    /pace-next/,
  ],
  'pace-biz': [
    /业务机会/, /专题/, /\bEpic\b/, /分解需求/, /精炼/, /细化/,
    /补充需求/, /战略对齐/, /业务全景/, /业务规划/, /需求发现/,
    /头脑风暴/, /导入需求/, /从文档导入/, /代码分析需求/,
    /技术债务盘点/, /\bdiscover\b/, /\bimport\b(?!.*node_modules)/,
    /\binfer\b/, /\brefine\b/, /pace-biz/,
  ],
  'pace-test': [
    /跑测试/, /测试覆盖/, /验证一下/, /验收/, /回归/,
    /影响分析/, /测试策略/, /\bcoverage\b/, /pace-test/,
  ],
  'pace-plan': [
    /规划迭代/, /下个迭代/, /迭代规划/, /排期/, /\bsprint\b/,
    /调整迭代范围/, /迭代调整/, /迭代健康/, /pace-plan/,
  ],
  'pace-retro': [
    /复盘/, /\bretro\b/, /\bDORA\b/, /质量报告/, /交付效率/,
    /度量报告/, /中期检查/, /交付概率/, /pace-retro/,
    /能按时交付吗/,
  ],
  'pace-guard': [
    /预检/, /预分析/, /\bguard\b/, /\brisk\b/, /隐患/, /安全检查/,
    /pace-guard/,
  ],
  'pace-sync': [
    /关联\s*Issue/, /配置同步/, /解除关联/, /\bunlink\b/,
    /创建\s*Issue/, /同步状态/, /GitHub\s*Actions/i,
    /\bpipeline\b/, /pace-sync/,
  ],
  'pace-release': [
    /发布/, /部署/, /上线/, /\brelease\b/, /pace-release/,
  ],
  'pace-feedback': [
    /用户反馈/, /线上问题/, /生产问题/, /告警/, /线上bug/,
    /\bincident\b/, /故障/, /\bP0\b/, /\bP1\b/, /严重故障/,
    /postmortem/, /事后复盘/,
  ],
  'pace-role': [
    /切换角色/, /切换视角/, /以.*视角/, /作为产品经理/, /作为运维/,
    /换个角度看/, /pace-role/,
  ],
  'pace-theory': [
    /怎么理解/, /方法论/, /\bBizDevOps\b/, /什么是\s*BR/,
    /什么是\s*PF/, /CR\s*是什么/, /价值链/, /状态机原理/,
    /成效指标/, /pace-theory/,
  ],
  'pace-trace': [
    /决策记录/, /决策原因/, /架构决策/, /\bADR\b/, /技术选型/,
    /pace-trace/,
  ],
  'pace-learn': [
    /知识库/, /lessons\s*learned/, /学到了什么/, /pace-learn/,
  ],
};

// Ambiguous single-word patterns that may match multiple skills.
// These are tracked separately and trigger forced eval if they're the only match signal.
const AMBIGUOUS_TERMS = {
  '实现':     ['pace-dev'],
  '修复':     ['pace-dev', 'pace-feedback'],
  '做个':     ['pace-dev', 'pace-biz'],
  '开发':     ['pace-dev'],
  '重构':     ['pace-dev'],
  'fix':      ['pace-dev'],
  'build':    ['pace-dev', 'pace-sync'],
  '审核':     ['pace-review'],
  '帮我看看': ['pace-review', 'pace-status'],
  'review':   ['pace-review'],
  '最紧急':   ['pace-next'],
  '优先级':   ['pace-next', 'pace-change'],
  '计划':     ['pace-plan', 'pace-biz'],
  '安排':     ['pace-plan'],
  '回顾':     ['pace-retro'],
  '总结':     ['pace-retro'],
  '度量':     ['pace-retro', 'pace-theory'],
  '趋势':     ['pace-retro'],
  '瓶颈':     ['pace-retro'],
  '风险':     ['pace-guard'],
  '同步':     ['pace-sync'],
  'sync':     ['pace-sync'],
  'push':     ['pace-sync'],
  'pull':     ['pace-sync'],
  'CI':       ['pace-sync'],
  '构建':     ['pace-sync'],
  'test':     ['pace-test'],
  'verify':   ['pace-test'],
  '进展':     ['pace-status'],
  '总览':     ['pace-status'],
  '概念':     ['pace-theory'],
  '理论':     ['pace-theory'],
  '原理':     ['pace-theory'],
  '追溯':     ['pace-trace', 'pace-theory'],
  '为什么这样做': ['pace-trace'],
  '经验':     ['pace-learn'],
  'pattern':  ['pace-learn'],
  '改进建议': ['pace-feedback'],
  '功能请求': ['pace-feedback'],
  '运维':     ['pace-feedback', 'pace-role'],
  '事件':     ['pace-feedback'],
};

// ---------------------------------------------------------------------------
// Matching logic
// ---------------------------------------------------------------------------

// Phase 1: high-confidence pattern matching
const highConfMatches = new Set();
for (const [skill, patterns] of Object.entries(SKILL_ROUTES)) {
  for (const re of patterns) {
    if (re.test(userPrompt)) {
      highConfMatches.add(skill);
      break;
    }
  }
}

// Phase 2: ambiguous term matching (only adds to candidates, doesn't override)
const ambiguousMatches = new Set();
for (const [term, skills] of Object.entries(AMBIGUOUS_TERMS)) {
  const re = new RegExp(term.includes(' ') ? term : `(?:^|[\\s，。！？、；：""''""])${term}(?:$|[\\s，。！？、；：""''""])`, 'i');
  if (re.test(userPrompt)) {
    for (const s of skills) ambiguousMatches.add(s);
  }
}

// Merge: high-confidence wins; ambiguous only contributes if no high-confidence match
const allMatches = highConfMatches.size > 0 ? highConfMatches : ambiguousMatches;

// ---------------------------------------------------------------------------
// Output decision
// ---------------------------------------------------------------------------

if (allMatches.size === 1) {
  // Path A: unique match — direct route suggestion
  const skill = [...allMatches][0];
  console.log(
    `devpace:skill-route Detected intent → /${skill}. ` +
    `ACTION: Invoke /${skill} to handle this request. ` +
    `If the user's intent does not actually match /${skill}, respond normally instead.`
  );
} else if (allMatches.size > 1) {
  // Path B (partial): multiple candidates — forced eval with narrowed scope
  const candidates = [...allMatches].map(s => `/${s}`).join(', ');
  console.log(
    `devpace:forced-eval Multiple devpace skills may apply: ${candidates}. ` +
    `ACTION: Evaluate which ONE skill best matches the user's intent; ` +
    `state your choice with a brief reason, then invoke that skill; ` +
    `if none truly matches, respond normally without any skill.`
  );
} else {
  // Path B (full): zero keyword match — could be semantic match, force full evaluation
  // Only trigger for prompts that look like they might involve project work
  // (skip casual conversation, greetings, etc.)
  const projectWorkSignals = /做|改|看|查|帮|给|要|来|搞|弄|整|处理|分析|检查|创建|添加|更新|删除|调整|优化|设计|规划|评估|what|how|show|check|create|add|update|delete|start|run|get|set|plan|analyze/i;

  if (projectWorkSignals.test(userPrompt) && userPrompt.length > 3) {
    console.log(
      `devpace:forced-eval No keyword match found, but this may be a devpace workflow request. ` +
      `ACTION: Evaluate whether this request matches any devpace skill — ` +
      `core skills: /pace-dev (implement), /pace-status (progress), /pace-next (recommendation), ` +
      `/pace-change (requirement change), /pace-biz (business planning), /pace-review (code review); ` +
      `if a skill matches, invoke it; if not, respond normally.`
    );
  }
  // else: casual/non-project prompt — no intervention needed
}

process.exit(0);

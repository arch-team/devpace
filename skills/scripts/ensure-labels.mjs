#!/usr/bin/env node

import { execFileSync } from 'child_process';

const REQUIRED_LABELS = [
  // 状态标签
  { name: 'backlog', color: 'ededed' },
  { name: 'in-progress', color: 'ededed' },
  { name: 'needs-review', color: 'ededed' },
  { name: 'awaiting-approval', color: 'ededed' },
  { name: 'approved', color: 'ededed' },
  { name: 'done', color: 'ededed' },
  { name: 'released', color: 'ededed' },
  { name: 'on-hold', color: 'ededed' },
  { name: 'planning', color: 'ededed' },
  { name: 'gate-1-passed', color: 'ededed' },
  { name: 'gate-2-passed', color: 'ededed' },
  { name: 'gate-3-passed', color: 'ededed' },
  // 实体类型标签
  { name: 'devpace:epic', color: '7057ff' },
  { name: 'devpace:br', color: '0075ca' },
  { name: 'devpace:pf', color: '1a7f37' },
  { name: 'devpace:cr', color: 'e4e669' },
];

function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1) {
    console.error('Usage: node ensure-labels.mjs <owner/repo>');
    process.exit(1);
  }

  const repo = args[0];
  const result = {
    status: 'ok',
    created: [],
    existing: [],
    failed: []
  };

  // 步骤 1: 检查 gh CLI 是否可用
  try {
    execFileSync('gh', ['auth', 'status'], {
      stdio: 'pipe',
      encoding: 'utf-8'
    });
  } catch (error) {
    result.status = 'unavailable';
    console.log(JSON.stringify(result));
    process.exit(0);
  }

  // 步骤 2: 获取现有标签
  let existingLabels = [];
  try {
    const output = execFileSync('gh', [
      'label', 'list',
      '--repo', repo,
      '--json', 'name',
      '--limit', '200'
    ], {
      encoding: 'utf-8',
      stdio: 'pipe'
    });
    existingLabels = JSON.parse(output).map(label => label.name);
  } catch (error) {
    // 如果获取标签失败，视为仓库不可用
    result.status = 'unavailable';
    console.log(JSON.stringify(result));
    process.exit(0);
  }

  // 步骤 3-4: 遍历必需标签，创建缺失的标签
  for (const label of REQUIRED_LABELS) {
    if (existingLabels.includes(label.name)) {
      result.existing.push(label.name);
    } else {
      try {
        execFileSync('gh', [
          'label', 'create', label.name,
          '--description', 'devpace sync',
          '--color', label.color,
          '--repo', repo
        ], {
          encoding: 'utf-8',
          stdio: 'pipe'
        });
        result.created.push(label.name);
      } catch (error) {
        result.failed.push(label.name);
      }
    }
  }

  // 步骤 5: 确定最终状态
  if (result.failed.length > 0) {
    result.status = 'partial';
  }

  // 步骤 6: 输出结果
  console.log(JSON.stringify(result));
  process.exit(0);
}

main();

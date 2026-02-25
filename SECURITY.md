# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.4.x   | ✅ Full support |
| 1.3.x   | 🔧 Security fixes only |
| < 1.3   | ❌ Not supported |

## Reporting a Vulnerability

**Please use [GitHub Private Vulnerability Reporting](https://github.com/arch-team/devpace/security/advisories/new)** to report security issues.

Do **not** open a public issue for security vulnerabilities.

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Scope

devpace runs inside the Claude Code sandbox and has a minimal attack surface:

- **File access**: Only reads/writes Markdown files in `.devpace/` project directory
- **No network**: Does not make network requests or connect to external services
- **No credentials**: Does not store, transmit, or process user credentials
- **No code execution**: Does not execute user code — only generates Markdown artifacts
- **Hook transparency**: All Hook scripts are open-source and auditable in the `hooks/` directory

## 安全策略

如果您发现安全漏洞，请通过 [GitHub 私密漏洞报告](https://github.com/arch-team/devpace/security/advisories/new) 提交。

请勿在公开 Issue 中报告安全问题。我们将在 48 小时内确认收到，并在 7 天内提供详细回复。

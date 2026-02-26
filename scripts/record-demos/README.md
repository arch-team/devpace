# Demo GIF Recording Guide

Record terminal demos using [VHS](https://github.com/charmbracelet/vhs) (recommended) or [asciinema](https://asciinema.org/).

## Prerequisites

```bash
# Install VHS (macOS)
brew install charmbracelet/tap/vhs

# Or install asciinema
brew install asciinema
```

## Recording with VHS

VHS uses `.tape` files to define scripted terminal recordings:

```bash
# Record GIF-1: /pace-init
vhs gif-1-pace-init.tape

# Record GIF-2: Natural language development
vhs gif-2-natural-language-dev.tape

# Record GIF-3: Cross-session restore
vhs gif-3-cross-session-restore.tape
```

## Before Recording

1. **Prepare a clean demo project**:
   ```bash
   mkdir /tmp/demo-project && cd /tmp/demo-project
   git init && echo '# My App' > README.md && git add . && git commit -m "init"
   ```

2. **Ensure devpace is installed**:
   ```bash
   claude --plugin-dir /path/to/devpace
   ```

3. **Terminal setup**:
   - Use a clean terminal profile (no custom prompts that might distract)
   - Set font size to 16pt+ for readability
   - Terminal width: 100 columns, height: 30 rows

## Output Targets

| GIF | File | Size Target | Embed Location |
|-----|------|-------------|----------------|
| GIF-1 | `demo-pace-init.gif` | < 2MB | README.md hero section |
| GIF-2 | `demo-natural-language.gif` | < 3MB | README.md "30-Second Experience" |
| GIF-3 | `demo-cross-session.gif` | < 2MB | README.md "Cross-session" section |

After recording, copy GIFs to `.github/` and update README.md image references.

## Tips

- Keep recordings short (15-30 seconds)
- Use `Type` with realistic speed (not too fast)
- Add `Sleep` pauses at key moments for viewers to read
- Test the tape file multiple times before final recording

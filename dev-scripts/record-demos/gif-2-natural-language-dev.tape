# GIF-2: Natural language development
# Duration target: 20-30 seconds
# Shows: "Help me implement X" → auto CR creation → quality check → done

Output demo-natural-language.gif

Set FontSize 18
Set Width 1100
Set Height 600
Set Theme "Catppuccin Mocha"
Set TypingSpeed 50ms
Set Padding 20

# Natural language request (no /command needed)
Type "Help me implement user authentication with JWT"
Enter
Sleep 2s

# Claude auto-creates a CR and starts working
# (Actual Claude responses will appear here)
# Template shows expected flow:

Sleep 3s

# Show Claude auto-running quality checks
# Gate 1: Code quality ✅
# Gate 2: Requirement alignment ✅

Sleep 3s

# Show pending review state
Type "# Claude auto-checked quality. Waiting for your approval."
Enter
Sleep 2s

# User approves
Type "approve"
Enter
Sleep 2s

# Done
Type "# Merged! Goal → Feature → Code — fully traced."
Enter
Sleep 2s

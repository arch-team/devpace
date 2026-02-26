# GIF-3: Cross-session context restore
# Duration target: 15-20 seconds
# Shows: New session → Claude auto-reports → zero re-explanation

Output demo-cross-session.gif

Set FontSize 18
Set Width 1100
Set Height 600
Set Theme "Catppuccin Mocha"
Set TypingSpeed 50ms
Set Padding 20

# Simulate opening a new Claude Code session
Type "claude"
Enter
Sleep 2s

# Claude automatically detects .devpace/ and reports
# (Actual response will vary)
# Expected: "Last session you were working on user auth..."

Sleep 4s

# Show the auto-context restoration
Type "# Claude knows exactly where we left off"
Enter
Sleep 1s

# Continue naturally
Type "continue with the auth module"
Enter
Sleep 3s

# Claude picks up right where it left off
Type "# Zero re-explanation. Zero manual context."
Enter
Sleep 2s

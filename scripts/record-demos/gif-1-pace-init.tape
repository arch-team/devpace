# GIF-1: /pace-init — Project initialization
# Duration target: 15-20 seconds
# Shows: One command → dialogue → .devpace/ generated

Output demo-pace-init.gif

Set FontSize 18
Set Width 1100
Set Height 600
Set Theme "Catppuccin Mocha"
Set TypingSpeed 60ms
Set Padding 20

# Start in a clean project
Type "cd /tmp/my-project && ls"
Enter
Sleep 500ms

# Show it's a regular project
Type "# A regular project — no devpace yet"
Enter
Sleep 1s

# Initialize devpace
Type "/pace-init"
Enter
Sleep 2s

# Simulate Claude's guided dialogue
# (In real recording, Claude will respond interactively)
# This tape is a template — adjust based on actual Claude responses

Sleep 3s

# Show the generated structure
Type "ls .devpace/"
Enter
Sleep 2s

# Highlight: zero-friction setup
Type "# Done! devpace is tracking your project"
Enter
Sleep 2s

#!/bin/bash
# Install codex-claude-handoff skill for both Codex and Claude Code
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="codex-claude-handoff"

echo "=== Installing Codex + Claude Handoff Skill ==="

# 1. Install for Codex
CODEX_SKILLS="$HOME/.codex/skills/$SKILL_NAME"
echo ""
echo "[1/3] Installing for Codex..."
if [ -d "$CODEX_SKILLS" ]; then
    echo "  Updating existing skill at $CODEX_SKILLS"
    cp "$SKILL_DIR/SKILL.md" "$CODEX_SKILLS/"
    cp -r "$SKILL_DIR/references" "$CODEX_SKILLS/" 2>/dev/null || true
    cp -r "$SKILL_DIR/scripts" "$CODEX_SKILLS/" 2>/dev/null || true
    cp -r "$SKILL_DIR/agents" "$CODEX_SKILLS/" 2>/dev/null || true
    cp "$SKILL_DIR/CLAUDE.md" "$CODEX_SKILLS/" 2>/dev/null || true
    cp -r "$SKILL_DIR/../docs" "$CODEX_SKILLS/" 2>/dev/null || true
else
    echo "  Creating skill at $CODEX_SKILLS"
    mkdir -p "$CODEX_SKILLS"
    cp "$SKILL_DIR/SKILL.md" "$CODEX_SKILLS/"
    cp -r "$SKILL_DIR/references" "$CODEX_SKILLS/"
    cp -r "$SKILL_DIR/scripts" "$CODEX_SKILLS/"
    cp -r "$SKILL_DIR/agents" "$CODEX_SKILLS/"
    cp "$SKILL_DIR/CLAUDE.md" "$CODEX_SKILLS/"
    cp -r "$SKILL_DIR/../docs" "$CODEX_SKILLS/"
fi
echo "  ✓ Codex skill installed"

# 2. Install for Claude Code (copy CLAUDE.md to project root)
echo ""
echo "[2/3] Claude Code instructions..."
echo "  To enable for Claude Code, copy CLAUDE.md to your project root:"
echo "    cp $CODEX_SKILLS/CLAUDE.md ./CLAUDE.md"
echo "  Or for all projects (Claude Code global config):"
echo "    cp $CODEX_SKILLS/CLAUDE.md ~/.claude/CLAUDE.md"

# 3. Project setup
echo ""
echo "[3/3] Project setup..."
echo "  In each project, run:"
echo "    mkdir -p specs handoff"
echo "    echo 'handoff/' >> .gitignore"
echo "    cp $CODEX_SKILLS/docs/AGENTS.md ./AGENTS.md"
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Usage:"
echo "  1. cd your-project"
echo "  2. Start Claude Code:   claude"
echo "  3. Say: '设计 XXX 功能，写 spec 和 plan-ready.json'"
echo "  4. After Claude finishes, start Codex: codex"
echo "  5. Say: '交接' or 'handoff' — skill auto-detects phase and acts"
echo ""
echo "Quick phase check (anytime):"
echo "  python3 $CODEX_SKILLS/scripts/check_phase.py"

#!/bin/bash
# Install both Codex Handoff skills
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_SKILLS="$HOME/.codex/skills"

echo "=== Installing Codex Handoff Skills ==="
echo ""

# Function to install a single skill
install_skill() {
    local skill_name="$1"
    local skill_src="$SCRIPT_DIR/$skill_name"
    local skill_dest="$CODEX_SKILLS/$skill_name"

    if [ ! -d "$skill_src" ]; then
        echo "  [SKIP] $skill_name not found at $skill_src"
        return
    fi

    echo "[$skill_name]"
    if [ -d "$skill_dest" ]; then
        echo "  Updating existing installation..."
        rm -rf "$skill_dest"
    fi

    mkdir -p "$skill_dest"
    cp "$skill_src/SKILL.md" "$skill_dest/"
    [ -d "$skill_src/agents" ] && cp -r "$skill_src/agents" "$skill_dest/"
    [ -d "$skill_src/scripts" ] && cp -r "$skill_src/scripts" "$skill_dest/"
    [ -d "$skill_src/references" ] && cp -r "$skill_src/references" "$skill_dest/"
    [ -f "$skill_src/CLAUDE.md" ] && cp "$skill_src/CLAUDE.md" "$skill_dest/"
    echo "  ✓ Installed to $skill_dest"
    echo ""
}

install_skill "codex-claude-handoff"
install_skill "codex-self-handoff"

# Claude Code instructions
echo "[Claude Code 配置]"
echo "  仅 codex-claude-handoff 需要："
echo "    项目级: cp $CODEX_SKILLS/codex-claude-handoff/CLAUDE.md ./CLAUDE.md"
echo "    全局:   cp $CODEX_SKILLS/codex-claude-handoff/CLAUDE.md ~/.claude/CLAUDE.md"
echo ""

# Project setup
echo "[项目初始化]"
echo "  在每个项目目录下运行："
echo "    mkdir -p specs handoff"
echo "    echo 'handoff/' >> .gitignore"
echo ""

echo "=== Installation Complete ==="
echo ""
echo "使用方法："
echo "  Codex + Claude Code 协同:  在 Codex 中说 '交接'"
echo "  Codex 自协同:              在 Codex 中说 '自交接'"
echo ""
echo "查相位:"
echo "  python3 $CODEX_SKILLS/codex-claude-handoff/scripts/check_phase.py"
echo "  python3 $CODEX_SKILLS/codex-self-handoff/scripts/check_phase.py"

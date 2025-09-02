# 👻 Casper Workflow Integration via MCP

This guide shows how to use the Casper workflow through the Haiven MCP Server so your AI tools (Cursor, VS Code, and other MCP-compatible apps) follow the same methodology.

## 🎯 TL;DR
- Tool: `get_casper_workflow`
- Modes: `share` (return content) (default) or `save` (write files)
- Sections: `explore`, `craft`, `polish`, `full` (default)

Quick examples:
- Cursor command: `casper` → executes the tool and assumes the Casper persona
- Cursor command with phase: `casper explore` → executes Casper in the exploration phase
- Cursor command to save rules to your current repo: `casper save to @my-repo` → writes casper-full.mdc under @my-repo/.cursor/rules
- Programmatic (MCP call): `get_casper_workflow()`
- One section (MCP): `get_casper_workflow({"section": "explore"})`
- Save (MCP): `get_casper_workflow({"mode": "save"})`

## 🚀 Quick Start
To use the tool
- Share (default): returns content to the LLM
  - `get_casper_workflow()`
  - `get_casper_workflow({"section": "craft"})`
- Save: writes files for your tool context
  - `get_casper_workflow({"mode": "save"})`
  - `get_casper_workflow({"mode": "save", "section": "polish"})`
Save targets (auto-detected unless you specify `tool_context`):
- Cursor → `.cursor/rules/` (creates `.mdc` files)
- VS Code → `.github/instructions/` (creates `.instructions.md` files)

Once saved, you can attach the file as `rules/instruction` for that chat and remove the mcp and work with casper using just the command `casper`.
Refer to your tool's documentation for more details.

## 🔁 Minimal Flow

```
Connect AI Tool → Call get_casper_workflow →
  ├─ share (default): returns content → use in prompts / rules
  └─ save: writes files → tool picks up persistent rules
```

## 📋 Sections at a Glance
- 🔍 Explore: analysis, UX flows, edge cases, approach selection
- 🎨 Craft: TDD cycles, quality checks, refactoring, commit practices
- ✨ Polish: validation, review prep, docs, PR readiness

## 🛠️ Short Examples
- Assistant reference:
  "Please follow the Casper methodology. Use get_casper_workflow to load the guidelines."

- Custom prompt:
  "You are following Casper. Fetch the workflow with get_casper_workflow, then guide me through Explore for: [story]."

## 🔧 Technical Notes
- Response shape:
```json
{
  "tool": "get_casper_workflow",
  "mode": "share",
  "section": "explore",
  "content": "# 🔍 Casper's Collaborative Exploration Phase...",
  "usage": "..",
  "sections_available": ["explore", "craft", "polish", "full"]
}
```
- Errors: descriptive messages, missing sections gracefully handled, errors logged

## 🎉 Benefits
- Consistency • Quality • Efficiency • Knowledge sharing • Flexibility

## 🆘 Troubleshooting (quick)
- Tool not found: ensure connectivity to haiven server and api-key is correct

## 📚 See Also
- [Main README](../README.md)
- [User Setup Guide](USER_SETUP_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)

---
*Casper integration ensures proven, consistent AI-assisted development.* 👻✨

## References
- [MCP](https://github.com/haiven/mcp)
- [VSCode](https://code.visualstudio.com/docs/copilot/customization/custom-instructions#_create-an-instructions-file)
- [Cursor](https://docs.cursor.com/en/context/rules#project-rules)
- [AmazonQ](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html#:~:text=In%20your%20IDE%2C%20open%20the,Save%20the%20file.)

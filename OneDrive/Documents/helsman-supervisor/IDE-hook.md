# hook the validator straight into VS Code so you get red squiggles + Problems panel errors and a one-click task to check reports.

## Here’s exactly what I added to the Helmsman package (it’s in the canvas):

1. a `schemas/supervision_report.schema.json` (the strict JSON Schema)
2. a `helmsman validate` CLI command that checks reports with `jsonschema`
3. VS Code workspace hooks you can drop into any project

## What you do on your side

1. install Helmsman with test/tui extras

```bash
pip install -e .[tui,streamlit,test]
```

2. in each supervised project, add `.vscode/settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": [
        "artifacts/reports/supervision_report.json",
        "artifacts/reports/supervision_report_*.json"
      ],
      "url": "./schemas/supervision_report.schema.json"
    }
  ]
}
```

Now VS Code will **inline-validate** those files automatically.

3. (Optional) add a task to run validation on demand
   Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate Helmsman report",
      "type": "shell",
      "command": "helmsman",
      "args": ["validate", "artifacts/reports/supervision_report_*.json"],
      "problemMatcher": {
        "owner": "helmsman",
        "fileLocation": ["absolute"],
        "pattern": {
          "regexp": "^(.*):([0-9]+):([0-9]+): (error|warning) (.*)$",
          "file": 1,
          "line": 2,
          "column": 3,
          "severity": 4,
          "message": 5
        }
      },
      "group": "test"
    }
  ]
}
```

Run via **Terminal → Run Task → Validate Helmsman report**. Any issues show up in the **Problems** panel.

4. (Nice to have) make each report self-describing
   If you include this in the JSON Helmsman emits:

```json
"$schema": "./schemas/supervision_report.schema.json",
"schema_version": "0.2.0"
```

VS Code validates even without the workspace mapping.

That’s it — you’ll get immediate feedback in VS Code while keeping a CLI validator for pipelines and agents. Want me to also wire Helmsman to automatically add `$schema` and `schema_version` when writing reports?

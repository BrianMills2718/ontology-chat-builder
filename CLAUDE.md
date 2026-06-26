# ontology-chat-builder

Interactive tool for AI-assisted OWL ontology creation and visualization via WebVOWL.

## Scope

AI-driven ontology builder that generates OWL files from natural language descriptions.
Supports Anthropic (Claude) and OpenAI GPT. Visualization via WebVOWL (Docker).

## Key Commands

```bash
make help          # Show all targets
python ontology_builder.py   # Run CLI builder
jupyter notebook ontology_builder.ipynb  # Notebook mode
docker-compose up  # Start WebVOWL visualization server
```

## Notes

- OWL files go to `./output/` (create if missing)
- WebVOWL served on port 8080 by default
- API keys via environment variables (Anthropic: `ANTHROPIC_API_KEY`, OpenAI: `OPENAI_API_KEY`)

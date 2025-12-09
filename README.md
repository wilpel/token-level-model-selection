# Token-Level Model Selection

Generate text by switching between large and small language models at the token level.

## The Idea

Big language models are powerful, but expensive. Small models are fast and cheap, but weaker in reasoning. Instead of choosing between the two: **use both at the same time.**

Let the big model guide the direction of the text, and let the small model step in for a portion of the tokens once the structure is established.

## Why This Works

Generating a complete, coherent answer is hard. But predicting the next token in an already-coherent stream is easy.

When the big model writes the first chunk of a response, it:
- **Chooses a structure**: Is this a list? A narrative? A direct answer?
- **Sets the tone**: Formal? Casual? Technical?
- **Establishes key terms**: What vocabulary and concepts are introduced?
- **Creates momentum**: Where is this going?

All of these decisions get embedded in the context. So when the small model steps in for token 47, it doesn't need to make any of those decisions—they've already been made. The small model just needs to answer: given all of this, what's the most likely next token?

It's the difference between asking someone to write an essay and asking them to complete a sentence. The second task is dramatically easier.

## Usage

Requires [Ollama](https://ollama.ai/) running locally.

```bash
# Install
git clone https://github.com/wilpel/token-level-model-selection.git
cd token-level-model-selection
python3 -m venv venv
source venv/bin/activate
pip install requests

# Pull models
ollama pull gemma3:4b
ollama pull gemma3:270m

# Run
python3 ask.py "What is AI?"
```

### Options

```bash
python3 ask.py "What is AI?" \
  --big gemma3:4b \          # Big model (default: gemma3:4b)
  --small gemma3:270m \      # Small model (default: gemma3:270m)
  -r 0.5 \                   # Use small model every 2nd token
  --min-tokens 15 \          # Use big model for first 15 tokens
  -m 300                     # Max tokens to generate
```

### Examples

```bash
# 50% small model tokens (every 2nd token)
python3 ask.py "Explain quantum computing" -r 0.5

# 33% small model tokens (every 3rd token)
python3 ask.py "Write a poem about rain" -r 0.33

# Baseline (100% big model)
python3 ask.py "What is gravity?" -r 0
```

### Output Colors

- **Light blue** = Initial tokens (big model only, establishing structure)
- **White** = Big model
- **Red** = Small model

## Open Questions

- What's the minimum amount of "big model scaffolding" needed before the small model can take over? Is 15 tokens enough? 5? Does it depend on the task?
- Could you predict which tokens actually need the big model? Some tokens are obviously easy, but others might look simple while actually being pivotal.
- Could you build an adaptive version that calls the big model only when the small model is uncertain?

## License

MIT

#!/usr/bin/env python3
"""
Model Switching: Generate tokens using a mix of large and small models.

The idea: Use a large model for important tokens, small model for "filler" tokens.
Both models see full context - we're just switching which model generates each token.
"""

import argparse
import random
import json
import requests


def generate_token(prompt: str, model: str, temperature: float = 0.7) -> str:
    """Generate a single token from the given prompt."""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "raw": True,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": 1},
        },
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            return data.get("response", ""), data.get("done", False)
    return "", True


def generate(
    prompt: str,
    big_model: str = "gemma3:4b",
    small_model: str = "gemma3:270m",
    small_ratio: float = 0.5,
    max_tokens: int = 300,
    min_tokens_before_switch: int = 10,
    temperature: float = 0.7,
):
    """
    Generate text by switching between big and small models.

    Args:
        prompt: The question/instruction
        big_model: Main model for important tokens
        small_model: Faster model for filler tokens
        small_ratio: Probability of using small model (0.0-1.0)
        max_tokens: Maximum tokens to generate
        min_tokens_before_switch: Always use big model for first N tokens
        temperature: Sampling temperature
    """
    context = f"Question: {prompt}\n\nAnswer:"
    generated = ""
    small_count = 0

    # Calculate interval: if ratio=0.5, use small every 2nd token; ratio=0.33, every 3rd
    small_interval = int(1 / small_ratio) if small_ratio > 0 else 0

    for i in range(max_tokens):
        # Decide which model to use (deterministic: every Nth token after min_tokens)
        tokens_since_start = i - min_tokens_before_switch
        use_small = (
            i >= min_tokens_before_switch
            and small_interval > 0
            and tokens_since_start >= 0
            and tokens_since_start % small_interval == 0
        )

        model = small_model if use_small else big_model
        if use_small:
            small_count += 1

        # Generate token
        full_prompt = context + generated
        token, done = generate_token(full_prompt, model, temperature)

        if done or not token:
            break

        # Print token (light blue = initial, red = small model, white = big model)
        if i < min_tokens_before_switch:
            print(f"\033[94m{token}\033[0m", end="", flush=True)  # Light blue for initial
        elif use_small:
            print(f"\033[91m{token}\033[0m", end="", flush=True)  # Red for small
        else:
            print(token, end="", flush=True)  # White for big

        generated += token

    print()
    return generated, i + 1, small_count


def main():
    parser = argparse.ArgumentParser(
        description="Generate text using a mix of large and small models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ask.py "What is AI?"
  python3 ask.py "Explain gravity" --small-ratio 0.7
  python3 ask.py "Write a poem" --big gemma3:4b --small gemma3:270m
        """
    )
    parser.add_argument("question", nargs="?", help="Your question")
    parser.add_argument("--big", default="gemma3:4b", help="Big model (default: gemma3:4b)")
    parser.add_argument("--small", default="gemma3:270m", help="Small model (default: gemma3:270m)")
    parser.add_argument("--small-ratio", "-r", type=float, default=0.5, help="Ratio of small model tokens (default: 0.5)")
    parser.add_argument("--max-tokens", "-m", type=int, default=300, help="Max tokens (default: 300)")
    parser.add_argument("--min-tokens", type=int, default=10, help="Min tokens before switching (default: 10)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (default: 0.7)")

    args = parser.parse_args()

    if args.question:
        question = args.question
    else:
        question = input("Question: ")

    print(f"\n[big={args.big}, small={args.small}, ratio={args.small_ratio}]\n")

    generated, total_tokens, small_count = generate(
        question,
        big_model=args.big,
        small_model=args.small,
        small_ratio=args.small_ratio,
        max_tokens=args.max_tokens,
        min_tokens_before_switch=args.min_tokens,
        temperature=args.temperature,
    )

    print(f"\n---")
    print(f"Tokens: {total_tokens} | Big: {total_tokens - small_count} | Small: {small_count} ({small_count/total_tokens:.0%})")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from .data_generation import build_dataset, validate_dataset
from .heavy_data import generate_heavy_dataset, heavy_data_stats, validate_heavy_dataset
from .retrieval import build_index, create_embedding
from .retrieval_eval import evaluate_retrieval
from .runner import compare_runs, resolve_config, run_benchmark

ROOT = Path(__file__).resolve().parents[1]


def _add_embedding_options(parser: argparse.ArgumentParser, defaults: bool = True) -> None:
    parser.add_argument("--embed-model", default="bge-m3" if defaults else None)
    parser.add_argument("--embed-backend", choices=["ollama", "openai"], default="ollama" if defaults else None)
    parser.add_argument("--embed-base-url")
    parser.add_argument("--embed-api-key")
    parser.add_argument("--query-prefix", default="" if defaults else None)
    parser.add_argument("--passage-prefix", default="" if defaults else None)
    parser.add_argument("--cache-db", type=Path, default=Path(".cache/retrieval.sqlite3") if defaults else None)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m bench", description="Local LLM control-evaluation benchmark")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate-data", help="Create the original mock dataset if absent")
    generate.add_argument("--force", action="store_true", help="Replace base mock data")
    heavy = commands.add_parser("generate-heavy-data", help="Generate deterministic M/L/XL variants")
    heavy.add_argument("--seed", type=int, default=1729)
    heavy.add_argument("--bytes-per-token", type=int, default=4)
    heavy.add_argument("--force", action="store_true")

    validate = commands.add_parser("validate-data", help="Validate a dataset and its evidence references")
    validate.add_argument("--dataset", choices=["base", "heavy"], default="base")
    stats = commands.add_parser("data-stats", help="Summarize cases, token estimates, and files")
    stats.add_argument("--dataset", choices=["base", "heavy"], default="heavy")

    run = commands.add_parser("run", help="Run full-context or retrieval-assisted evaluations")
    run.add_argument("--config", type=Path, help="YAML settings file")
    run.add_argument("--backend", choices=["ollama", "openai"])
    run.add_argument("--model")
    run.add_argument("--base-url")
    run.add_argument("--api-key")
    run.add_argument("--temperature", type=float)
    run.add_argument("--seed", type=int)
    run.add_argument("--num-ctx", type=str, help="Ollama context size or auto")
    run.add_argument("--max-output-tokens", type=int)
    run.add_argument("--keep-alive")
    run.add_argument("--prompt-version")
    run.add_argument("--query-version")
    run.add_argument("--split", choices=["dev", "test", "all"])
    run.add_argument("--output-language")
    run.add_argument("--repeat", type=int)
    run.add_argument("--limit", type=int)
    run.add_argument("--dataset", choices=["base", "heavy"])
    run.add_argument("--context-mode", choices=["full", "retrieval"])
    run.add_argument("--retriever", choices=["dense", "bm25", "hybrid"])
    run.add_argument("--tier", choices=["S", "M", "L", "XL", "all"])
    run.add_argument("--control")
    run.add_argument("--status", help="Comma-separated expected statuses")
    run.add_argument("--max-minutes", type=float)
    run.add_argument("--case-timeout", type=float)
    run.add_argument("--resume", help="Existing run id or runs/<id> path")
    run.add_argument("--dry-run", action="store_true", default=None)
    run.add_argument("--assume-prompt-tps", type=float)
    run.add_argument("--assume-gen-tps", type=float)
    run.add_argument("--num-ctx-auto-margin", type=int)
    run.add_argument("--no-prompt-cache", dest="no_prompt_cache", action="store_true", default=None)
    run.add_argument("--allow-prompt-cache", dest="no_prompt_cache", action="store_false", default=None)
    _add_embedding_options(run, defaults=False)
    run.add_argument("--chunk-tokens", type=int)
    run.add_argument("--overlap", type=int)
    run.add_argument("--top-k", type=int)
    run.add_argument("--context-token-budget", type=int)
    run.add_argument("--context-order", choices=["file", "score"])

    index = commands.add_parser("index", help="Chunk and embed dataset evidence into the local SQLite cache")
    index.add_argument("--dataset", choices=["base", "heavy"], default="base")
    _add_embedding_options(index)
    index.add_argument("--chunk-tokens", type=int, default=400)
    index.add_argument("--overlap", type=int, default=60)

    retrieval = commands.add_parser("eval-retrieval", help="Measure evidence retrieval without calling an LLM")
    retrieval.add_argument("--dataset", choices=["base", "heavy"], default="base")
    retrieval.add_argument("--retriever", choices=["dense", "bm25", "hybrid"], default="hybrid")
    retrieval.add_argument("--top-k", type=int, default=8)
    retrieval.add_argument("--chunk-tokens", type=int, default=400)
    retrieval.add_argument("--overlap", type=int, default=60)
    retrieval.add_argument("--context-token-budget", type=int, default=4000)
    retrieval.add_argument("--limit", type=int)
    retrieval.add_argument("--sweep", action="store_true")
    retrieval.add_argument("--query-version", default="query_v1")
    _add_embedding_options(retrieval)

    compare = commands.add_parser("compare", help="Compare completed run directories")
    compare.add_argument("run_dirs", nargs="+", type=Path)
    compare.add_argument("--output", type=Path, help="Destination markdown file (default: comparison.md)")
    return parser


def _print_stats(stats: dict[str, Any]) -> None:
    print(f"Cases: {stats['cases']} | Files: {stats['total_files']} | Estimated evidence tokens: {stats['total_estimated_tokens']:,}")
    for title, key in (("Tier", "by_tier"), ("Control", "by_control"), ("Status", "by_status"), ("Language", "by_language")):
        print(f"\n{title}: cases / tokens / files")
        for name, row in sorted(stats[key].items()):
            print(f"  {name:28s} {row['cases']:4d} / {row['tokens']:10,d} / {row['files']:5d}")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "generate-data":
            count = build_dataset(ROOT, force=args.force)
            print(f"Validated {count} base mock cases in {ROOT / 'data'}.")
            return 0
        if args.command == "generate-heavy-data":
            count = generate_heavy_dataset(ROOT, args.seed, args.force, args.bytes_per_token)
            print(f"Validated {count} heavy mock cases. Dataset hash: generated separately from base.")
            return 0
        if args.command == "validate-data":
            count = validate_dataset(ROOT) if args.dataset == "base" else validate_heavy_dataset(ROOT)
            print(f"Data validation passed: {count} {args.dataset} cases; all control and evidence references exist.")
            return 0
        if args.command == "data-stats":
            if args.dataset == "base":
                count = validate_dataset(ROOT)
                labels = yaml.safe_load((ROOT / "data" / "labels.yaml").read_text(encoding="utf-8"))
                print(f"Base dataset: {count} cases; use `validate-data --dataset base` for full reference checks.")
                for status in sorted({row['expected_status'] for row in labels}):
                    print(f"  {status}: {sum(row['expected_status'] == status for row in labels)}")
            else:
                _print_stats(heavy_data_stats(ROOT))
            return 0
        if args.command == "run":
            override_map = {"backend": args.backend, "model": args.model, "base_url": args.base_url,
                            "api_key": args.api_key, "temperature": args.temperature, "seed": args.seed,
                            "num_ctx": args.num_ctx, "max_output_tokens": args.max_output_tokens,
                            "keep_alive": args.keep_alive, "prompt_version": args.prompt_version,
                            "query_version": args.query_version,
                            "split": args.split, "output_language": args.output_language,
                            "repeat": args.repeat, "limit": args.limit, "dataset": args.dataset,
                            "context_mode": args.context_mode, "retriever": args.retriever, "tier": args.tier,
                            "control": args.control, "status": args.status, "max_minutes": args.max_minutes,
                            "case_timeout": args.case_timeout, "resume": args.resume, "dry_run": args.dry_run,
                            "assume_prompt_tps": args.assume_prompt_tps, "assume_gen_tps": args.assume_gen_tps,
                            "num_ctx_auto_margin": args.num_ctx_auto_margin, "no_prompt_cache": args.no_prompt_cache,
                            "embed_model": args.embed_model, "embed_backend": args.embed_backend,
                            "embed_base_url": args.embed_base_url, "embed_api_key": args.embed_api_key,
                            "query_prefix": args.query_prefix, "passage_prefix": args.passage_prefix,
                            "cache_db": str(args.cache_db) if args.cache_db else None, "chunk_tokens": args.chunk_tokens,
                            "overlap": args.overlap, "top_k": args.top_k,
                            "context_token_budget": args.context_token_budget, "context_order": args.context_order}
            config = resolve_config(args.config, override_map)
            run_dir = run_benchmark(ROOT, config)
            if run_dir:
                print(f"Run complete: {run_dir}")
                print(f"Report: {run_dir / 'report.md'}")
            return 0
        if args.command == "index":
            config = vars(args).copy()
            config["cache_db"] = ROOT / args.cache_db
            embedding = create_embedding(config)
            info = build_index(ROOT, args.dataset, embedding, config["cache_db"], args.chunk_tokens, args.overlap)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return 0
        if args.command == "eval-retrieval":
            config = vars(args).copy()
            config["cache_db"] = ROOT / args.cache_db
            embedding = None if args.retriever == "bm25" and not args.sweep else create_embedding(config)
            output = evaluate_retrieval(ROOT, args.dataset, embedding, config["cache_db"], args.retriever,
                                        args.top_k, args.chunk_tokens, args.overlap,
                                        args.context_token_budget, args.limit, args.sweep, args.query_version)
            print(f"Retrieval report: {output}")
            return 0
        if args.command == "compare":
            for path in args.run_dirs:
                if not (path / "metrics.json").exists():
                    raise ValueError(f"Run is missing metrics.json: {path}")
            output = compare_runs(args.run_dirs, args.output)
            print(f"Comparison report: {output}")
            return 0
    except (OSError, ValueError, yaml.YAMLError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

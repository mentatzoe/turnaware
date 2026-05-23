"""Command-line interface for TurnAware."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .core import evaluate
from .errors import (
    EXIT_INPUT,
    EXIT_RUNTIME,
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    InputError,
    TurnAwareError,
    ValidationError,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="turnaware")
    subparsers = parser.add_subparsers(dest="command", required=True)
    admit = subparsers.add_parser("admit", help="evaluate one admission request")
    admit.add_argument("--input", "-i", metavar="PATH", help="read admission request JSON from a file")
    return parser


def _read_input(path: str | None) -> str:
    if path is None:
        return sys.stdin.read()

    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"could not read input file {path!r}: {exc.strerror}") from exc


def _load_request(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON: {exc.msg}") from exc


def _write_error(error: TurnAwareError) -> None:
    print(f"{error.label}: {error}", file=sys.stderr)


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command != "admit":
            raise InputError(f"unsupported command: {args.command}")
        raw = _read_input(args.input)
        request = _load_request(raw)
        result = evaluate(request)
    except InputError as exc:
        _write_error(exc)
        return EXIT_INPUT
    except ValidationError as exc:
        _write_error(exc)
        return EXIT_VALIDATION
    except TurnAwareError as exc:
        _write_error(exc)
        return EXIT_RUNTIME

    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return EXIT_SUCCESS

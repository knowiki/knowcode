"""Tree-sitter grammar registry.

Loads and caches tree-sitter language grammars.
"""

from __future__ import annotations

import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript

from structural_engine.parser.models import Language

_REGISTRY: dict[Language, tree_sitter.Language] = {}

def get_language(lang: Language) -> tree_sitter.Language:
    """Get the tree-sitter Language object for a given supported language.

    Parameters
    ----------
    lang : Language
        The language to load.

    Returns
    -------
    tree_sitter.Language
        The compiled tree-sitter language.
    """
    if lang in _REGISTRY:
        return _REGISTRY[lang]

    ts_lang = None
    if lang == Language.PYTHON:
        ts_lang = tree_sitter.Language(tree_sitter_python.language())
    elif lang == Language.JAVASCRIPT:
        ts_lang = tree_sitter.Language(tree_sitter_javascript.language())
    elif lang == Language.TYPESCRIPT:
        ts_lang = tree_sitter.Language(tree_sitter_typescript.language_typescript())
    else:
        raise ValueError(f"Unsupported language: {lang}")

    _REGISTRY[lang] = ts_lang
    return ts_lang

def get_parser(lang: Language) -> tree_sitter.Parser:
    """Create a new tree-sitter parser for the given language.

    Parameters
    ----------
    lang : Language
        The language to parse.

    Returns
    -------
    tree_sitter.Parser
        A configured parser instance.
    """
    ts_lang = get_language(lang)
    parser = tree_sitter.Parser(ts_lang)
    return parser

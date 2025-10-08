"""Talon grammar for tree-sitter"""

import json
from pathlib import Path
from tree_sitter import Language, Parser
from tree_sitter_type_provider import TreeSitterTypeProvider
from tree_sitter_type_provider.node_types import NodeType

from ._binding import language

# Load node types
_node_types_path = Path(__file__).parent / "node-types.json"
with open(_node_types_path) as f:
    _data = json.load(f)

_node_types = [NodeType.from_json(json.dumps(entry)) for entry in _data]

# Create the TreeSitterTypeProvider module
_dynamic_module = TreeSitterTypeProvider(
    module_name="tree_sitter_talon._internal.dynamic",
    node_types=_node_types,
    extra=("comment",),
    as_class_name=lambda name: "Talon" + "".join(word.capitalize() for word in name.split("_")),
)

# Get language
_lang_ptr = language()
_lang = Language(_lang_ptr, "talon")
_dynamic_module.language = _lang

# Create parser
_parser = Parser()
_parser.set_language(_lang)
_dynamic_module.parser = _parser

# Create parse functions
def parse(source: str, encoding: str = "utf-8", raise_parse_error: bool = False):
    """Parse Talon source code and return typed AST."""
    tree = _parser.parse(source.encode(encoding))
    result = _dynamic_module.from_tree_sitter(tree, encoding=encoding)

    # Check for parse errors if requested
    if raise_parse_error and tree.root_node.has_error:
        raise ParseError(f"Parse error in source code")

    return result

def parse_file(path: str, encoding: str = "utf-8"):
    """Parse Talon file and return typed AST."""
    with open(path, encoding=encoding) as f:
        return parse(f.read(), encoding=encoding)

_dynamic_module.parse = parse
_dynamic_module.parse_file = parse_file

# Export key items
from_tree_sitter = _dynamic_module.from_tree_sitter

# Get all the Talon* node classes and other exports from the dynamic module
_exports = [name for name in dir(_dynamic_module) if not name.startswith('_')]
for _name in _exports:
    globals()[_name] = getattr(_dynamic_module, _name)

# Base Node class - check if it exists in dynamic module, otherwise provide fallback
if hasattr(_dynamic_module, 'Node'):
    Node = _dynamic_module.Node
else:
    # Use the base node type from tree-sitter-type-provider
    from tree_sitter_type_provider import Node

# Import ParseError from tree-sitter-type-provider
from tree_sitter_type_provider import ParseError

################################################################################
# Add helper methods to node classes
################################################################################

from typing import Optional, Sequence
from tree_sitter_type_provider import Point, NodeTypeName

# Helper to merge comments into block
def _TalonBlock_with_comments(self, comments: Optional[Sequence]) -> "TalonBlock":
    return TalonBlock(
        text=self.text,
        type_name=self.type_name,
        start_position=self.start_position,
        end_position=self.end_position,
        children=[*(comments or ()), *self.children],
    )

# Custom __init__ for TalonCommandDeclaration to merge comments
def _TalonCommandDeclaration___init__(self, text: str, type_name: NodeTypeName, start_position: Point, end_position: Point, children: Optional[Sequence], left, right) -> None:
    self.text = text
    self.type_name = type_name
    self.start_position = start_position
    self.end_position = end_position
    self.children = None
    self.left = left
    self.right = _TalonBlock_with_comments(right, children)

setattr(TalonCommandDeclaration, "__init__", _TalonCommandDeclaration___init__)

# Custom __init__ for TalonKeyBindingDeclaration
def _TalonKeyBindingDeclaration___init__(self, text: str, type_name: NodeTypeName, start_position: Point, end_position: Point, children: Optional[Sequence], left, right) -> None:
    self.text = text
    self.type_name = type_name
    self.start_position = start_position
    self.end_position = end_position
    self.children = None
    self.left = left
    self.right = _TalonBlock_with_comments(right, children)

setattr(TalonKeyBindingDeclaration, "__init__", _TalonKeyBindingDeclaration___init__)

# Custom __init__ for TalonSettingsDeclaration
def _TalonSettingsDeclaration___init__(self, text: str, type_name: NodeTypeName, start_position: Point, end_position: Point, children: Optional[Sequence], left, right) -> None:
    self.text = text
    self.type_name = type_name
    self.start_position = start_position
    self.end_position = end_position
    self.children = None
    self.left = left
    self.right = _TalonBlock_with_comments(right, children)

setattr(TalonSettingsDeclaration, "__init__", _TalonSettingsDeclaration___init__)

# Method to test if a matches block is explicit
def _TalonMatches_is_explicit(self) -> bool:
    return self.text == "-" or self.text.endswith("\n-")

setattr(TalonMatches, "is_explicit", _TalonMatches_is_explicit)

# Methods to test if declarations are short
def _TalonBlock_is_short(self) -> bool:
    return len(self.children) <= 1

setattr(TalonBlock, "is_short", _TalonBlock_is_short)

def _TalonCommandDeclaration_is_short(self) -> bool:
    return self.right.is_short()

setattr(TalonCommandDeclaration, "is_short", _TalonCommandDeclaration_is_short)

def _TalonSettingsDeclaration_is_short(self) -> bool:
    return self.right.is_short()

setattr(TalonSettingsDeclaration, "is_short", _TalonSettingsDeclaration_is_short)

def _TalonKeyBindingDeclaration_is_short(self) -> bool:
    return self.right.is_short()

setattr(TalonKeyBindingDeclaration, "is_short", _TalonKeyBindingDeclaration_is_short)

__all__ = ["language", "parse", "parse_file", "Node", "ParseError", "from_tree_sitter"] + _exports

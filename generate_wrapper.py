#!/usr/bin/env python3
"""
Generate Python wrapper with tree-sitter-type-provider
"""
import json
import sys
from pathlib import Path
from tree_sitter import Language, Parser
from tree_sitter_type_provider import TreeSitterTypeProvider
from tree_sitter_type_provider.node_types import NodeType

# Load node types
with open('src/node-types.json') as f:
    data = json.load(f)

node_types = [NodeType.from_json(json.dumps(entry)) for entry in data]

# Create the internal package structure
internal_dir = Path("bindings/python/tree_sitter_talon/_internal")
internal_dir.mkdir(parents=True, exist_ok=True)

# Create __init__.py for _internal
(internal_dir / "__init__.py").write_text("")

# Load the compiled language
sys.path.insert(0, str(Path("bindings/python").absolute()))
from tree_sitter_talon._binding import language as language_fn
lang_ptr = language_fn()
lang = Language(lang_ptr, "talon")

# Create the TreeSitterTypeProvider module
dynamic_module = TreeSitterTypeProvider(
    module_name="tree_sitter_talon._internal.dynamic",
    node_types=node_types,
    extra=("comment",),
    as_class_name=lambda name: "Talon" + "".join(word.capitalize() for word in name.split("_")),
)

# Add language, parser, and parse functions
dynamic_module.language = lang

parser = Parser()
parser.set_language(lang)
dynamic_module.parser = parser

def parse(source: str, encoding: str = "utf-8") -> dynamic_module.TalonSourceFile:  # type: ignore
    tree = parser.parse(source.encode(encoding))
    return dynamic_module.from_tree_sitter(tree, encoding=encoding)  # type: ignore

def parse_file(path: str, encoding: str = "utf-8") -> dynamic_module.TalonSourceFile:  # type: ignore
    with open(path, encoding=encoding) as f:
        return parse(f.read(), encoding=encoding)

dynamic_module.parse = parse
dynamic_module.parse_file = parse_file
dynamic_module.from_tree_sitter = dynamic_module.from_tree_sitter  # type: ignore

print(f"✓ Generated wrapper with {len(node_types)} node types")
print(f"✓ Module attributes: {len([name for name in dir(dynamic_module) if not name.startswith('_')])}")

# Test it
test_code = "-\\ngamepad(dpad_left): print('test')"
result = parse(test_code)
print(f"✓ Test parse succeeded: {type(result)}")
print(f"✓ Has gamepad_declaration: {hasattr(dynamic_module, 'TalonGamepadDeclaration')}")

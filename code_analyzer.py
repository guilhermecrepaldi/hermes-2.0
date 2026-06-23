"""Hermes Code Analyzer — AST-based code understanding.
Deep understanding of code structure, dependencies, and quality.
Like Claude Code's codebase awareness.
"""
from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    name: str
    line: int
    end_line: int
    args: List[str] = field(default_factory=list)
    returns: str = ""
    docstring: str = ""
    complexity: int = 0
    calls: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    line: int
    methods: List[FunctionInfo] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class ImportInfo:
    module: str
    names: List[str] = field(default_factory=list)
    line: int = 0


@dataclass
class FileAnalysis:
    path: str
    name: str
    lines: int = 0
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    complexity_total: int = 0
    docstring_coverage: float = 0.0


@dataclass
class Dependency:
    source: str
    target: str
    type: str  # import | call | inherit | use


class CodeAnalyzer:
    """Deep code analysis using AST parsing.

    Understands:
    - Classes, functions, methods, imports
    - Dependency graphs between files
    - Code complexity (cyclomatic)
    - Docstring coverage
    - Impact of changes
    """

    def __init__(self, root: Optional[str] = None):
        self.root = Path(root or os.getcwd()).resolve()
        self.files: Dict[str, FileAnalysis] = {}
        self.dependencies: List[Dependency] = []
        self._analyzed = False

    def analyze(self) -> None:
        """Analyze all Python files in the project."""
        logger.info(f"Analyzing code in {self.root.name}")

        for py_file in sorted(self.root.rglob("*.py")):
            if self._should_skip(py_file):
                continue
            try:
                analysis = self._analyze_file(py_file)
                self.files[str(py_file.relative_to(self.root))] = analysis
            except Exception as e:
                logger.debug(f"Failed to analyze {py_file.name}: {e}")

        self._build_dependency_graph()
        self._analyzed = True
        logger.info(f"Analyzed {len(self.files)} files")

    def _should_skip(self, path: Path) -> bool:
        skip_dirs = {"__pycache__", ".git", ".venv", "venv",
                     "node_modules", "dist", "build", ".pytest_cache"}
        return any(p.name in skip_dirs for p in path.parents)

    def _analyze_file(self, path: Path) -> FileAnalysis:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        analysis = FileAnalysis(
            path=str(path.relative_to(self.root)),
            name=path.name,
            lines=len(lines),
        )

        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as e:
            analysis.errors.append(f"Syntax error: {e.msg}")
            return analysis

        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis.imports.append(ImportInfo(
                        module=alias.name,
                        names=[alias.asname or alias.name],
                        line=node.lineno,
                    ))

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                analysis.imports.append(ImportInfo(
                    module=module,
                    names=names,
                    line=node.lineno,
                ))

            # Functions
            elif isinstance(node, ast.FunctionDef):
                func = self._analyze_function(node, text)
                analysis.functions.append(func)
                analysis.complexity_total += func.complexity

            # Classes
            elif isinstance(node, ast.ClassDef):
                cls = self._analyze_class(node, text)
                analysis.classes.append(cls)
                for method in cls.methods:
                    analysis.complexity_total += method.complexity

        # Docstring coverage
        total = len(analysis.functions) + len(analysis.classes)
        with_docs = sum(1 for f in analysis.functions if f.docstring)
        with_docs += sum(1 for c in analysis.classes if c.docstring)
        analysis.docstring_coverage = (with_docs / max(total, 1)) * 100

        return analysis

    def _analyze_function(self, node: ast.FunctionDef, text: str) -> FunctionInfo:
        func = FunctionInfo(
            name=node.name,
            line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            args=[arg.arg for arg in node.args.args],
            returns=ast.unparse(node.returns) if node.returns else "",
            complexity=self._calc_complexity(node),
        )

        # Docstring
        doc = ast.get_docstring(node)
        if doc:
            func.docstring = doc[:100]

        # Function calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                func.calls.append(child.func.id)
            elif isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                func.calls.append(f"{ast.unparse(child.func)[:30]}")

        return func

    def _analyze_class(self, node: ast.ClassDef, text: str) -> ClassInfo:
        cls = ClassInfo(
            name=node.name,
            line=node.lineno,
            bases=[ast.unparse(b) for b in node.bases],
            docstring=ast.get_docstring(node) or "",
        )

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                cls.methods.append(self._analyze_function(item, text))

        return cls

    def _calc_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                  ast.Assert, ast.Raise)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _build_dependency_graph(self):
        """Build dependency graph between files."""
        file_map = {}
        for rel_path in self.files:
            name = Path(rel_path).stem
            file_map[name] = rel_path

        for rel_path, analysis in self.files.items():
            for imp in analysis.imports:
                # Check if imported module is a local file
                module_name = imp.module.split(".")[0]
                if module_name in file_map and file_map[module_name] != rel_path:
                    self.dependencies.append(Dependency(
                        source=rel_path,
                        target=file_map[module_name],
                        type="import",
                    ))

    def impact_analysis(self, file_path: str) -> dict:
        """Analyze what will be affected if file_path changes."""
        if not self._analyzed:
            self.analyze()

        affected = []
        for dep in self.dependencies:
            if dep.target == file_path or dep.source == file_path:
                affected.append({
                    "file": dep.source if dep.target == file_path else dep.target,
                    "relationship": dep.type,
                    "direction": "incoming" if dep.target == file_path else "outgoing",
                })

        analysis = self.files.get(file_path)

        return {
            "file": file_path,
            "affected_count": len(affected),
            "affected_files": affected,
            "has_errors": len(analysis.errors) > 0 if analysis else False,
            "complexity": analysis.complexity_total if analysis else 0,
            "docstring_coverage": f"{analysis.docstring_coverage:.0f}%" if analysis else "0%",
            "lines": analysis.lines if analysis else 0,
        }

    def get_project_stats(self) -> dict:
        """Get comprehensive project statistics."""
        if not self._analyzed:
            self.analyze()

        total_classes = sum(len(f.classes) for f in self.files.values())
        total_functions = sum(len(f.functions) for f in self.files.values())
        total_lines = sum(f.lines for f in self.files.values())
        total_imports = sum(len(f.imports) for f in self.files.values())
        total_errors = sum(len(f.errors) for f in self.files.values())
        total_complexity = sum(f.complexity_total for f in self.files.values())

        # Average docstring coverage
        coverages = [f.docstring_coverage for f in self.files.values() if f.lines > 0]
        avg_coverage = sum(coverages) / max(len(coverages), 1)

        # Top complex files
        complex_files = sorted(
            [(p, f.complexity_total) for p, f in self.files.items()],
            key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "files_analyzed": len(self.files),
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "total_imports": total_imports,
            "total_errors": total_errors,
            "total_complexity": total_complexity,
            "avg_complexity_per_file": total_complexity / max(len(self.files), 1),
            "avg_docstring_coverage": f"{avg_coverage:.0f}%",
            "dependencies": len(self.dependencies),
            "most_complex": [{"file": f, "complexity": c} for f, c in complex_files],
        }

    def find_function(self, name: str) -> List[dict]:
        """Find all functions by name (partial match)."""
        results = []
        for rel_path, analysis in self.files.items():
            for func in analysis.functions:
                if name.lower() in func.name.lower():
                    results.append({
                        "file": rel_path,
                        "function": func.name,
                        "line": func.line,
                        "args": func.args,
                        "complexity": func.complexity,
                    })
            for cls in analysis.classes:
                for method in cls.methods:
                    if name.lower() in method.name.lower():
                        results.append({
                            "file": rel_path,
                            "class": cls.name,
                            "method": method.name,
                            "line": method.line,
                            "complexity": method.complexity,
                        })
        return results

    def get_summary(self) -> str:
        """Human-readable project summary."""
        if not self._analyzed:
            self.analyze()

        stats = self.get_project_stats()

        lines = [
            f"=== Code Analysis: {self.root.name} ===",
            f"Files: {stats['files_analyzed']} ({stats['total_lines']} lines)",
            f"Classes: {stats['total_classes']} | Functions: {stats['total_functions']}",
            f"Dependencies: {stats['dependencies']}",
            f"Complexity: {stats['total_complexity']} total ({stats['avg_complexity_per_file']:.1f}/file)",
            f"Docstring coverage: {stats['avg_docstring_coverage']}",
            f"Syntax errors: {stats['total_errors']}",
        ]

        if stats['most_complex']:
            lines.append("\nMost complex files:")
            for m in stats['most_complex']:
                lines.append(f"  - {m['file']} (complexity: {m['complexity']})")

        return "\n".join(lines)

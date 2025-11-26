"""
Component Registry - Loads and manages component metadata
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class VariableSpec:
    """Specification for a component variable"""
    index: str  # Can be "10" or "10-12" for ranges
    name: str
    type: str
    unit: str
    description: str
    source: Optional[str] = None  # For inputs
    scope: Optional[str] = None  # For outputs
    required: Optional[bool] = None  # For parameters
    default: Optional[any] = None  # For parameters


@dataclass
class ComponentMetadata:
    """Complete metadata for a component"""
    name: str
    category: str
    dof: str
    description: str
    lifecycle: Dict[str, bool]
    inputs: List[VariableSpec] = field(default_factory=list)
    outputs: List[VariableSpec] = field(default_factory=list)
    parameters: List[VariableSpec] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    usage_example: str = ""
    notes: List[str] = field(default_factory=list)
    source_file: Optional[Path] = None


class ComponentRegistry:
    """Registry of all available CADAC components"""

    def __init__(self, components_dir: Optional[Path] = None):
        """
        Initialize the component registry

        Args:
            components_dir: Path to components directory (defaults to ../components)
        """
        if components_dir is None:
            # Default to components directory relative to this file
            self.components_dir = Path(__file__).parent.parent / 'components'
        else:
            self.components_dir = Path(components_dir)

        self.components: Dict[str, ComponentMetadata] = {}
        self._load_all_components()

    def _load_all_components(self):
        """Load all component INDEX.md files"""
        index_files = list(self.components_dir.glob('**/INDEX.md'))

        for index_file in index_files:
            self._load_index_file(index_file)

    def _load_index_file(self, index_file: Path):
        """Load a single INDEX.md file (may contain multiple components)"""
        content = index_file.read_text()

        # Split by component entries
        component_entries = re.split(r'\n---\n', content)

        for entry in component_entries:
            if not entry.strip():
                continue

            metadata = self._parse_component_entry(entry, index_file)
            if metadata and metadata.name:
                self.components[metadata.name] = metadata

    def _parse_component_entry(self, entry: str, source_file: Path) -> Optional[ComponentMetadata]:
        """Parse a single component entry from INDEX.md"""
        # Extract YAML block
        yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', entry, re.DOTALL)
        if not yaml_match:
            return None

        try:
            data = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML in {source_file}: {e}")
            return None

        if not data or 'component' not in data:
            return None

        comp = data['component']
        metadata = ComponentMetadata(
            name=comp.get('name', ''),
            category=comp.get('category', ''),
            dof=str(comp.get('dof', '')),
            description=comp.get('description', ''),
            lifecycle=data.get('lifecycle', {}),
            dependencies=data.get('dependencies', {}),
            usage_example=data.get('usage_example', ''),
            notes=data.get('notes', []),
            source_file=source_file
        )

        # Parse inputs
        for inp in data.get('inputs', []):
            metadata.inputs.append(VariableSpec(
                index=str(inp.get('index', '')),
                name=inp.get('name', ''),
                type=inp.get('type', ''),
                unit=inp.get('unit', ''),
                description=inp.get('description', ''),
                source=inp.get('source')
            ))

        # Parse outputs
        for out in data.get('outputs', []):
            metadata.outputs.append(VariableSpec(
                index=str(out.get('index', '')),
                name=out.get('name', ''),
                type=out.get('type', ''),
                unit=out.get('unit', ''),
                description=out.get('description', ''),
                scope=out.get('scope')
            ))

        # Parse parameters
        for param in data.get('parameters', []):
            metadata.parameters.append(VariableSpec(
                index=str(param.get('index', '')),
                name=param.get('name', ''),
                type=param.get('type', ''),
                unit=param.get('unit', ''),
                description=param.get('description', ''),
                required=param.get('required', False),
                default=param.get('default')
            ))

        return metadata

    def get(self, name: str) -> Optional[ComponentMetadata]:
        """Get component metadata by name"""
        return self.components.get(name)

    def list_all(self) -> List[str]:
        """List all available component names"""
        return sorted(self.components.keys())

    def list_by_category(self, category: str) -> List[str]:
        """List all components in a category"""
        return sorted([
            name for name, meta in self.components.items()
            if meta.category.lower() == category.lower()
        ])

    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return sorted(set(meta.category for meta in self.components.values()))

    def find_by_dof(self, dof: str) -> List[str]:
        """Find components that support a specific DoF (3, 6, or 3/6)"""
        results = []
        for name, meta in self.components.items():
            if dof in meta.dof or meta.dof == f"{dof}DoF" or (dof == "3/6" and meta.dof in ["3DoF", "6DoF", "3/6"]):
                results.append(name)
        return sorted(results)

    def check_dependencies(self, component_name: str) -> Dict[str, List[str]]:
        """Get dependency information for a component"""
        meta = self.get(component_name)
        if not meta:
            return {}
        return meta.dependencies

    def __repr__(self) -> str:
        return f"ComponentRegistry({len(self.components)} components)"

    def __str__(self) -> str:
        lines = [f"CADAC Component Registry ({len(self.components)} components)"]
        for category in self.get_categories():
            comps = self.list_by_category(category)
            lines.append(f"\n{category} ({len(comps)}):")
            for comp in comps:
                lines.append(f"  - {comp}")
        return '\n'.join(lines)

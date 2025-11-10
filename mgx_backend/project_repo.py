"""Project repository management."""

import os
import aiofiles
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FileRepository(BaseModel):
    """Manage files in a directory."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    path: Path
    
    def __init__(self, path: str | Path):
        super().__init__(path=Path(path))
        self.path.mkdir(parents=True, exist_ok=True)
    
    @property
    def all_files(self) -> List[str]:
        """Get all files in this repository."""
        if not self.path.exists():
            return []
        return [str(f.relative_to(self.path)) for f in self.path.rglob("*") if f.is_file()]
    
    async def save(self, filename: str, content: str):
        """Save content to a file."""
        filepath = self.path / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def read(self, filename: str) -> Optional[str]:
        """Read content from a file."""
        filepath = self.path / filename
        if not filepath.exists():
            return None
        
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            return await f.read()
    
    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        return (self.path / filename).exists()


class DocRepository(BaseModel):
    """Manage documentation files."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    prd: FileRepository
    system_design: FileRepository
    tasks: FileRepository
    
    def __init__(self, root: Path):
        docs_path = root / "docs"
        super().__init__(
            prd=FileRepository(docs_path / "prd"),
            system_design=FileRepository(docs_path / "system_design"),
            tasks=FileRepository(docs_path / "tasks"),
        )
    
    @property
    def all_files(self) -> List[str]:
        """Get all documentation files."""
        files = []
        files.extend([f"prd/{f}" for f in self.prd.all_files])
        files.extend([f"system_design/{f}" for f in self.system_design.all_files])
        files.extend([f"tasks/{f}" for f in self.tasks.all_files])
        return files


class ProjectRepo(BaseModel):
    """Manage project repository structure."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    workdir: Path
    docs: DocRepository
    srcs: FileRepository
    
    def __init__(self, root: str | Path):
        root_path = Path(root)
        root_path.mkdir(parents=True, exist_ok=True)
        
        super().__init__(
            workdir=root_path,
            docs=DocRepository(root_path),
            srcs=FileRepository(root_path / "src"),
        )
    
    def __str__(self) -> str:
        docs_files = self.docs.all_files
        src_files = self.srcs.all_files
        
        return (
            f"ProjectRepo({self.workdir})\n"
            f"  Docs: {len(docs_files)} files\n"
            f"    {docs_files[:5]}\n"
            f"  Srcs: {len(src_files)} files\n"
            f"    {src_files[:5]}"
        )
    
    async def save_prd(self, content: str):
        """Save PRD document."""
        await self.docs.prd.save("prd.md", content)
    
    async def save_design(self, content: str):
        """Save system design document."""
        await self.docs.system_design.save("system_design.md", content)
    
    async def save_code_files(self, code_content: str):
        """Parse and save code files from LLM output."""
        # Parse the code content
        files = self._parse_code_files(code_content)
        
        if not files:
            print(f"⚠️  Warning: No files parsed from code content. Content length: {len(code_content)}")
            print(f"   First 500 chars: {code_content[:500]}")
            return
        
        print(f"📁 Parsed {len(files)} files from code content")
        
        for filepath, content in files.items():
            try:
                # Normalize file path: remove leading slashes and convert absolute paths to relative
                filepath = filepath.lstrip('/')
                
                # Remove project name from path if it appears at the start
                # e.g., "/2048-game/index.html" -> "index.html" or "2048-game/index.html" -> "index.html"
                project_name = self.workdir.name
                if filepath.startswith(f"{project_name}/"):
                    filepath = filepath[len(project_name) + 1:]
                
                # Determine if it's a source file or other file
                if filepath.startswith("src/"):
                    await self.srcs.save(filepath[4:], content)
                    print(f"   ✅ Saved: src/{filepath[4:]}")
                else:
                    # Save to root
                    file_path = self.workdir / filepath
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(content)
                    print(f"   ✅ Saved: {filepath}")
            except Exception as e:
                print(f"   ❌ Error saving {filepath}: {e}")
                raise
    
    def _parse_code_files(self, content: str) -> dict:
        """Parse code files from LLM output."""
        files = {}
        lines = content.split('\n')
        
        current_file = None
        current_content = []
        in_file = False
        
        # Try multiple parsing strategies
        for line in lines:
            # Strategy 1: FILE: prefix
            if line.startswith('FILE:'):
                # Save previous file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line.replace('FILE:', '').strip()
                current_content = []
                in_file = False
                
            # Strategy 2: Markdown code blocks with file paths
            elif line.startswith('```') and current_file is None:
                # Check if next line contains a file path
                continue
            elif line.strip().startswith('//') or line.strip().startswith('#'):
                # Skip comments that might look like file paths
                if not in_file:
                    continue
                    
            elif line.strip() == '---':
                in_file = not in_file
                
            elif in_file and current_file:
                current_content.append(line)
            elif current_file and not in_file:
                # If we have a current_file but not in_file, we might be between markers
                # Try to detect if this is the start of file content
                if line.strip() and not line.strip().startswith('FILE:'):
                    in_file = True
                    current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
        
        # If no files found with FILE: format, try alternative parsing
        if not files:
            files = self._parse_code_files_alternative(content)
        
        return files
    
    def _parse_code_files_alternative(self, content: str) -> dict:
        """Alternative parsing strategy for code files."""
        files = {}
        
        # Look for markdown code blocks with language/file indicators
        import re
        
        # Pattern 1: ```language:path/to/file
        pattern1 = r'```(\w+):([^\n]+)\n(.*?)```'
        matches1 = re.findall(pattern1, content, re.DOTALL)
        for lang, filepath, code in matches1:
            files[filepath.strip()] = code.strip()
        
        # Pattern 2: File: path/to/file or # File: path/to/file
        pattern2 = r'(?:^|\n)(?:#\s*)?File:\s*([^\n]+)\n(.*?)(?=\n(?:File:|```|$))'
        matches2 = re.findall(pattern2, content, re.DOTALL | re.MULTILINE)
        for filepath, code in matches2:
            files[filepath.strip()] = code.strip()
        
        # Pattern 3: Look for common file extensions and assume structure
        if not files:
            # Try to find code blocks and infer file names from context
            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
            for i, (lang, code) in enumerate(code_blocks):
                if lang:
                    # Infer file name from language
                    ext_map = {
                        'javascript': 'index.js',
                        'js': 'index.js',
                        'typescript': 'index.ts',
                        'ts': 'index.ts',
                        'python': 'main.py',
                        'py': 'main.py',
                        'html': 'index.html',
                        'css': 'style.css',
                        'json': 'package.json',
                    }
                    filename = ext_map.get(lang.lower(), f'file{i+1}.{lang}')
                    files[filename] = code.strip()
        
        return files
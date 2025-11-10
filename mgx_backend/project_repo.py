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
        
        for filepath, content in files.items():
            # Determine if it's a source file or other file
            if filepath.startswith("src/"):
                await self.srcs.save(filepath[4:], content)
            else:
                # Save to root
                file_path = self.workdir / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
    
    def _parse_code_files(self, content: str) -> dict:
        """Parse code files from LLM output."""
        files = {}
        lines = content.split('\n')
        
        current_file = None
        current_content = []
        in_file = False
        
        for line in lines:
            if line.startswith('FILE:'):
                # Save previous file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line.replace('FILE:', '').strip()
                current_content = []
                in_file = False
                
            elif line.strip() == '---':
                in_file = not in_file
                
            elif in_file and current_file:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
        
        return files
"""Write Code action."""

from typing import Optional
from mgx_backend.action import Action


class WriteCode(Action):
    """Write complete, production-ready code."""
    
    name: str = "WriteCode"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing code."""
        return f"""You are a Senior Software Engineer. Based on the System Design below, write complete, production-ready code.

System Design Document:
{context}

CRITICAL INSTRUCTIONS:
- Output ONLY code files in the specified format below
- DO NOT add any explanatory text, comments, or descriptions outside of code blocks
- DO NOT write sentences like "This is a basic setup" or "We'd also need to..."
- DO NOT add notes or explanations after code blocks
- ONLY output the FILE: markers and code content
- Code comments inside files are allowed and encouraged

Please write the complete implementation including:

1. **All Source Code Files**
   - Write every file mentioned in the design
   - Include complete, working code (no placeholders or TODOs)
   - Follow best practices and coding standards
   - Add appropriate comments INSIDE the code files

2. **File Structure**
   - Organize files according to the design
   - Create a clear directory structure

3. **Configuration Files**
   - Package.json, requirements.txt, or equivalent
   - Configuration files (if needed)
   - Environment setup files

4. **Documentation Files**
   - README.md with setup instructions (as a code file)
   - Code documentation (as comments in code files)

5. **Code Quality**
   - Clean, readable code
   - Proper error handling
   - Input validation
   - Security best practices

OUTPUT FORMAT (STRICT - NO DEVIATIONS):
```
FILE: path/to/file1.ext
---
[complete file content - ONLY code, no explanations]
---

FILE: path/to/file2.ext
---
[complete file content - ONLY code, no explanations]
---
```

IMPORTANT:
- Start directly with FILE: markers
- End after the last file's closing markers
- Do NOT add any text after the last file
- Do NOT explain what the code does outside of code comments
- Do NOT write sentences like "This is..." or "We need to..." after code blocks

Make sure every file is complete and functional. The code should be ready to run."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteCode action."""
        prompt = self.build_prompt(context)
        code = await self.llm.ask(prompt, stream_callback=stream_callback)
        return code
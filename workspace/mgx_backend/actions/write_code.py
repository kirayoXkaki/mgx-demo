"""Write Code action."""

from typing import Optional
from mgx_backend.action import Action


class WriteCode(Action):
    """Write complete, production-ready code."""
    
    name: str = "WriteCode"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing code."""
        return f"""You are a Senior Software Engineer. Based on the System Design below, write complete, production-ready code with FULL APPLICATION IMPLEMENTATION.

System Design Document:
{context}

CRITICAL INSTRUCTIONS:
- Output ONLY code files in the specified format below
- DO NOT add any explanatory text, comments, or descriptions outside of code blocks
- DO NOT write sentences like "This is a basic setup" or "We'd also need to..."
- DO NOT add notes or explanations after code blocks
- ONLY output the FILE: markers and code content
- Code comments inside files are allowed and encouraged

MOST IMPORTANT - APPLICATION IMPLEMENTATION:
You MUST implement the COMPLETE, WORKING APPLICATION, not just the architecture framework.

For example:
- If building a game: Implement the FULL game logic, game loop, rendering, input handling, scoring, win/lose conditions
- If building a web app: Implement ALL pages, components, API endpoints, database operations, authentication, business logic
- If building a calculator: Implement ALL mathematical operations, UI interactions, error handling
- If building a todo app: Implement ALL CRUD operations, state management, persistence, UI interactions

DO NOT just create:
- Empty class definitions
- Placeholder functions
- Skeleton code without implementation
- Architecture-only code

INSTEAD, you MUST create:
- Complete, runnable application code
- Full business logic implementation
- All user interactions and features
- Working functionality that can be executed immediately

Please write the complete implementation including:

1. **All Source Code Files with FULL IMPLEMENTATION**
   - Write every file mentioned in the design
   - Include complete, working code with ALL functionality implemented
   - NO placeholders, NO TODOs, NO "// TODO: implement this"
   - Implement ALL functions, methods, and classes completely
   - Include ALL business logic, game logic, or application logic
   - Follow best practices and coding standards
   - Add appropriate comments INSIDE the code files

2. **File Structure**
   - Organize files according to the design
   - Create a clear directory structure

3. **Configuration Files**
   - Package.json, requirements.txt, or equivalent with ALL dependencies
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
[complete file content with FULL implementation - ONLY code, no explanations]
---

FILE: path/to/file2.ext
---
[complete file content with FULL implementation - ONLY code, no explanations]
---
```

IMPORTANT:
- Start directly with FILE: markers
- End after the last file's closing markers
- Do NOT add any text after the last file
- Do NOT explain what the code does outside of code comments
- Do NOT write sentences like "This is..." or "We need to..." after code blocks
- IMPLEMENT EVERYTHING - no placeholders, no stubs, no empty functions

Make sure every file is complete and functional. The code should be ready to run and the application should work immediately after installation."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteCode action."""
        prompt = self.build_prompt(context)
        code = await self.llm.ask(prompt, stream_callback=stream_callback)
        return code
"""Write Code action."""

from mgx_backend.action import Action


class WriteCode(Action):
    """Write complete, production-ready code."""
    
    name: str = "WriteCode"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing code."""
        return f"""You are a Senior Software Engineer. Based on the System Design below, write complete, production-ready code.

System Design Document:
{context}

Please write the complete implementation including:

1. **All Source Code Files**
   - Write every file mentioned in the design
   - Include complete, working code (no placeholders or TODOs)
   - Follow best practices and coding standards
   - Add appropriate comments

2. **File Structure**
   - Organize files according to the design
   - Create a clear directory structure

3. **Configuration Files**
   - Package.json, requirements.txt, or equivalent
   - Configuration files (if needed)
   - Environment setup files

4. **Documentation**
   - README.md with setup instructions
   - Code documentation
   - Usage examples

5. **Code Quality**
   - Clean, readable code
   - Proper error handling
   - Input validation
   - Security best practices

Please output the code in the following format:

```
FILE: path/to/file1.ext
---
[complete file content]
---

FILE: path/to/file2.ext
---
[complete file content]
---

... (continue for all files)
```

Make sure every file is complete and functional. The code should be ready to run after following the setup instructions."""
    
    async def run(self, context: str) -> str:
        """Execute WriteCode action."""
        prompt = self.build_prompt(context)
        code = await self.llm.ask(prompt)
        return code
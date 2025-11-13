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

MOST IMPORTANT - APPLICATION LOGIC IMPLEMENTATION:
You MUST implement the COMPLETE, WORKING APPLICATION with ALL game logic, not just the server framework or empty classes.

**For Games - YOU MUST IMPLEMENT:**
1. **Complete Game Logic Class/Module**:
   - Game state management class with ALL properties and methods
   - Game loop implementation (update() and render() methods with full logic)
   - Player movement logic (exact position calculation, direction handling, collision checking)
   - Enemy/NPC AI logic (complete AI algorithms, pathfinding, decision-making)
   - Collision detection functions (complete coordinate checking, bounding box logic)
   - Game mechanics (scoring, win/lose conditions, level progression)
   - Entity management (creation, update, destruction of all game objects)

2. **Game Loop Implementation**:
   - MUST have a working game loop (setInterval, requestAnimationFrame, or similar)
   - Each iteration MUST: process input, update game state, check collisions, render
   - MUST implement all update logic for all entities

3. **Game Logic Functions**:
   - Player movement: calculateNextPosition(), handleInput(), checkWallCollision()
   - Enemy AI: calculateEnemyPath(), updateEnemyPosition(), enemyDecisionLogic()
   - Collision: checkCollision(), handleCollision(), resolveCollision()
   - Game mechanics: updateScore(), checkWinCondition(), checkLoseCondition()
   - State management: initializeGame(), resetGame(), changeGameState()

4. **Data Structures**:
   - Game state object/class with ALL properties initialized
   - Player object with position, direction, speed, state, etc.
   - Enemy objects with positions, AI states, behaviors
   - Map/grid data structure with walls, paths, collectibles
   - All game entities as complete objects/classes

5. **DO NOT create**:
   - Empty class definitions with no methods
   - Placeholder functions like "// TODO: implement movement"
   - Skeleton code without implementation
   - Server routes without game logic
   - Database models without game state management

**For Web Applications - YOU MUST IMPLEMENT:**
- Complete business logic in service/controller layers
- All API endpoints with full request/response handling
- Complete data processing and transformation logic
- All user workflows and state transitions
- Form validation and error handling

**For Other Applications:**
- Complete core functionality algorithms
- All business rules and logic
- Complete data processing workflows
- All user interaction handlers

Please write the complete implementation including:

1. **All Source Code Files with FULL IMPLEMENTATION**
   - Write every file mentioned in the design
   - Include complete, working code with ALL functionality implemented
   - NO placeholders, NO TODOs, NO "// TODO: implement this"
   - Implement ALL functions, methods, and classes completely
   - Include ALL game logic, business logic, or application logic
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
- For games: MUST include complete game loop, movement logic, collision detection, AI, scoring, win/lose conditions
- For apps: MUST include complete business logic, workflows, data processing

Make sure every file is complete and functional. The code should be ready to run and the application should work immediately after installation. The game must be playable with all core mechanics working."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteCode action."""
        prompt = self.build_prompt(context)
        code = await self.llm.ask(prompt, stream_callback=stream_callback)
        return code
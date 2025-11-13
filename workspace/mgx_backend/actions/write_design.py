"""Write System Design action."""

from typing import Optional
from mgx_backend.action import Action


class WriteDesign(Action):
    """Write a System Design Document."""
    
    name: str = "WriteDesign"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing system design."""
        return f"""You are a Software Architect. Based on the PRD below, design a complete software system architecture WITH DETAILED APPLICATION LOGIC.

PRD (Product Requirements Document):
{context}

CRITICAL: This design document must include BOTH architecture AND detailed application logic implementation. Do NOT just describe the architecture framework - you MUST specify the actual game logic, business logic, algorithms, and implementation details.

Please write a detailed System Design Document that includes:

1. **Architecture Overview**
   - High-level architecture diagram (describe in text)
   - Architecture style (e.g., MVC, microservices, layered)
   - Key design principles

2. **Technology Stack**
   - Programming language(s)
   - Framework(s)
   - Database(s)
   - Third-party libraries and services
   - Justification for each choice

3. **System Components**
   - Frontend components
   - Backend components
   - Database schema
   - API design
   - Component interactions

4. **Data Models**
   - Entity definitions
   - Relationships
   - Data flow diagrams (describe in text)

5. **API Specifications**
   - RESTful endpoints (if applicable)
   - Request/response formats
   - Authentication/authorization

6. **File Structure**
   - Project directory structure
   - File organization
   - Module breakdown

7. **DETAILED APPLICATION LOGIC (MOST IMPORTANT - REQUIRED)**
   This section is CRITICAL and must be EXTREMELY detailed. This is NOT optional - you MUST include complete game logic design.
   
   **For Games (REQUIRED - Must include ALL of these):**
   - **Complete game mechanics and rules**: Detailed description of how the game works, step by step
   - **Game state management**: Exact data structures for game state, initial state values, all possible game states (waiting, playing, paused, gameOver, win), state transition conditions
   - **Game loop design**: Exact implementation of game loop - update cycle frequency, render cycle, what happens in each frame, timing mechanisms
   - **Core game algorithms with pseudocode**:
     * Collision detection algorithm (exact method, coordinate checking, bounding boxes)
     * Scoring system (how points are calculated, when points are awarded)
     * Win/lose conditions (exact conditions, how to check)
     * Movement algorithms (how entities move, pathfinding if needed)
   - **Player input handling**: Exact key/input mapping, input processing flow, how input affects game state
   - **Game entities and their behaviors**: 
     * For each entity (player, enemies, collectibles, obstacles): exact properties, behaviors, update logic
     * Entity lifecycle (creation, update, destruction)
     * Entity interactions (what happens when entities collide)
   - **Animation and rendering logic**: How sprites/visuals are updated, animation frames, rendering order
   - **Score calculation and progression**: Exact scoring rules, score display, high score tracking
   - **Level/mode management**: How levels are structured, level progression, difficulty scaling
   - **Specific game features implementation** (MUST be detailed):
     * For Pac-Man: Ghost AI algorithm (chase mode, scatter mode, frightened mode), exact pathfinding logic, pellet collection mechanics, power pellet effects and duration, fruit spawning, tunnel mechanics
     * For other games: All unique game mechanics with exact implementation details
   
   **For Web Applications:**
   - Complete business logic flows
   - User workflows and state transitions
   - Data processing algorithms
   - Feature-specific implementation logic
   - User interaction handlers
   - State management approach
   - Form validation and processing
   - Data transformation logic
   
   **For Other Applications:**
   - Core functionality algorithms
   - Business rules and logic
   - Data processing workflows
   - User interaction patterns
   - State management
   - Event handling logic

8. **Core Algorithms and Data Structures (REQUIRED)**
   - **Key algorithms with detailed pseudocode**: Every major algorithm must have step-by-step pseudocode
   - **Exact data structures**: Define exact data structures for:
     * Game state object/class with all properties
     * Player entity with all properties (position, direction, speed, state, etc.)
     * Enemy entities with all properties
     * Map/grid structure with exact representation
     * All game objects and their properties
   - **Algorithm implementations**: 
     * Movement algorithms (how to calculate next position)
     * Collision detection (exact coordinate checking logic)
     * AI algorithms (for enemies/NPCs - exact decision-making logic)
     * Game logic algorithms (scoring, win/lose checking, etc.)
   - **Performance considerations**: How algorithms are optimized
   - **Edge cases**: All edge cases and exact handling logic for each

9. **User Interface Logic**
   - UI component interactions
   - User input handling
   - Event flow and propagation
   - State updates triggered by user actions
   - Visual feedback mechanisms

10. **Implementation Plan**
    - Development phases
    - Component dependencies
    - Build order
    - Specific implementation steps for each feature

11. **Non-Functional Requirements**
    - Performance considerations
    - Scalability approach
    - Security measures
    - Error handling strategy

CRITICAL REMINDERS - YOU MUST FOLLOW THESE:
- **DO NOT just describe architecture** - you MUST specify the actual game logic implementation
- **DO NOT write vague descriptions** like "implement game loop" or "add collision detection"
- **DO write specific details** like "Game loop runs at 60 FPS, each frame: 1) process input, 2) update player position based on direction and speed, 3) update ghost positions using A* pathfinding, 4) check collisions between player and walls/ghosts/pellets, 5) render all entities"
- **For games**: You MUST include:
  * Exact game loop implementation (what happens in each iteration)
  * Exact collision detection algorithm (how coordinates are checked)
  * Exact movement algorithms (how entities calculate their next position)
  * Exact AI algorithms (how enemies make decisions, with pseudocode)
  * Exact game state management (all states, transitions, data structures)
  * Exact scoring/win/lose logic (when and how these are calculated)
- **Include pseudocode or step-by-step algorithms** for all major game logic
- **Specify exact data structures** - not just "game state object" but "game state object with properties: playerX, playerY, playerDirection, ghostPositions[], pelletGrid[][], score, lives, gameStatus"
- The design must be SPECIFIC enough that an engineer can implement the COMPLETE, WORKING GAME directly from this document WITHOUT needing to design the game logic themselves
- Describe HOW features work with exact implementation details, not just WHAT features exist
- Avoid any vague or abstract descriptions - every game mechanic must have concrete implementation details

Please be specific and technical. The design should be detailed enough for engineers to start coding immediately AND understand exactly how to implement the application logic.

Output the design document in markdown format."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteDesign action."""
        prompt = self.build_prompt(context)
        design = await self.llm.ask(prompt, stream_callback=stream_callback)
        return design
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

7. **DETAILED APPLICATION LOGIC (MOST IMPORTANT)**
   This section is CRITICAL and must be very detailed:
   
   **For Games:**
   - Complete game mechanics and rules
   - Game state management (initial state, game states, transitions)
   - Game loop design (update cycle, render cycle)
   - Core game algorithms (e.g., collision detection, scoring, win/lose conditions)
   - Player input handling and response
   - Game entities and their behaviors
   - Animation and rendering logic
   - Score calculation and progression
   - Level/mode management
   - Specific game features implementation (e.g., for Pac-Man: ghost AI, pellet collection, power-up mechanics)
   
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

8. **Core Algorithms and Data Structures**
   - Key algorithms used (with pseudocode or detailed description)
   - Data structures for game state, entities, etc.
   - Performance considerations for algorithms
   - Edge cases and how to handle them

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

IMPORTANT REMINDERS:
- The design must be SPECIFIC enough that an engineer can implement the COMPLETE, WORKING APPLICATION directly from this document
- Include concrete examples, algorithms, and logic flows
- Describe HOW features work, not just WHAT features exist
- For games: specify game rules, mechanics, and logic in detail
- For apps: specify business logic, workflows, and data processing in detail
- Avoid vague descriptions - be concrete and actionable

Please be specific and technical. The design should be detailed enough for engineers to start coding immediately AND understand exactly how to implement the application logic.

Output the design document in markdown format."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteDesign action."""
        prompt = self.build_prompt(context)
        design = await self.llm.ask(prompt, stream_callback=stream_callback)
        return design
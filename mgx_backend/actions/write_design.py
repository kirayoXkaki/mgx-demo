"""Write System Design action."""

from typing import Optional
from mgx_backend.action import Action


class WriteDesign(Action):
    """Write a System Design Document."""
    
    name: str = "WriteDesign"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing system design."""
        return f"""You are a Software Architect. Based on the PRD below, design a complete software system architecture.

PRD (Product Requirements Document):
{context}

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

7. **Implementation Plan**
   - Development phases
   - Component dependencies
   - Build order

8. **Non-Functional Requirements**
   - Performance considerations
   - Scalability approach
   - Security measures
   - Error handling strategy

Please be specific and technical. The design should be detailed enough for engineers to start coding immediately.

Output the design document in markdown format."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WriteDesign action."""
        prompt = self.build_prompt(context)
        design = await self.llm.ask(prompt, stream_callback=stream_callback)
        return design
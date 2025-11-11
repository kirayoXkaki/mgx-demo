"""Write Product Requirements Document action."""

from typing import Optional
from mgx_backend.action import Action


class WritePRD(Action):
    """Write a Product Requirements Document."""
    
    name: str = "WritePRD"
    
    def build_prompt(self, context: str) -> str:
        """Build prompt for writing PRD."""
        return f"""You are a Product Manager. Based on the user requirement below, write a comprehensive Product Requirements Document (PRD).

User Requirement:
{context}

Please write a detailed PRD that includes:

1. **Project Overview**
   - Brief description of the product
   - Target users
   - Core value proposition

2. **Goals and Objectives**
   - Primary goals
   - Success metrics
   - Key performance indicators

3. **Core Features**
   - List of main features
   - Feature priorities (Must-have, Should-have, Nice-to-have)
   - User stories for each feature

4. **Technical Requirements**
   - Platform requirements
   - Technology stack suggestions
   - Performance requirements
   - Security considerations

5. **User Interface Requirements**
   - UI/UX principles
   - Key user flows
   - Accessibility requirements

6. **Constraints and Assumptions**
   - Technical constraints
   - Business constraints
   - Assumptions made

7. **Timeline and Milestones**
   - Development phases
   - Key milestones
   - Estimated timeline

Please be specific, detailed, and actionable. The PRD should be clear enough for architects and engineers to understand what needs to be built.

Output the PRD in markdown format."""
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute WritePRD action."""
        prompt = self.build_prompt(context)
        prd = await self.llm.ask(prompt, stream_callback=stream_callback)
        return prd
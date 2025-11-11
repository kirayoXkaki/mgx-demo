"""Base role class."""

from typing import List, Set, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from mgx_backend.action import Action
from mgx_backend.message import Message
from mgx_backend.llm import BaseLLM


class Role(BaseModel):
    """Base class for all roles."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Role"
    profile: str = "Role"
    goal: str = ""
    constraints: str = ""
    
    actions: List[Action] = Field(default_factory=list)
    _watch: Set[str] = PrivateAttr(default_factory=set)
    _env: Optional[Any] = PrivateAttr(default=None)
    _llm: Optional[BaseLLM] = PrivateAttr(default=None)
    
    _news: List[Message] = PrivateAttr(default_factory=list)
    _todo: Optional[Action] = PrivateAttr(default=None)
    
    def set_actions(self, actions: List[type]):
        """Set actions for this role."""
        self.actions = [action() for action in actions]
    
    def set_env(self, env: Any):
        """Set environment."""
        self._env = env
        self._llm = env.context.llm()
        
        # Set LLM for all actions
        for action in self.actions:
            action.set_llm(self._llm)
    
    def watch(self, action_types: Set[str]):
        """Watch for specific action types."""
        self._watch = action_types
    
    async def observe(self, message: Message):
        """Observe a message."""
        # Check if this role should react to this message
        if not self._watch or message.cause_by in self._watch:
            self._news.append(message)
    
    @property
    def is_idle(self) -> bool:
        """Check if role is idle."""
        return len(self._news) == 0 and self._todo is None
    
    async def think(self) -> bool:
        """Decide what to do next."""
        if not self._news:
            return False
        
        # Send progress update: role is thinking
        if self._env and self._env.context:
            callback = self._env.context.kwargs.get("progress_callback")
            if callback:
                await callback({
                    "type": "thinking",
                    "role": self.name,
                    "stage": f"{self.name}: Thinking about next action...",
                    "message": f"{self.name} is analyzing requirements and deciding what to do next"
                })
        
        # Simple strategy: execute actions in order
        if self.actions:
            self._todo = self.actions[0]
            
            # Send progress update: role decided to act
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                if callback:
                    await callback({
                        "type": "action_start",
                        "role": self.name,
                        "action": self._todo.name,
                        "stage": f"{self.name}: Starting {self._todo.name}...",
                        "message": f"{self.name} is starting to {self._todo.name.lower().replace('write', 'write').replace('code', 'implement code')}"
                    })
            
            return True
        
        return False
    
    async def act(self) -> Message:
        """Execute current action."""
        if not self._todo:
            return None
        
        # Send progress update: action executing
        if self._env and self._env.context:
            callback = self._env.context.kwargs.get("progress_callback")
            if callback:
                await callback({
                    "type": "action_executing",
                    "role": self.name,
                    "action": self._todo.name,
                    "stage": f"{self.name}: Executing {self._todo.name}...",
                    "message": f"{self.name} is working on {self._todo.name.lower().replace('write', 'writing').replace('code', 'code implementation')}"
                })
        
        # Get context from news
        context = "\n".join([msg.content for msg in self._news])
        
        # Stream callback for real-time updates
        current_file = None
        current_content = {}
        accumulated_content = ""
        in_file_content = False
        last_update_time = {}
        last_chat_update_time = 0
        last_chat_update_length = 0
        last_file_update = {}
        
        async def stream_callback(chunk: str):
            """Handle streaming output from LLM."""
            nonlocal current_file, current_content, accumulated_content, in_file_content, last_update_time, last_chat_update_time, last_chat_update_length, last_file_update
            
            accumulated_content += chunk
            
            # Send chat message update (more frequent for better UX)
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                if callback:
                    import time
                    now = time.time()
                    content_length = len(accumulated_content)
                    # Update chat every 20 chars or 0.5 seconds
                    if (content_length - last_chat_update_length > 20 or 
                        now - last_chat_update_time > 0.5):
                        last_chat_update_time = now
                        last_chat_update_length = content_length
                        await callback({
                            "type": "stream_chunk",
                            "role": self.name,
                            "action": self._todo.name,
                            "chunk": chunk,
                            "accumulated": accumulated_content
                        })
            
            # Handle different action types
            if self._todo.name == "WriteCode":
                # Parse FILE: markers for code generation
                # Process accumulated content to find files
                lines = accumulated_content.split('\n')
                buffer = ""
                
                for i, line in enumerate(lines):
                    if line.startswith('FILE:'):
                        # Save previous file if exists
                        if current_file and current_content.get(current_file):
                            # Send final update for previous file
                            if self._env and self._env.context:
                                callback = self._env.context.kwargs.get("progress_callback")
                                if callback:
                                    await callback({
                                        "type": "file_content",
                                        "filepath": current_file,
                                        "content": current_content[current_file]
                                    })
                        
                        # New file detected
                        filepath = line.replace('FILE:', '').strip()
                        current_file = filepath
                        in_file_content = False
                        if filepath not in current_content:
                            current_content[filepath] = ""
                            import time
                            last_update_time[filepath] = time.time()
                            
                            # Send file update
                            if self._env and self._env.context:
                                callback = self._env.context.kwargs.get("progress_callback")
                                if callback:
                                    await callback({
                                        "type": "file_update",
                                        "role": self.name,
                                        "filepath": filepath,
                                        "action": "creating"
                                    })
                    elif current_file and line.strip() == '---':
                        # Toggle file content marker
                        in_file_content = not in_file_content
                    elif current_file and in_file_content:
                        # Accumulate file content
                        current_content[current_file] += line + '\n'
                        
                        # Send incremental file content update (more frequent: every 50 chars or 0.3 seconds)
                        import time
                        now = time.time()
                        last_update = last_file_update.get(current_file, 0)
                        content_length = len(current_content[current_file])
                        last_length = last_file_update.get(f"{current_file}_len", 0)
                        
                        # Update if 50+ chars added or 0.3+ seconds passed
                        if (content_length - last_length > 50 or now - last_update > 0.3):
                            last_file_update[current_file] = now
                            last_file_update[f"{current_file}_len"] = content_length
                            if self._env and self._env.context:
                                callback = self._env.context.kwargs.get("progress_callback")
                                if callback:
                                    await callback({
                                        "type": "file_content",
                                        "filepath": current_file,
                                        "content": current_content[current_file]
                                    })
            elif self._todo.name in ["WritePRD", "WriteDesign"]:
                # For PRD and Design, treat the entire content as a document file
                # Create a virtual file for the document
                doc_filename = "prd.md" if self._todo.name == "WritePRD" else "system_design.md"
                doc_path = f"docs/{doc_filename}"
                
                if doc_path not in current_content:
                    current_content[doc_path] = ""
                    import time
                    last_file_update[doc_path] = time.time()
                    last_file_update[f"{doc_path}_len"] = 0
                    
                    # Send file update
                    if self._env and self._env.context:
                        callback = self._env.context.kwargs.get("progress_callback")
                        if callback:
                            await callback({
                                "type": "file_update",
                                "role": self.name,
                                "filepath": doc_path,
                                "action": "creating"
                            })
                
                # Update document content in real-time
                current_content[doc_path] = accumulated_content
                
                # Send incremental updates (every 50 chars or 0.3 seconds)
                import time
                now = time.time()
                last_update = last_file_update.get(doc_path, 0)
                content_length = len(current_content[doc_path])
                last_length = last_file_update.get(f"{doc_path}_len", 0)
                
                if (content_length - last_length > 50 or now - last_update > 0.3):
                    last_file_update[doc_path] = now
                    last_file_update[f"{doc_path}_len"] = content_length
                    if self._env and self._env.context:
                        callback = self._env.context.kwargs.get("progress_callback")
                        if callback:
                            await callback({
                                "type": "file_content",
                                "filepath": doc_path,
                                "content": current_content[doc_path]
                            })
        
        # Execute action with streaming
        result = await self._todo.run(context, stream_callback=stream_callback)
        
        # Send final file contents for all actions
        if current_content:
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                if callback:
                    for filepath, content in current_content.items():
                        await callback({
                            "type": "file_complete",
                            "filepath": filepath,
                            "content": content
                        })
        
        # Send progress update: action completed
        if self._env and self._env.context:
            callback = self._env.context.kwargs.get("progress_callback")
            if callback:
                await callback({
                    "type": "action_complete",
                    "role": self.name,
                    "action": self._todo.name,
                    "stage": f"{self.name}: {self._todo.name} completed",
                    "message": f"{self.name} has completed {self._todo.name.lower()}"
                })
        
        # Create output message
        message = Message(
            content=result,
            role=self.name,
            cause_by=self._todo.name,
            sent_from=self.name
        )
        
        # Clear news and todo
        self._news = []
        self._todo = None
        
        return message
    
    async def run(self) -> Optional[Message]:
        """Run the role (think + act)."""
        if await self.think():
            message = await self.act()
            if message and self._env:
                await self._env.publish_message(message)
            return message
        return None
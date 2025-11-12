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
            
            # Send human-like chat message: explain what I'm going to do
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                print(f"🔍 [Role] think() - callback available: {callback is not None}, role={self.name}")
                if callback:
                    # Generate human-like introduction message
                    intro_message = self._generate_intro_message()
                    print(f"💬 [Role] Sending intro chat_message: role={self.name}, message={intro_message[:50]}...")
                    await callback({
                        "type": "chat_message",
                        "role": self.name,
                        "action": self._todo.name,
                        "stage": f"{self.name}: Starting {self._todo.name}...",
                        "message": intro_message
                    })
                    
                    # Also send action_start for compatibility
                    await callback({
                        "type": "action_start",
                        "role": self.name,
                        "action": self._todo.name,
                        "stage": f"{self.name}: Starting {self._todo.name}...",
                        "message": f"{self.name} is starting to {self._todo.name.lower().replace('write', 'write').replace('code', 'implement code')}"
                    })
            
            return True
        
        return False
    
    def _generate_intro_message(self) -> str:
        """Generate a human-like introduction message explaining what the role is about to do."""
        action_name = self._todo.name if self._todo else "work"
        
        # Map action names to human-readable descriptions
        action_descriptions = {
            "WritePRD": "编写产品需求文档（PRD）",
            "WriteDesign": "设计系统架构和技术方案",
            "WriteCode": "实现代码和功能"
        }
        
        action_desc = action_descriptions.get(action_name, action_name)
        
        # Generate personalized messages based on role
        if self.name == "Alice" or self.profile == "Product Manager":
            return f"👋 你好！我是 {self.name}，产品经理。\n\n我将开始{action_desc}，基于你的需求来规划产品的功能和特性。让我先分析一下需求，然后开始编写详细的产品需求文档。"
        elif self.name == "Bob" or self.profile == "Architect":
            return f"👋 你好！我是 {self.name}，系统架构师。\n\n我已经收到了产品需求文档，现在我将开始{action_desc}。我会设计系统的整体架构、技术选型、模块划分等，确保系统具有良好的可扩展性和可维护性。"
        elif self.name == "Charlie" or self.profile == "Engineer":
            return f"👋 你好！我是 {self.name}，软件工程师。\n\n我已经收到了系统设计文档，现在我将开始{action_desc}。我会根据架构设计实现具体的功能代码，确保代码质量和可运行性。"
        else:
            return f"👋 你好！我是 {self.name}。\n\n我将开始{action_desc}。"
    
    def _generate_completion_message(self, action_name: str = None) -> str:
        """Generate a human-like completion message and introduce the next team member."""
        if action_name is None:
            action_name = self._todo.name if self._todo else "work"
        
        # Find the next role that will be triggered by this action's output
        next_role = None
        if self._env:
            # Check which role watches for this action's output
            for role in self._env.get_roles():
                if role != self and hasattr(role, '_watch'):
                    if action_name in role._watch:
                        next_role = role
                        break
        
        # Generate completion message
        action_descriptions = {
            "WritePRD": "产品需求文档",
            "WriteDesign": "系统设计文档",
            "WriteCode": "代码实现"
        }
        
        action_desc = action_descriptions.get(action_name, action_name)
        
        if self.name == "Alice" or self.profile == "Product Manager":
            completion_msg = f"✅ 我已经完成了{action_desc}的编写。"
            if next_role:
                completion_msg += f"\n\n接下来，我会把文档交给 {next_role.name}（{next_role.profile}），由他/她来设计系统架构。"
            return completion_msg
        elif self.name == "Bob" or self.profile == "Architect":
            completion_msg = f"✅ 我已经完成了{action_desc}的设计。"
            if next_role:
                completion_msg += f"\n\n接下来，我会把设计文档交给 {next_role.name}（{next_role.profile}），由他/她来实现具体的代码。"
            return completion_msg
        elif self.name == "Charlie" or self.profile == "Engineer":
            completion_msg = f"✅ 我已经完成了{action_desc}的开发。"
            completion_msg += "\n\n🎉 项目已经完成！所有代码都已经生成并保存。"
            return completion_msg
        else:
            return f"✅ 我已经完成了{action_desc}。"
    
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
        
        # Initialize result to None to track if action completed
        result = None
        
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
            
            # Debug: log that stream_callback is being called
            if not hasattr(stream_callback, '_call_count'):
                stream_callback._call_count = 0
            stream_callback._call_count += 1
            if stream_callback._call_count <= 3:
                print(f"🔍 [Stream] stream_callback called #{stream_callback._call_count}, chunk length: {len(chunk)}, action: {self._todo.name}")
                print(f"   progress_callback available: {self._env.context.kwargs.get('progress_callback') is not None if self._env and self._env.context else False}")
            
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
                # Debug: log first few chunks to see what we're receiving
                if len(accumulated_content) < 1000 and not hasattr(stream_callback, '_debug_logged'):
                    print(f"🔍 [Stream] WriteCode first {len(accumulated_content)} chars: {accumulated_content[:500]}")
                    stream_callback._debug_logged = True
                
                # Helper function to normalize file path (same logic as project_repo.py)
                def normalize_filepath(filepath: str) -> str:
                    """Normalize file path to match saved path."""
                    # Remove leading slashes
                    filepath = filepath.lstrip('/')
                    
                    # Remove project name from path if it appears at the start
                    if self._env and self._env.context:
                        project_name = getattr(self._env.context.config.project, 'project_name', None)
                        if project_name and filepath.startswith(f"{project_name}/"):
                            filepath = filepath[len(project_name) + 1:]
                    
                    # IMPORTANT: Always add src/ prefix for code files
                    if not filepath.startswith("src/"):
                        filepath = f"src/{filepath}"
                    
                    return filepath
                
                # Parse FILE: markers for code generation
                # IMPORTANT: Check ALL complete lines in accumulated_content, not just new lines
                # This handles cases where FILE: marker is split across chunks
                all_lines = accumulated_content.split('\n')
                
                # Track which FILE: lines we've already processed
                if not hasattr(stream_callback, '_processed_file_lines'):
                    stream_callback._processed_file_lines = set()
                
                # Debug: log FILE: markers found
                file_markers = [line for line in all_lines if line.startswith('FILE:')]
                if file_markers and not hasattr(stream_callback, '_file_markers_logged'):
                    print(f"🔍 [Stream] WriteCode total FILE: markers in accumulated_content: {len(file_markers)}")
                    print(f"   First few: {file_markers[:5]}")
                    stream_callback._file_markers_logged = True
                
                # Find all complete FILE: lines (those that end with \n or are not the last line)
                for i, line in enumerate(all_lines):
                    # Only process complete lines (not the last line if content doesn't end with \n)
                    is_complete = False
                    if i < len(all_lines) - 1:
                        # Not the last line, so it's complete
                        is_complete = True
                    elif accumulated_content.endswith('\n'):
                        # Last line but content ends with \n, so it's complete
                        is_complete = True
                    
                    # Only process complete FILE: lines we haven't seen before
                    if is_complete and line.startswith('FILE:') and line not in stream_callback._processed_file_lines:
                        stream_callback._processed_file_lines.add(line)
                        
                        # Debug log
                        if len(stream_callback._processed_file_lines) <= 5:
                            print(f"🔍 [Stream] WriteCode found complete FILE: line: {repr(line)}")
                        
                        # Extract filepath
                        raw_filepath = line.replace('FILE:', '').strip()
                        
                        # Skip if filepath is empty (incomplete FILE: marker)
                        if not raw_filepath:
                            print(f"⚠️  [Stream] Skipping incomplete FILE: line (no filepath): {repr(line)}")
                            continue
                        
                        # Normalize filepath
                        normalized_filepath = normalize_filepath(raw_filepath)
                        
                        # Save previous file if exists
                        if current_file and current_file != normalized_filepath and current_content.get(current_file):
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
                        current_file = normalized_filepath
                        in_file_content = True
                        
                        if normalized_filepath not in current_content:
                            current_content[normalized_filepath] = ""
                            import time
                            last_update_time[normalized_filepath] = time.time()
                            last_file_update[normalized_filepath] = time.time()
                            last_file_update[f"{normalized_filepath}_len"] = 0
                            
                            # Send file update
                            if self._env and self._env.context:
                                callback = self._env.context.kwargs.get("progress_callback")
                                if callback:
                                    print(f"📝 [Stream] New file detected: {normalized_filepath}")
                                    try:
                                        await callback({
                                            "type": "file_update",
                                            "role": self.name,
                                            "filepath": normalized_filepath,
                                            "action": "creating"
                                        })
                                        print(f"   ✅ [Stream] Sent file_update for: {normalized_filepath}")
                                    except Exception as e:
                                        print(f"   ❌ [Stream] Error sending file_update: {e}")
                                        import traceback
                                        traceback.print_exc()
                
                # Now collect content for all detected files
                # Only process if we have new files or content changed significantly
                # Limit processing frequency to avoid performance issues
                if stream_callback._processed_file_lines:
                    import time
                    now = time.time()
                    
                    # Throttle: only process every 0.1 seconds or if we have new files
                    if not hasattr(stream_callback, '_last_content_process_time'):
                        stream_callback._last_content_process_time = 0
                    
                    new_files_detected = len(stream_callback._processed_file_lines) > len(current_content)
                    
                    if new_files_detected or (now - stream_callback._last_content_process_time > 0.1):
                        stream_callback._last_content_process_time = now
                        
                        import re
                        # Process each detected file (limit to avoid performance issues)
                        processed_count = 0
                        for processed_line in stream_callback._processed_file_lines:
                            if processed_count > 10:  # Limit to 10 files per chunk to avoid blocking
                                break
                            
                            if not processed_line.startswith('FILE:'):
                                continue
                            
                            raw_filepath = processed_line.replace('FILE:', '').strip()
                            if not raw_filepath:
                                continue
                            
                            normalized_filepath = normalize_filepath(raw_filepath)
                            
                            # Extract content after this FILE: marker using regex
                            # Pattern: FILE: path\n(?:---\n)?(content)(?=\nFILE:|\Z)
                            escaped_marker = re.escape(processed_line)
                            pattern = re.compile(f'{escaped_marker}\\n(?:---\\n)?(.*?)(?=\\nFILE:|\\Z)', re.DOTALL)
                            match = pattern.search(accumulated_content)
                            
                            if match:
                                file_content_raw = match.group(1).strip()
                                # Clean up content (remove --- markers if present)
                                if file_content_raw.startswith('---'):
                                    file_content_raw = file_content_raw[3:].lstrip()
                                if file_content_raw.endswith('---'):
                                    file_content_raw = file_content_raw[:-3].rstrip()
                                
                                # Update current_content
                                if normalized_filepath not in current_content:
                                    current_content[normalized_filepath] = ""
                                    last_update_time[normalized_filepath] = time.time()
                                    last_file_update[normalized_filepath] = time.time()
                                    last_file_update[f"{normalized_filepath}_len"] = 0
                                
                                # Only send update if content changed significantly
                                old_content = current_content.get(normalized_filepath, "")
                                if file_content_raw != old_content:
                                    current_content[normalized_filepath] = file_content_raw
                                    
                                    # Send incremental update (every 50 chars or 0.3 seconds)
                                    last_update = last_file_update.get(normalized_filepath, 0)
                                    content_length = len(file_content_raw)
                                    last_length = last_file_update.get(f"{normalized_filepath}_len", 0)
                                    
                                    if (content_length - last_length > 50 or now - last_update > 0.3):
                                        last_file_update[normalized_filepath] = now
                                        last_file_update[f"{normalized_filepath}_len"] = content_length
                                        if self._env and self._env.context:
                                            callback = self._env.context.kwargs.get("progress_callback")
                                            if callback:
                                                try:
                                                    await callback({
                                                        "type": "file_content",
                                                        "filepath": normalized_filepath,
                                                        "content": file_content_raw
                                                    })
                                                    # Log first few updates per file
                                                    if not hasattr(stream_callback, '_logged_file_content'):
                                                        stream_callback._logged_file_content = set()
                                                    if normalized_filepath not in stream_callback._logged_file_content:
                                                        stream_callback._logged_file_content.add(normalized_filepath)
                                                        print(f"   📤 [Stream] Sent first file_content for: {normalized_filepath} ({content_length} chars)")
                                                except Exception as e:
                                                    print(f"   ❌ [Stream] Error sending file_content for {normalized_filepath}: {e}")
                                                    import traceback
                                                    traceback.print_exc()
                                
                                processed_count += 1
            elif self._todo.name in ["WritePRD", "WriteDesign"]:
                # For PRD and Design, treat the entire content as a document file
                # Create a virtual file for the document
                # Match the actual saved path structure
                if self._todo.name == "WritePRD":
                    doc_path = "docs/prd/prd.md"
                else:
                    doc_path = "docs/system_design/system_design.md"
                
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
        print(f"🔍 [Role] Executing {self._todo.name} with stream_callback")
        print(f"   progress_callback available: {self._env.context.kwargs.get('progress_callback') is not None if self._env and self._env.context else False}")
        print(f"   accumulated_content length before: {len(accumulated_content)}")
        
        try:
            result = await self._todo.run(context, stream_callback=stream_callback)
            print(f"✅ [Role] {self._todo.name} completed, result length: {len(result) if result else 0}")
            print(f"   accumulated_content length after: {len(accumulated_content)}")
            print(f"   current_content has {len(current_content)} files: {list(current_content.keys())}")
            if current_content:
                for filepath, content in current_content.items():
                    print(f"   - {filepath}: {len(content)} chars")
        except Exception as e:
            print(f"❌ [Role] {self._todo.name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            # Set result to empty string to prevent None error
            result = f"Error during {self._todo.name}: {str(e)}"
            # Send error notification
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                if callback:
                    await callback({
                        "type": "error",
                        "role": self.name,
                        "action": self._todo.name,
                        "error": str(e),
                        "message": f"{self.name} encountered an error during {self._todo.name.lower()}"
                    })
        
        # Send final file contents for all actions
        if current_content:
            if self._env and self._env.context:
                callback = self._env.context.kwargs.get("progress_callback")
                if callback:
                    print(f"📦 [Stream] Sending {len(current_content)} file(s) as complete")
                    for filepath, content in current_content.items():
                        # Normalize path for WriteCode files
                        if self._todo.name == "WriteCode":
                            def normalize_filepath(filepath: str) -> str:
                                filepath = filepath.lstrip('/')
                                if self._env and self._env.context:
                                    project_name = getattr(self._env.context.config.project, 'project_name', None)
                                    if project_name and filepath.startswith(f"{project_name}/"):
                                        filepath = filepath[len(project_name) + 1:]
                                return filepath
                            normalized_path = normalize_filepath(filepath)
                        else:
                            normalized_path = filepath
                        # Send file_complete message
                        print(f"   ✅ [Stream] File complete: {normalized_path} ({len(content)} chars)")
                        await callback({
                            "type": "file_complete",
                            "filepath": normalized_path,
                            "content": content
                        })
        
        
        # Save action name before clearing todo (needed for completion message)
        action_name = self._todo.name if self._todo else "action"
        
        # Send progress update: action completed
        if self._env and self._env.context:
            callback = self._env.context.kwargs.get("progress_callback")
            if callback:
                # Send completion message
                await callback({
                    "type": "action_complete",
                    "role": self.name,
                    "action": action_name,
                    "stage": f"{self.name}: {action_name} completed",
                    "message": f"{self.name} has completed {action_name.lower()}"
                })
                
                # Send human-like completion message and introduce next team member
                # Note: We need to call this before clearing _todo, so pass action_name
                completion_message = self._generate_completion_message(action_name)
                if completion_message:
                    print(f"💬 [Role] Sending completion chat_message: role={self.name}, message={completion_message[:50]}...")
                    await callback({
                        "type": "chat_message",
                        "role": self.name,
                        "action": action_name,
                        "stage": f"{self.name}: {action_name} completed",
                        "message": completion_message
                    })
        
        # Ensure result is not None (prevent errors)
        if result is None:
            result = ""
            print(f"⚠️  [Role] {action_name} returned None, using empty string")
        
        # Create output message
        message = Message(
            content=result,
            role=self.name,
            cause_by=action_name,
            sent_from=self.name
        )
        
        # Clear news and todo (IMPORTANT: Always clear to mark role as idle)
        self._news = []
        self._todo = None
        
        print(f"✅ [Role] {self.name} completed {action_name}, role is now idle")
        
        return message
    
    async def run(self) -> Optional[Message]:
        """Run the role (think + act)."""
        if await self.think():
            message = await self.act()
            if message and self._env:
                await self._env.publish_message(message)
            return message
        return None
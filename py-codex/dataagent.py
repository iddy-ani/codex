from flask import request, jsonify
import os
import threading
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import threading
from queue import Queue
import os
from core.agent import Agent
from config import AppConfig, load_config
from pathlib import Path
from openai.types.chat import ChatCompletionToolMessageParam
from core.instructions_manager import instructions_manager


class CodexSession:
    def __init__(self, session_id, config, working_directory=None):
        self.session_id = session_id
        self.working_directory = working_directory or Path.cwd()
        # Ensure working directory is a Path object
        if isinstance(self.working_directory, str):
            self.working_directory = Path(self.working_directory)
        
        # Get current custom instructions
        custom_instructions = instructions_manager.get_current_instructions()
        if custom_instructions:
            # Update config with custom instructions
            config = self._update_config_for_directory(config, self.working_directory)
            config['instructions'] = custom_instructions
            print(f"[Codex] Using custom instructions: {instructions_manager.get_selected_instruction()}")
        else:
            # Use default instructions if no custom instructions
            config = self._update_config_for_directory(config, self.working_directory)
            print("[Codex] Using default instructions")
        
        # *** PASS WORKING DIRECTORY TO AGENT ***
        self.agent = Agent(config, working_directory=self.working_directory)
        self.is_active = True
        self.message_queue = Queue()
        # Add these new attributes for tool handling
        self.pending_tool_calls = {}  # tool_call_id -> tool_call_object
        self.tool_results = {}  # tool_call_id -> result
        self.waiting_for_tools = False
        
        # print(f"[Codex] Session {session_id} initialized with working directory: {self.working_directory}")

    def _update_config_for_directory(self, config, working_dir):
        """Update the agent config to use the specified working directory"""
        # Make a copy of the config
        updated_config = config.copy()
        
        # Load project-specific configuration if it exists
        try:
            from config import load_config
            project_config = load_config(
                cwd=working_dir,
                disable_project_doc=False,
                project_doc_path=None,
                is_full_context=False,
                flex_mode=False,
                full_stdout=True,
            )
            
            # Merge project config with session config
            updated_config.update(project_config)
            # print(f"[Codex] Loaded project config from {working_dir}")
            
        except Exception as e:
            print(f"[Codex] Could not load project config from {working_dir}: {e}")
            # Use the original config if project config fails
        
        return updated_config

    async def process_message_stream(self, message, socketio_instance):
        """Process a message and emit streaming responses"""
        try:
            # print(f"[Codex] Starting stream processing for session {self.session_id}")
            
            # Process the message and stream the response
            response_started = False
            
            async for event in self.agent.process_turn_stream(prompt=message):
                if not self.is_active:
                    # print(f"[Codex] Session {self.session_id} is no longer active, breaking")
                    break
                
                # print(f"[Codex] Received agent event: {event}")
                
                # Convert the agent event to our expected format
                converted_event = self.convert_agent_event(event)
                if converted_event:
                    # print(f"[Codex] Emitting event: {converted_event}")
                    
                    # Emit the converted event to the frontend immediately
                    socketio_instance.emit('codex_stream', {
                        'session_id': self.session_id,
                        'event': converted_event
                    }, room=self.session_id)
                    
                    response_started = True
                else:
                    print(f"[Codex] Skipping event (no conversion): {event}")
            
            # Check if we have pending tool calls that need approval
            if hasattr(self.agent, 'pending_tool_calls') and self.agent.pending_tool_calls:
                # print(f"[Codex] Agent has {len(self.agent.pending_tool_calls)} pending tool calls")
                
                # Store the tool calls for later execution - do this AFTER the stream
                for tool_call in self.agent.pending_tool_calls:
                    self.pending_tool_calls[tool_call.id] = tool_call
                    # print(f"[Codex] Stored tool call: {tool_call.id} ({tool_call.function.name})")
                
                self.waiting_for_tools = True
                # Don't emit response_end yet - wait for tool execution
                # print(f"[Codex] Waiting for tool approval/execution...")
                return
            
            # Always emit response_end to finalize the stream
            # print(f"[Codex] Stream processing completed, emitting response_end")
            socketio_instance.emit('codex_stream', {
                'session_id': self.session_id,
                'event': {'type': 'response_end'}
            }, room=self.session_id)
                
        except Exception as e:
            # print(f"[Codex] Error in stream processing: {e}")
            import traceback
            traceback.print_exc()
            
            socketio_instance.emit('codex_stream', {
                'session_id': self.session_id,
                'event': {
                    'type': 'error',
                    'content': str(e)
                }
            }, room=self.session_id)

    async def continue_with_tool_results(self, socketio_instance):
        """Continue processing after all tools have been executed"""
        try:
            if not self.tool_results:
                # print(f"[Codex] No tool results to continue with")
                return
            
            # print(f"[Codex] Starting continuation with {len(self.tool_results)} tool results")
            # for tool_id, result in self.tool_results.items():
                # print(f"[Codex] Tool {tool_id}: {result[:100]}...")
            
            # Convert tool results to the format expected by the agent
            tool_messages = []
            for tool_call_id, result in self.tool_results.items():
                tool_message: ChatCompletionToolMessageParam = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": str(result)
                }
                tool_messages.append(tool_message)
                # print(f"[Codex] Created tool message for {tool_call_id}")
            
            # print(f"[Codex] Continuing agent stream with {len(tool_messages)} tool messages")
            
            # Continue the agent stream with tool results
            response_received = False
            new_tool_calls_detected = False
            
            async for event in self.agent.continue_with_tool_results_stream(tool_messages):
                if not self.is_active:
                    # print(f"[Codex] Session no longer active during continuation")
                    break
                
                # print(f"[Codex] Continuation event: {event}")
                converted_event = self.convert_agent_event(event)
                if converted_event:
                    # print(f"[Codex] Emitting continuation event: {converted_event}")
                    socketio_instance.emit('codex_stream', {
                        'session_id': self.session_id,
                        'event': converted_event
                    }, room=self.session_id)
                    
                    if converted_event['type'] == 'text_delta':
                        response_received = True
                    elif converted_event['type'] == 'tool_call_start':
                        new_tool_calls_detected = True
                        # print(f"[Codex] New tool call detected during continuation")
                    elif converted_event['type'] == 'response_end':
                        # print(f"[Codex] Continuation stream completed successfully")
                        break
                # else:
                #     print(f"[Codex] Skipping continuation event: {event}")
            
            # *** CHECK FOR NEW TOOL CALLS FROM AGENT ***
            if hasattr(self.agent, 'pending_tool_calls') and self.agent.pending_tool_calls:
                # print(f"[Codex] Agent has {len(self.agent.pending_tool_calls)} NEW pending tool calls after continuation")
                
                # Store the NEW tool calls for approval
                for tool_call in self.agent.pending_tool_calls:
                    if tool_call.id not in self.pending_tool_calls:  # Only add new ones
                        self.pending_tool_calls[tool_call.id] = tool_call
                        # print(f"[Codex] Stored NEW tool call: {tool_call.id} ({tool_call.function.name})")
                
                # Clear only the completed tool results, keep the new pending calls
                self.tool_results.clear()
                self.waiting_for_tools = True
                # print(f"[Codex] Waiting for approval of NEW tool calls, not clearing tool state")
                
                # Don't emit response_end yet - wait for new tool execution
                return
            
            if not response_received and not new_tool_calls_detected:
                # print(f"[Codex] Warning: No text response or new tool calls received during continuation")
                # Still emit response_end to close the stream
                socketio_instance.emit('codex_stream', {
                    'session_id': self.session_id,
                    'event': {'type': 'response_end'}
                }, room=self.session_id)
            
            # *** ONLY CLEAR STATE IF NO NEW TOOL CALLS ***
            self.pending_tool_calls.clear()
            self.tool_results.clear()
            self.waiting_for_tools = False
            # print(f"[Codex] No new tool calls, clearing tool state and completing continuation")
            
        except Exception as e:
            # print(f"[Codex] Error continuing with tool results: {e}")
            import traceback
            traceback.print_exc()
            
            socketio_instance.emit('codex_stream', {
                'session_id': self.session_id,
                'event': {
                    'type': 'error',
                    'content': f'Error continuing with tool results: {str(e)}'
                }
            }, room=self.session_id)
            
            # Clear tool state on error
            self.pending_tool_calls.clear()
            self.tool_results.clear()
            self.waiting_for_tools = False
            # print(f"[Codex] Tool state cleared after error")

    def convert_agent_event(self, agent_event):
        """Convert agent stream event to frontend format"""
        # print(f"[Codex] Converting agent event: {agent_event}")
        
        if not isinstance(agent_event, dict):
            # If it's not a dict, try to convert it
            if hasattr(agent_event, '__dict__'):
                agent_event = agent_event.__dict__
            elif hasattr(agent_event, 'type'):
                # Try to extract basic info
                event_dict = {
                    'type': getattr(agent_event, 'type', 'unknown'),
                    'content': getattr(agent_event, 'content', None),
                }
                agent_event = event_dict
            else:
                # print(f"[Codex] Cannot convert event type: {type(agent_event)}")
                return None
        
        event_type = agent_event.get('type')
        # print(f"[Codex] Event type: {event_type}")
        
        if event_type == 'text_delta':
            return {
                'type': 'text_delta',
                'content': agent_event.get('content', '')
            }
        elif event_type == 'text' or event_type == 'message':
            # Handle full text messages as deltas
            return {
                'type': 'text_delta',
                'content': agent_event.get('content', '')
            }
        elif event_type == 'tool_call_start':
            return {
                'type': 'tool_call_start',
                'tool_call_id': agent_event.get('tool_call_id'),
                'tool_function_name': agent_event.get('tool_function_name')
            }
        elif event_type == 'tool_call_delta':
            return {
                'type': 'tool_call_delta',
                'tool_call_id': agent_event.get('tool_call_id'),
                'tool_arguments_delta': agent_event.get('tool_arguments_delta')
            }
        elif event_type == 'tool_call_end':
            return {
                'type': 'tool_call_end',
                'tool_call_id': agent_event.get('tool_call_id'),
                'tool_function_name': agent_event.get('tool_function_name'),
                'tool_arguments_complete': agent_event.get('tool_arguments_delta')  # Complete args in delta field
            }
        elif event_type == 'response_end' or event_type == 'done':
            return {
                'type': 'response_end'
            }
        elif event_type == 'error':
            return {
                'type': 'error',
                'content': agent_event.get('content', 'Unknown error')
            }
        elif event_type == 'cancelled':
            return {
                'type': 'cancelled'
            }
        else:
            # For any unhandled event type that has content, treat it as text
            if agent_event.get('content'):
                # print(f"[Codex] Treating unknown event type '{event_type}' as text_delta")
                return {
                    'type': 'text_delta',
                    'content': agent_event.get('content', '')
                }
            # print(f"[Codex] Unhandled event type: {event_type}")
            return None
        

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Clean up any sessions for this client
    session_id = request.sid
    if session_id in codex_sessions:
        codex_sessions[session_id].is_active = False
        del codex_sessions[session_id]

@socketio.on('start_codex_session')
def handle_start_codex_session(data):
    """Start a new Codex session"""
    session_id = request.sid
    
    try:
        # Get working directory from frontend
        working_directory = data.get('working_directory', '').strip()
        
        # If no directory provided, use current directory
        if not working_directory:
            working_directory = str(Path.cwd())
        else:
            # Validate the provided directory
            working_path = Path(working_directory).resolve()
            if not working_path.exists():
                emit('codex_session_error', {
                    'error': f'Directory does not exist: {working_directory}'
                })
                return
            if not working_path.is_dir():
                emit('codex_session_error', {
                    'error': f'Path is not a directory: {working_directory}'
                })
                return
            if not os.access(working_path, os.R_OK):
                emit('codex_session_error', {
                    'error': f'Directory is not readable: {working_directory}'
                })
                return
            
            working_directory = str(working_path)

        # Handle instruction selection if provided
        instruction_name = data.get('instruction_name')
        if instruction_name:
            # Verify instruction exists and set it as selected
            content = instructions_manager.get_instruction_content(instruction_name)
            if content:
                instructions_manager.set_selected_instruction(instruction_name)
                print(f"[Codex] Using instruction: {instruction_name}")
            else:
                print(f"[Codex] Warning: Instruction '{instruction_name}' not found, using current selection")

        # Load Codex configuration
        config_options = {
            "disable_project_doc": False,
            "project_doc_path": None,
            "is_full_context": False,
            "flex_mode": False,
            "full_stdout": True,
        }
        
        print("[Codex] Loading config...")
        # Use the specified working directory for config loading
        app_config = load_config(cwd=Path(working_directory), **config_options)
        
        # Override with any frontend-provided config
        if 'model' in data:
            app_config['model'] = data['model']
            print(f"[Codex] Using model: {data['model']}")
            
        # Create new session with the specified working directory
        print(f"[Codex] Creating session for {session_id} with working directory: {working_directory}")
        codex_sessions[session_id] = CodexSession(session_id, app_config, working_directory)
        
        # Join the session room
        join_room(session_id)
        
        emit('codex_session_started', {
            'session_id': session_id,
            'status': 'ready',
            'working_directory': working_directory,
            'instruction_name': instructions_manager.get_selected_instruction()
        })
        print(f"[Codex] Session {session_id} started successfully")
        
    except Exception as e:
        print(f"[Codex] Error starting session: {e}")
        import traceback
        traceback.print_exc()
        emit('codex_session_error', {
            'error': str(e)
        })

@socketio.on('send_codex_message')
def handle_codex_message(data):
    """Handle a message sent to Codex"""
    session_id = request.sid
    message = data.get('message', '')
    
    # print(f"[Codex] Received message from {session_id}: {message}")
    
    if session_id not in codex_sessions:
        # print(f"[Codex] No active session for {session_id}")
        emit('codex_error', {'error': 'No active session'})
        return
    
    session = codex_sessions[session_id]
    
    if not session.is_active:
        # print(f"[Codex] Session {session_id} is not active")
        emit('codex_error', {'error': 'Session is not active'})
        return
    
    # Clear any previous tool state
    session.pending_tool_calls.clear()
    session.tool_results.clear()
    session.waiting_for_tools = False
    
    # Run the async message processing in a separate thread
    def run_async_processing():
        # print(f"[Codex] Starting async processing for {session_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                session.process_message_stream(message, socketio)
            )
            # print(f"[Codex] Async processing completed successfully for {session_id}")
        except Exception as e:
            # print(f"[Codex] Error in async processing: {e}")
            import traceback
            traceback.print_exc()
            
            # Emit error to frontend
            socketio.emit('codex_stream', {
                'session_id': session_id,
                'event': {
                    'type': 'error',
                    'content': f'Processing error: {str(e)}'
                }
            }, room=session_id)
        finally:
            loop.close()
            # print(f"[Codex] Async processing cleanup completed for {session_id}")
    
    thread = threading.Thread(target=run_async_processing)
    thread.daemon = True
    thread.start()
    # print(f"[Codex] Started processing thread for {session_id}")

@socketio.on('execute_codex_tool')
def handle_tool_execution(data):
    """Handle tool execution approval/rejection"""
    session_id = request.sid
    tool_call_id = data.get('tool_call_id')
    action = data.get('action')  # 'approve' or 'reject'
    
    # print(f"[Codex] Tool execution request: {tool_call_id}, action: {action}")
    
    if session_id not in codex_sessions:
        # print(f"[Codex] No active session found for {session_id}")
        emit('codex_error', {'error': 'No active session'})
        return
    
    session = codex_sessions[session_id]
    
    # *** PREVENT DUPLICATE PROCESSING ***
    if tool_call_id in session.tool_results:
        # print(f"[Codex] Tool {tool_call_id} already processed, ignoring duplicate request")
        return
    
    # Debug session state
    # print(f"[Codex] Session state - pending_tool_calls: {list(session.pending_tool_calls.keys())}")
    # print(f"[Codex] Session state - waiting_for_tools: {session.waiting_for_tools}")
    # print(f"[Codex] Session state - tool_results: {list(session.tool_results.keys())}")
    
    try:
        if action == 'approve':
            # Execute the pending tool call
            if tool_call_id in session.pending_tool_calls:
                tool_call = session.pending_tool_calls[tool_call_id]
                # print(f"[Codex] Executing approved tool: {tool_call.function.name}")
                # print(f"[Codex] Agent working directory: {session.agent.working_directory}")
                
                result = session.agent._execute_tool_implementation(
                    tool_call,
                    is_sandboxed=True,  # Always sandbox for web interface
                    allowed_write_paths=[session.working_directory]  # Allow writes in working dir
                )
                
                # Store the result
                session.tool_results[tool_call_id] = result
                
                # Send the result back to frontend
                emit('codex_tool_result', {
                    'tool_call_id': tool_call_id,
                    'result': result
                })
                
                # print(f"[Codex] Tool {tool_call_id} executed successfully with result: {result[:100]}...")
                
            else:
                # print(f"[Codex] ERROR: Tool call {tool_call_id} not found in pending calls")
                # print(f"[Codex] Available pending calls: {list(session.pending_tool_calls.keys())}")
                session.tool_results[tool_call_id] = "Error: Tool call not found"
                emit('codex_tool_result', {
                    'tool_call_id': tool_call_id,
                    'result': 'Error: Tool call not found'
                })
        else:
            # Reject the tool execution
            # print(f"[Codex] Tool {tool_call_id} rejected by user")
            session.tool_results[tool_call_id] = 'Tool execution rejected by user'
            emit('codex_tool_result', {
                'tool_call_id': tool_call_id,
                'result': 'Tool execution rejected by user'
            })
        
        # Check if all pending tools have been processed
        all_tools_processed = all(
            tool_id in session.tool_results 
            for tool_id in session.pending_tool_calls.keys()
        )
        
        # print(f"[Codex] All tools processed: {all_tools_processed} ({len(session.tool_results)}/{len(session.pending_tool_calls)})")
        
        # *** ONLY CONTINUE IF ALL TOOLS PROCESSED AND WAITING ***
        if all_tools_processed and session.waiting_for_tools and session.tool_results:
            # print(f"[Codex] All tools processed, continuing stream...")
            # Set waiting_for_tools to False to prevent duplicate continuations
            session.waiting_for_tools = False
            
            # *** REMOVE PROCESSED TOOL CALLS FROM PENDING LIST ***
            processed_tool_ids = list(session.tool_results.keys())
            for tool_id in processed_tool_ids:
                if tool_id in session.pending_tool_calls:
                    del session.pending_tool_calls[tool_id]
                    # print(f"[Codex] Removed processed tool call {tool_id} from pending list")
            
            # print(f"[Codex] Remaining pending tool calls after cleanup: {list(session.pending_tool_calls.keys())}")
            
            # Continue the agent stream with all tool results
            def run_continuation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        session.continue_with_tool_results(socketio)
                    )
                except Exception as e:
                    # print(f"[Codex] Error in continuation thread: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    loop.close()
            
            # Run in separate thread
            import threading
            thread = threading.Thread(target=run_continuation)
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        # print(f"[Codex] Error in tool execution: {e}")
        import traceback
        traceback.print_exc()
        
        # Store error result
        session.tool_results[tool_call_id] = f'Tool execution error: {str(e)}'
        
        emit('codex_error', {'error': f'Tool execution error: {str(e)}'})

@socketio.on('stop_codex_session')
def handle_stop_codex_session():
    """Stop the current Codex session"""
    session_id = request.sid
    
    if session_id in codex_sessions:
        codex_sessions[session_id].is_active = False
        del codex_sessions[session_id]
        leave_room(session_id)
        
    emit('codex_session_stopped')

# Regular HTTP endpoints for Codex management
@app.route('/api/codex/health', methods=['GET'])
def codex_health_check():
    """Check if Codex functionality is available"""
    try:
        # Test if we can import required modules
        from core.agent import Agent
        return jsonify({
            "status": "success",
            "message": "Codex functionality available",
            "active_sessions": len(codex_sessions)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Codex functionality unavailable: {str(e)}"
        }), 500

@app.route('/api/codex/config', methods=['GET'])
def get_codex_config():
    """Get available Codex configuration options"""
    try:
        # Get current instructions info
        instructions = temp_instructions_manager.get_instructions_list()
        selected_instruction = temp_instructions_manager.get_selected_instruction()
        
        return jsonify({
            "status": "success",
            "models": [
                # O3 Reasoning Models
                "o3",
                "o3-mini", 
                "o3-pro",
                
                # GPT-4.1 Family
                "gpt-4.1-nano",
                "gpt-4.1-mini",
                "gpt-4.1",
                
                # Coding Specialist
                "codex-mini",
                
                # GPT-4o and GPT-4 variants
                "gpt-4o",
                "gpt-4",
                "gpt-4-32k",
                
                # Earlier models
                "o1",
                "gpt-4.5-preview",
                "gpt-35-turbo"
            ],
            "model_descriptions": {
                "o3": "O3 - Flagship multimodal reasoning model, excellent for complex coding tasks",
                "o3-mini": "O3 Mini - Cost-effective reasoning model, 90% cheaper than O3",
                "o3-pro": "O3-Pro - Maximum reasoning power for complex problems",
                "gpt-4.1-nano": "GPT-4.1 Nano - Ultra-fast, sub-second latency for simple tasks", 
                "gpt-4.1-mini": "GPT-4.1 Mini - Balanced speed and quality, 26% cheaper than GPT-4o",
                "gpt-4.1": "GPT-4.1 - Latest flagship with 1M token context, excellent for code diffs",
                "codex-mini": "Codex Mini - Specialized for code completion and generation",
                "gpt-4o": "GPT-4o - Real-time multimodal model with low latency", 
                "gpt-4": "GPT-4 Turbo - High-quality model with vision capabilities",
                "gpt-4-32k": "GPT-4 32k - Large context variant for long documents",
                "o1": "O1 - Advanced reasoning model for complex STEM and coding",
                "gpt-4.5-preview": "GPT-4.5 Preview - Research preview bridging GPT-4 to GPT-5",
                "gpt-35-turbo": "GPT-3.5 Turbo - Fast, cost-effective model for lightweight tasks"
            },
            "default_model": "codex-mini",
            "max_tokens": 10000,
            "current_instruction": selected_instruction,  # This now gets the actual selected instruction
            "instructions_available": len(instructions) > 0,
            "instructions_folder": temp_instructions_manager.get_instructions_dir()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Update your Codex session handler to use the selected instruction:

@socketio.on('start_codex_session')
def handle_start_codex_session(data):
    """Start a new Codex session"""
    session_id = request.sid
    
    try:
        # Get working directory from frontend
        working_directory = data.get('working_directory', '').strip()
        
        # If no directory provided, use current directory
        if not working_directory:
            working_directory = str(Path.cwd())
        else:
            # Validate the provided directory
            working_path = Path(working_directory).resolve()
            if not working_path.exists():
                emit('codex_session_error', {
                    'error': f'Directory does not exist: {working_directory}'
                })
                return
            if not working_path.is_dir():
                emit('codex_session_error', {
                    'error': f'Path is not a directory: {working_directory}'
                })
                return
            if not os.access(working_path, os.R_OK):
                emit('codex_session_error', {
                    'error': f'Directory is not readable: {working_directory}'
                })
                return
            
            working_directory = str(working_path)

        # Handle instruction selection if provided
        instruction_name = data.get('instruction_name')
        if instruction_name:
            # Verify instruction exists and set it as selected
            content = temp_instructions_manager.get_instruction_content(instruction_name)
            if content:
                temp_instructions_manager.set_selected_instruction(instruction_name)
                print(f"[Codex] Using instruction: {instruction_name}")
            else:
                print(f"[Codex] Warning: Instruction '{instruction_name}' not found, using current selection")

        # Load Codex configuration
        config_options = {
            "disable_project_doc": False,
            "project_doc_path": None,
            "is_full_context": False,
            "flex_mode": False,
            "full_stdout": True,
        }
        
        print("[Codex] Loading config...")
        # Use the specified working directory for config loading
        app_config = load_config(cwd=Path(working_directory), **config_options)
        
        # GET AND APPLY CUSTOM INSTRUCTIONS
        selected_instruction = temp_instructions_manager.get_selected_instruction()
        custom_instructions = temp_instructions_manager.get_instruction_content(selected_instruction)
        
        if custom_instructions:
            app_config['instructions'] = custom_instructions
            print(f"[Codex] Applied custom instructions: {selected_instruction}")
        else:
            print(f"[Codex] Warning: Could not load instructions '{selected_instruction}', using default config")
        
        # Override with any frontend-provided config
        if 'model' in data:
            app_config['model'] = data['model']
            print(f"[Codex] Using model: {data['model']}")
            
        # Create new session with the specified working directory
        print(f"[Codex] Creating session for {session_id} with working directory: {working_directory}")
        codex_sessions[session_id] = CodexSession(session_id, app_config, working_directory)
        
        # Join the session room
        join_room(session_id)
        
        emit('codex_session_started', {
            'session_id': session_id,
            'status': 'ready',
            'working_directory': working_directory,
            'instruction_name': selected_instruction
        })
        print(f"[Codex] Session {session_id} started successfully")
        
    except Exception as e:
        print(f"[Codex] Error starting session: {e}")
        import traceback
        traceback.print_exc()
        emit('codex_session_error', {
            'error': str(e)
        })
    
@socketio.on('test_codex_message')
def handle_test_codex_message(data):
    """Test handler to verify basic functionality"""
    session_id = request.sid
    message = data.get('message', '')
    
    print(f"[Codex Test] Received test message: {message}")
    
    # Send a simple test response
    test_events = [
        {'type': 'text_delta', 'content': 'Hello '},
        {'type': 'text_delta', 'content': 'from '},
        {'type': 'text_delta', 'content': 'Codex! '},
        {'type': 'text_delta', 'content': f'You said: {message}'},
        {'type': 'response_end'}
    ]
    
    def send_test_events():
        import time
        for event in test_events:
            print(f"[Codex Test] Sending event: {event}")
            socketio.emit('codex_stream', {
                'session_id': session_id,
                'event': event
            }, room=session_id)
            time.sleep(0.1)  # Small delay between events
    
    # Send events in a separate thread
    thread = threading.Thread(target=send_test_events)
    thread.daemon = True
    thread.start()

@app.route('/api/codex/get-current-directory', methods=['GET'])
def get_current_directory():
    """Get the current working directory of the backend"""
    try:
        current_dir = str(Path.cwd())
        return jsonify({
            "status": "success",
            "current_directory": current_dir
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/codex/browse-directory', methods=['POST'])
def browse_directory():
    """Browse directory or provide directory listing"""
    try:
        data = request.json
        action = data.get('action', 'list_directory')
        current_path = data.get('current_path', '').strip()
        
        # For now, we'll provide a simple directory listing instead of a picker
        # In a desktop app, you could integrate with system file dialogs
        
        if current_path:
            try:
                path_obj = Path(current_path).resolve()
            except Exception:
                path_obj = Path.cwd()
        else:
            path_obj = Path.cwd()
            
        # Ensure the path exists and is a directory
        if not path_obj.exists():
            path_obj = Path.cwd()
        elif not path_obj.is_dir():
            path_obj = path_obj.parent if path_obj.parent.exists() else Path.cwd()
        
        # List directory contents
        items = []
        try:
            # Add parent directory option (if not at root)
            if path_obj.parent != path_obj:
                items.append({
                    "name": "..",
                    "path": str(path_obj.parent),
                    "is_directory": True,
                    "is_parent": True,
                    "size": None
                })
            
            # List current directory contents
            for item in sorted(path_obj.iterdir()):
                if item.name.startswith('.'):
                    continue  # Skip hidden files
                
                try:
                    stat_info = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_directory": item.is_dir(),
                        "is_parent": False,
                        "size": stat_info.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                    })
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue
                    
        except PermissionError:
            return jsonify({
                "status": "error",
                "message": f"Permission denied accessing: {path_obj}"
            }), 403
        
        return jsonify({
            "status": "success",
            "current_path": str(path_obj),
            "parent": str(path_obj.parent) if path_obj.parent != path_obj else None,
            "items": items,
            "can_select": True
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/codex/validate-directory', methods=['POST'])
def validate_directory():
    """Validate if a directory path exists and is accessible"""
    try:
        data = request.json
        path = data.get('path', '')
        
        if not path:
            return jsonify({
                "status": "error",
                "message": "No path provided"
            }), 400
        
        path_obj = Path(path).resolve()
        
        result = {
            "path": str(path_obj),
            "exists": path_obj.exists(),
            "is_directory": path_obj.is_dir() if path_obj.exists() else False,
            "readable": os.access(path_obj, os.R_OK) if path_obj.exists() else False,
            "writable": os.access(path_obj, os.W_OK) if path_obj.exists() else False,
        }
        
        if result["exists"] and result["is_directory"] and result["readable"]:
            status = "valid"
            message = "Directory is valid and accessible"
        else:
            status = "invalid"
            if not result["exists"]:
                message = "Directory does not exist"
            elif not result["is_directory"]:
                message = "Path is not a directory"
            elif not result["readable"]:
                message = "Directory is not readable"
            else:
                message = "Directory is not accessible"
        
        return jsonify({
            "status": status,
            "message": message,
            **result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

class TempInstructionsManager:
    """Temporary inline instructions manager"""
    
    def __init__(self):
        self.base_dir = Path.home() / ".dataagent"
        self.instructions_dir = self.base_dir / "instructions"
        self.config_file = self.base_dir / "instructions_config.json"
        self.instructions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default if none exist
        default_file = self.instructions_dir / "default.md"
        if not default_file.exists():
            default_content = """# Default Codex Instructions

You are Codex, an AI coding assistant integrated into the Data Agent platform.

## Your Capabilities
- Writing and debugging code in multiple languages
- Analyzing data files and creating visualizations
- Creating scripts and automation tools
- Explaining technical concepts clearly
- File manipulation and organization
- Command-line operations

## Guidelines
- Always ask for permission before making significant changes to files
- Provide clear explanations of what your tools do and what results mean
- When analyzing data, always follow up with insights and recommendations
- Be helpful, accurate, and prioritize safety in all suggestions
- Focus on practical, working solutions

## Tool Usage
After executing any tool, always provide:
1. What the tool accomplished
2. Interpretation of the results
3. Any insights or patterns discovered
4. Recommended next steps

Remember: You're here to help users be more productive with their coding and data analysis tasks!
"""
            try:
                with open(default_file, 'w', encoding='utf-8') as f:
                    f.write(default_content)
            except Exception as e:
                print(f"Could not create default instructions: {e}")
    
    def get_instructions_dir(self):
        return str(self.instructions_dir)
    
    def get_instructions_list(self):
        """Get list of instruction files"""
        instructions = []
        try:
            for file_path in self.instructions_dir.glob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract title from first line if it's a header
                    lines = content.split('\n')
                    title = lines[0].replace('# ', '').strip() if lines and lines[0].startswith('# ') else file_path.stem
                    
                    instructions.append({
                        'filename': file_path.stem,
                        'title': title,
                        'path': str(file_path),
                        'size': len(content),
                        'modified': os.path.getmtime(file_path)
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"Error listing instructions: {e}")
        
        return sorted(instructions, key=lambda x: x['filename'])
    
    def get_selected_instruction(self):
        """Get the currently selected instruction filename"""
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config.get('selected_instruction', 'default')
            except:
                pass
        return 'default'
    
    def set_selected_instruction(self, filename: str):
        """Set the currently selected instruction"""
        try:
            import json
            config = {'selected_instruction': filename}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error setting selected instruction: {e}")
            return False
    
    def get_instruction_content(self, filename: str):
        """Get content of a specific instruction file"""
        file_path = self.instructions_dir / f"{filename}.md"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading instruction file {filename}: {e}")
            return None

# Update the global instance
temp_instructions_manager = TempInstructionsManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.route('/api/codex/instructions/select', methods=['POST'])
def select_instruction():
    """Set the active instruction file"""
    try:
        data = request.json
        filename = data.get('filename', '').strip()
        
        if not filename:
            return jsonify({
                "status": "error",
                "message": "Filename is required"
            }), 400
        
        # Verify the instruction file exists
        content = temp_instructions_manager.get_instruction_content(filename)
        if content is None:
            return jsonify({
                "status": "error",
                "message": "Instruction file not found"
            }), 404
        
        success = temp_instructions_manager.set_selected_instruction(filename)
        if success:
            return jsonify({
                "status": "success",
                "message": f"Selected instruction: {filename}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to set selected instruction"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/api/codex/instructions/current', methods=['GET'])
def get_current_instructions():
    """Get the currently active instructions content"""
    try:
        selected = temp_instructions_manager.get_selected_instruction()
        content = temp_instructions_manager.get_instruction_content(selected)
        
        if content is None:
            # Fallback to default
            content = temp_instructions_manager.get_instruction_content('default')
            selected = 'default'
        
        return jsonify({
            "status": "success",
            "selected": selected,
            "content": content or ""
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/api/codex/instructions/open-folder', methods=['POST'])
def open_instructions_folder():
    """Open the instructions folder in File Explorer"""
    try:
        folder_path = temp_instructions_manager.get_instructions_dir()
        
        # Open folder in Windows File Explorer
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
            return jsonify({
                "status": "success",
                "message": f"Opened instructions folder: {folder_path}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "This feature is only available on Windows"
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to open folder: {str(e)}"
        }), 500

@app.route('/api/codex/instructions', methods=['GET'])
def get_instructions_list():
    """Get list of all available instruction files"""
    try:
        instructions = temp_instructions_manager.get_instructions_list()
        selected = temp_instructions_manager.get_selected_instruction()
        
        return jsonify({
            "status": "success",
            "instructions": instructions,
            "selected": selected
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/codex/instructions', methods=['POST'])
def save_instruction():
    """Save or create a new instruction file"""
    try:
        data = request.json
        filename = data.get('filename', '').strip()
        content = data.get('content', '')
        
        if not filename:
            return jsonify({
                "status": "error",
                "message": "Filename is required"
            }), 400
        
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_filename:
            safe_filename = "untitled"
        
        file_path = temp_instructions_manager.instructions_dir / f"{safe_filename}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "status": "success",
            "message": f"Instruction '{safe_filename}' saved successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/codex/instructions/<filename>', methods=['GET'])
def get_instruction_content(filename):
    """Get content of a specific instruction file"""
    try:
        file_path = temp_instructions_manager.instructions_dir / f"{filename}.md"
        
        if not file_path.exists():
            return jsonify({
                "status": "error",
                "message": "Instruction file not found"
            }), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "content": content
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/api/codex/instructions/<filename>', methods=['DELETE'])
def delete_instruction(filename):
    """Delete an instruction file"""
    try:
        if filename == 'default':
            return jsonify({
                "status": "error",
                "message": "Cannot delete default instructions"
            }), 400
        
        file_path = temp_instructions_manager.instructions_dir / f"{filename}.md"
        if not file_path.exists():
            return jsonify({
                "status": "error",
                "message": "File not found"
            }), 404
        
        file_path.unlink()
        
        return jsonify({
            "status": "success",
            "message": f"Instruction '{filename}' deleted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


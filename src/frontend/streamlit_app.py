# src/frontend/streamlit_app.py
import streamlit as st
import requests
import os
import logging
import traceback
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import json
from dotenv import load_dotenv
from datetime import datetime
import sys
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class ChatResponse:
    """Data class for API chat response"""
    answer: str

class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class APIError(AppError):
    """Exception for API-related errors"""
    pass

class ValidationError(AppError):
    """Exception for validation errors"""
    pass

class ConfigurationError(AppError):
    """Exception for configuration errors"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    @staticmethod
    def log_error(error: Exception, context: str = "", user_message: str = None):
        """Log error with context and return user-friendly message"""
        error_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Log detailed error information
        logger.error(f"Error ID: {error_id}")
        logger.error(f"Context: {context}")
        logger.error(f"Error Type: {type(error).__name__}")
        logger.error(f"Error Message: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Display user-friendly error in Streamlit
        if user_message:
            st.error(f"❌ {user_message}")
        else:
            st.error(f"❌ An error occurred. Error ID: {error_id}")
        
        # Show detailed error in debug mode
        if st.session_state.get('debug_mode', False):
            with st.expander(f"🐛 Debug Info (Error ID: {error_id})"):
                st.code(f"Error Type: {type(error).__name__}")
                st.code(f"Error Message: {str(error)}")
                st.code(f"Context: {context}")
                if hasattr(error, 'details') and error.details:
                    st.json(error.details)
        
        return error_id

class APIClient:
    """Handles all API communications with enhanced error handling"""
    
    def __init__(self):
        self.endpoint = self._validate_endpoint()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Streamlit-PDF-Chatbot/1.0'
        })
        
        # Test connection on initialization
        self._test_connection()
    
    def _validate_endpoint(self) -> str:
        """Validate and return the API endpoint"""
        endpoint = os.getenv('ENDPOINT')
        
        if not endpoint:
            error = ConfigurationError(
                "ENDPOINT environment variable not set",
                "MISSING_ENDPOINT",
                {"env_file_exists": os.path.exists('.env')}
            )
            ErrorHandler.log_error(
                error, 
                "API Client Initialization",
                "Configuration error: Please check your .env file"
            )
            raise error
        
        # Validate URL format
        if not endpoint.startswith(('http://', 'https://')):
            error = ConfigurationError(
                f"Invalid endpoint format: {endpoint}",
                "INVALID_ENDPOINT_FORMAT",
                {"endpoint": endpoint}
            )
            ErrorHandler.log_error(
                error,
                "API Client Initialization",
                "Invalid endpoint URL format in configuration"
            )
            raise error
        
        logger.info(f"API endpoint configured: {endpoint}")
        return endpoint.rstrip('/')
    
    def _test_connection(self):
        """Test basic connectivity to the API endpoint"""
        try:
            # Try a simple HEAD request to test connectivity
            response = requests.head(self.endpoint, timeout=5)
            logger.info(f"Connection test successful. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Connection test failed: {str(e)}")
            # Don't raise error here, just log the warning
    
    def send_query(self, query: str, pdf_uuid: str = None) -> Optional[ChatResponse]:
        """Send user query to the answer endpoint with comprehensive error handling"""
        if not query or not query.strip():
            error = ValidationError(
                "Query cannot be empty",
                "EMPTY_QUERY"
            )
            ErrorHandler.log_error(
                error,
                "Query Validation",
                "Please enter a valid question"
            )
            return None
        
        try:
            url = f"{self.endpoint}/answer"
            payload = {"query": query.strip()}
            if pdf_uuid:
                payload["pdf_uuid"] = pdf_uuid
            
            logger.info(f"Sending query to {url}")
            logger.debug(f"Query payload: {payload}")
            
            response = self.session.post(
                url,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            # Handle different HTTP status codes
            if response.status_code == 404:
                raise APIError(
                    "Answer endpoint not found",
                    "ENDPOINT_NOT_FOUND",
                    {"url": url, "status_code": response.status_code}
                )
            elif response.status_code == 500:
                raise APIError(
                    "Server error occurred",
                    "SERVER_ERROR",
                    {"url": url, "status_code": response.status_code}
                )
            elif response.status_code != 200:
                raise APIError(
                    f"Unexpected status code: {response.status_code}",
                    "UNEXPECTED_STATUS",
                    {"url": url, "status_code": response.status_code}
                )
            
            response.raise_for_status()
            
            # Parse JSON response
            try:
                data = response.json()
                logger.debug(f"Response data: {data}")
            except json.JSONDecodeError as e:
                raise APIError(
                    "Invalid JSON response from server",
                    "INVALID_JSON",
                    {"response_text": response.text[:500]}
                )
            
            # Validate response structure
            required_fields = ['answer']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise APIError(
                    f"Missing required fields in response: {missing_fields}",
                    "MISSING_RESPONSE_FIELDS",
                    {"missing_fields": missing_fields, "response_data": data}
                )
            
            # Create response object with only the answer field
            chat_response = ChatResponse(
                answer=data.get('answer', '')
            )
            
            logger.info("Query processed successfully")
            return chat_response
            
        except requests.exceptions.Timeout as e:
            error = APIError(
                "Request timed out",
                "TIMEOUT",
                {"timeout": 30, "url": url}
            )
            ErrorHandler.log_error(
                error,
                "API Query Request",
                "The request took too long. Please try again."
            )
            return None
            
        except requests.exceptions.ConnectionError as e:
            error = APIError(
                "Cannot connect to API server",
                "CONNECTION_ERROR",
                {"endpoint": self.endpoint}
            )
            ErrorHandler.log_error(
                error,
                "API Query Request",
                "Cannot connect to the server. Please check your internet connection."
            )
            return None
            
        except APIError:
            # Re-raise API errors as they're already handled
            raise
            
        except Exception as e:
            error = APIError(
                f"Unexpected error during query: {str(e)}",
                "UNEXPECTED_ERROR",
                {"error_type": type(e).__name__}
            )
            ErrorHandler.log_error(
                error,
                "API Query Request",
                "An unexpected error occurred. Please try again."
            )
            return None
    
    def upload_pdf(self, pdf_file, process_mode="normal") -> dict:
        """Upload PDF file to the server with enhanced error handling
        
        Args:
            pdf_file: The PDF file to upload
            process_mode: Processing mode - 'normal', 'full', or 'fast'
        """
        try:
            # Validate file
            if not pdf_file:
                raise ValidationError(
                    "No file provided",
                    "NO_FILE"
                )
            
            if not pdf_file.name.lower().endswith('.pdf'):
                raise ValidationError(
                    "File must be a PDF",
                    "INVALID_FILE_TYPE",
                    {"file_name": pdf_file.name}
                )
            
            file_size = len(pdf_file.getvalue())
            file_size_mb = file_size / (1024 * 1024)
            
            # Updated size limit: 20MB
            max_size = 20 * 1024 * 1024  # 20MB
            if file_size > max_size:
                raise ValidationError(
                    f"File too large: {file_size_mb:.1f}MB (max: 20MB)",
                    "FILE_TOO_LARGE",
                    {"file_size": file_size, "max_size": max_size}
                )
            
            logger.info(f"Uploading PDF: {pdf_file.name} ({file_size_mb:.2f}MB) with mode: {process_mode}")
            
            url = f"{self.endpoint}/uploadpdf"
            files = {'file': (pdf_file.name, pdf_file.getvalue(), 'application/pdf')}
            
            # Remove Content-Type header for file upload
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                url,
                files=files,
                headers=headers,
                timeout=1000
            )
            logger.info(f"the whole result file {response}")
            logger.info(f"Upload response status: {response.status_code}")
            
            if response.status_code == 404:
                raise APIError(
                    "Upload endpoint not found",
                    "UPLOAD_ENDPOINT_NOT_FOUND",
                    {"url": url}
                )
            elif response.status_code == 413:
                raise APIError(
                    "File too large for server",
                    "FILE_TOO_LARGE_SERVER",
                    {"file_size": file_size}
                )
            
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise APIError(
                    "Invalid JSON response from upload endpoint",
                    "UPLOAD_INVALID_JSON",
                    {"response_text": response.text[:500]}
                )

            success = data.get('success', False)
            logger.info(f"Upload result: {'success' if success else 'failed'}")

            if success:
                logger.info(f"pdf_uuid at upload pdf function: {data.get('pdf_uuid')}")
                logger.info(f"data: {data}")
                return {
                    'success': True,
                    'pdf_uuid': data.get('pdf_uuid'),
                    'pdf_name': data.get('filename'),
                    'filename': data.get('filename'),
                    'display_name': data.get('display_name', f"{data.get('filename', 'Unknown')} ({data.get('pdf_uuid', 'No UUID')[:8]})")
                }
            else:
                return {'success': False, 'error': data.get('message', 'Upload failed')}
            
        except ValidationError as e:
            ErrorHandler.log_error(
                e,
                "PDF Upload Validation",
                e.message
            )
            return {'success': False, 'error': e.message}
            
        except requests.exceptions.Timeout as e:
            error = APIError(
                "Upload timed out",
                "UPLOAD_TIMEOUT",
                {"timeout": 60, "file_name": pdf_file.name if pdf_file else "unknown"}
            )
            ErrorHandler.log_error(
                error,
                "PDF Upload Request",
                "Upload took too long. Please try a smaller file."
            )
            return {'success': False, 'error': 'Upload timed out'}
            
        except requests.exceptions.ConnectionError as e:
            error = APIError(
                "Cannot connect to upload server",
                "UPLOAD_CONNECTION_ERROR",
                {"endpoint": self.endpoint}
            )
            ErrorHandler.log_error(
                error,
                "PDF Upload Request",
                "Cannot connect to the server for upload."
            )
            return {'success': False, 'error': 'Connection failed'}
            
        except Exception as e:
            error = APIError(
                f"Unexpected error during upload: {str(e)}",
                "UPLOAD_UNEXPECTED_ERROR",
                {"error_type": type(e).__name__}
            )
            ErrorHandler.log_error(
                error,
                "PDF Upload Request",
                "An unexpected error occurred during upload."
            )
            return {'success': False, 'error': str(e)}

class ChatUI:
    """Handles chat interface rendering and state management with error handling"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        try:
            if "messages" not in st.session_state:
                st.session_state.messages = []
            if "suggested_questions" not in st.session_state:
                st.session_state.suggested_questions = []
            if "suggested_query" not in st.session_state:
                st.session_state.suggested_query = None
            if "debug_mode" not in st.session_state:
                st.session_state.debug_mode = False
            if "error_count" not in st.session_state:
                st.session_state.error_count = 0
            if 'current_pdf_uuid' not in st.session_state:
                st.session_state.current_pdf_uuid = None
            if 'current_pdf_name' not in st.session_state:
                st.session_state.current_pdf_name = None
            if 'pdf_display_name' not in st.session_state:
                st.session_state.pdf_display_name = None
            if 'pdf_content' not in st.session_state:
                st.session_state.pdf_content = None
                
            logger.info("Session state initialized successfully")
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "Session State Initialization",
                "Failed to initialize application state"
            )
    
    def display_chat_history(self):
        """Display all chat messages with error handling"""
        try:
            for idx, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Display enrollment prompt if applicable
                    if message["role"] == "assistant" and message.get("show_enroll"):
                        st.info("💡 Would you like to enroll for more information?")
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "Chat History Display",
                "Error displaying chat history"
            )
    
    def _handle_user_input(self, user_input: str):
        """Process user input and get response with comprehensive error handling"""
        try:
            # Validate input
            if not user_input or not user_input.strip():
                st.warning("Please enter a valid question.")
                return
            
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input.strip()
            })
            
            # Get response from API
            with st.spinner("Thinking..."):
                response = self.api_client.send_query(user_input.strip(), st.session_state.current_pdf_uuid)
            
            if response:
                # Add assistant response to chat
                assistant_message = {
                    "role": "assistant", 
                    "content": response.answer
                }
                st.session_state.messages.append(assistant_message)
                
                # Reset error count on successful response
                st.session_state.error_count = 0
                
            else:
                # Increment error count
                st.session_state.error_count += 1
                
                # Add error message with helpful suggestions
                error_message = "I'm sorry, I encountered an error while processing your request."
                
                if st.session_state.error_count >= 3:
                    error_message += " Multiple errors detected. Please check your connection and try again later."
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message
                })
                
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "User Input Handling",
                "Error processing your message"
            )
    
    def render_chat_interface(self):
        """Render the main chat interface with error boundaries"""
        try:
            # Modern header with better design
            st.markdown("""
                <div style="text-align: center; padding: 2rem 0 1rem 0;">
                    <h1 style="font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        🧠 Hybrid RAG Assistant
                    </h1>
                    <p style="font-size: 1.2rem; color: #6b7280; margin: 0;">
                        Intelligent document querying with text and table understanding
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Add mode selector with better visibility
            st.markdown("""
                <div style="text-align: center; margin: 1.5rem 0 1rem 0;">
                    <p style="color: #1f2937 !important; font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 600;">
                        Select Mode
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                mode = st.radio(
                    "mode_selector",
                    ["💬 Normal Chat", "🔍 Comparison Demo"],
                    horizontal=True,
                    key="mode_radio",
                    index=0,
                    label_visibility="collapsed"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if mode == "🔍 Comparison Demo":
                self._render_comparison_mode()
                return
            
            # Display current PDF indicator with modern card design
            if st.session_state.current_pdf_uuid:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 2rem;
                        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
                    ">
                        <div style="display: flex; align-items: center; color: white;">
                            <span style="font-size: 2.5rem; margin-right: 1rem;">📄</span>
                            <div>
                                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.3rem;">ACTIVE DOCUMENT</div>
                                <div style="font-size: 1.3rem; font-weight: 600;">{st.session_state.pdf_display_name}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show suggested questions based on document type
                st.markdown("### 💡 Suggested Questions")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 Ask about tables", use_container_width=True):
                        st.session_state['suggested_query'] = "What tables are in this document?"
                        st.rerun()
                with col2:
                    if st.button("📝 Summarize content", use_container_width=True):
                        st.session_state['suggested_query'] = "Can you summarize the main points?"
                        st.rerun()
                with col3:
                    if st.button("🔍 Find specific data", use_container_width=True):
                        st.session_state['suggested_query'] = "What are the key statistics?"
                        st.rerun()
                
                st.markdown("---")
            else:
                # Modern empty state
                st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                        border-radius: 20px;
                        padding: 4rem 2rem;
                        margin: 3rem 0;
                        text-align: center;
                        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                    ">
                        <div style="font-size: 5rem; margin-bottom: 1.5rem; animation: pulse 2s infinite;">📚</div>
                        <h2 style="color: #92400e; margin: 0 0 1rem 0; font-size: 2rem; font-weight: 700;">
                            No Document Loaded
                        </h2>
                        <p style="color: #78350f; font-size: 1.2rem; margin: 0; max-width: 600px; margin: 0 auto;">
                            Upload a PDF using the sidebar to unlock the power of Hybrid RAG and start asking intelligent questions!
                        </p>
                        <div style="margin-top: 2rem;">
                            <span style="background: white; padding: 0.75rem 1.5rem; border-radius: 8px; 
                                        color: #92400e; font-weight: 600; display: inline-block;">
                                👈 Check out the sidebar to get started
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Display chat history
            st.markdown("### 💬 Conversation")
            self.display_chat_history()
            
            # Handle suggested query
            if 'suggested_query' in st.session_state and st.session_state.suggested_query:
                query_to_process = st.session_state.suggested_query
                st.session_state.suggested_query = None
                self._handle_user_input(query_to_process)
                st.rerun()
            
            # Chat input with better styling
            if prompt := st.chat_input("💭 Ask me anything about your documents...", key="user_input"):
                self._handle_user_input(prompt)
                st.rerun()
            
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "Chat Interface Rendering",
                "Error rendering chat interface"
            )
    
    def _render_comparison_mode(self):
        """Render the comparison demo mode showing Conventional vs Hybrid RAG side-by-side"""
        try:
            # Check if PDF is loaded
            if not st.session_state.current_pdf_uuid:
                st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                        border-radius: 20px;
                        padding: 3rem 2rem;
                        margin: 2rem 0;
                        text-align: center;
                        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                    ">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
                        <h2 style="color: #991b1b; margin: 0 0 1rem 0; font-size: 1.8rem; font-weight: 600;">
                            Upload Required
                        </h2>
                        <p style="color: #7f1d1d; font-size: 1.1rem; margin: 0;">
                            Please upload a PDF document first to try the comparison demo!
                        </p>
                        <p style="color: #991b1b; font-size: 0.95rem; margin-top: 1rem; opacity: 0.9;">
                            💡 Upload a PDF with tables (like the FIFA World Cup PDF) for best results.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                return
            
            # Display active document with modern card
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
                ">
                    <div style="display: flex; align-items: center; color: white;">
                        <span style="font-size: 2rem; margin-right: 1rem;">📄</span>
                        <div>
                            <div style="font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.3rem;">LOADED DOCUMENT</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{st.session_state.pdf_display_name}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Introduction with modern styling
            st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="font-size: 2rem; font-weight: 700; color: #1f2937; margin-bottom: 0.5rem;">
                        🎯 Comparison Demo
                    </h2>
                    <h3 style="font-size: 1.3rem; font-weight: 600; 
                               background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        Conventional RAG vs Hybrid RAG
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div style="background: #f9fafb; border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; border: 1px solid #e5e7eb;">
                    <p style="color: #374151; font-size: 1.05rem; margin: 0; line-height: 1.6;">
                        This demo shows the <strong>difference</strong> between:<br><br>
                        📚 <strong>Conventional RAG:</strong> Uses only vector search on text embeddings (Pinecone)<br>
                        🧠 <strong>Hybrid RAG:</strong> Uses LangGraph to intelligently route queries to text, tables, or both
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Query input with better design
            demo_query = st.text_input(
                "**🔍 Enter your question:**",
                placeholder="e.g., What was the host nation for the first World Cup?",
                key="comparison_query"
            )
            
            # Suggested questions with card design
            st.markdown("**💡 Try These Questions:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Table Query", use_container_width=True, type="secondary"):
                    demo_query = "What was the host nation for the first World Cup?"
                    st.rerun()
            with col2:
                if st.button("📝 Text Query", use_container_width=True, type="secondary"):
                    demo_query = "Tell me about the history of the World Cup"
                    st.rerun()
            with col3:
                if st.button("🔀 Hybrid Query", use_container_width=True, type="secondary"):
                    demo_query = "Compare the winners and scores from different tournaments"
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Run comparison button
            if st.button("🚀 Run Comparison", type="primary", use_container_width=True):
                if not demo_query or not demo_query.strip():
                    st.error("❌ Please enter a question first!")
                    return
                
                # Show question being asked
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        margin: 1.5rem 0;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    ">
                        <div style="color: #1f2937; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">YOUR QUESTION</div>
                        <div style="color: #111827; font-size: 1.2rem; font-weight: 500;">{demo_query}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Create two columns for side-by-side comparison
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 1.5rem;
                            border-radius: 12px;
                            text-align: center;
                            margin-bottom: 1rem;
                            box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
                        ">
                            <h3 style="color: white; margin: 0; font-size: 1.5rem;">📚 Conventional RAG</h3>
                            <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 0.95rem;">Vector Search Only</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    conventional_placeholder = st.empty()
                    conventional_placeholder.info("🔄 Processing...")
                
                with col_right:
                    st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            padding: 1.5rem;
                            border-radius: 12px;
                            text-align: center;
                            margin-bottom: 1rem;
                            box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
                        ">
                            <h3 style="color: white; margin: 0; font-size: 1.5rem;">🧠 Hybrid RAG</h3>
                            <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 0.95rem;">LangGraph + Tables</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    hybrid_placeholder = st.empty()
                    hybrid_placeholder.info("🔄 Processing...")
                
                # Call the comparison API
                try:
                    response = requests.post(
                        f"{self.api_client.endpoint}/compare",
                        json={
                            "query": demo_query,
                            "pdf_uuid": st.session_state.current_pdf_uuid
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display Conventional RAG result
                        with col_left:
                            conv = data.get("conventional_rag", {})
                            if conv.get("success"):
                                conventional_placeholder.markdown(f"""
                                    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                                                border-left: 4px solid #f5576c; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                        <div style="color: #1f2937; margin-bottom: 1rem;">
                                            <strong style="color: #f5576c;">Answer:</strong><br>
                                            <span style="line-height: 1.6;">{conv.get('answer', 'No answer')}</span>
                                        </div>
                                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0;">
                                        <div style="color: #6b7280; font-size: 0.9rem;">
                                            <strong>⏱️ Time:</strong> {conv.get('processing_time', 0):.2f}s<br>
                                            <strong>📋 Method:</strong> {conv.get('description', 'Vector search')}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                conventional_placeholder.error(f"❌ Error: {conv.get('error', 'Unknown error')}")
                        
                        # Display Hybrid RAG result
                        with col_right:
                            hyb = data.get("hybrid_rag", {})
                            if hyb.get("success"):
                                hybrid_placeholder.markdown(f"""
                                    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                                                border-left: 4px solid #00f2fe; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                        <div style="color: #1f2937; margin-bottom: 1rem;">
                                            <strong style="color: #00f2fe;">Answer:</strong><br>
                                            <span style="line-height: 1.6;">{hyb.get('answer', 'No answer')}</span>
                                        </div>
                                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0;">
                                        <div style="color: #6b7280; font-size: 0.9rem;">
                                            <strong>⏱️ Time:</strong> {hyb.get('processing_time', 0):.2f}s<br>
                                            <strong>🎯 Query Type:</strong> {hyb.get('query_type', 'unknown')}<br>
                                            <strong>📋 Method:</strong> {hyb.get('description', 'LangGraph manager')}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                hybrid_placeholder.error(f"❌ Error: {hyb.get('error', 'Unknown error')}")
                        
                        # Analysis section
                        st.markdown("---")
                        st.markdown("""
                            <div style="text-align: center; margin: 2rem 0 1rem 0;">
                                <h3 style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">📊 Analysis</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        conv_time = data.get("conventional_rag", {}).get("processing_time", 0)
                        hyb_time = data.get("hybrid_rag", {}).get("processing_time", 0)
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if conv_time and hyb_time:
                                faster = "Conventional RAG" if conv_time < hyb_time else "Hybrid RAG"
                                st.info(f"**⚡ Faster:** {faster}")
                        
                        with col_b:
                            st.success("""
**🎯 Key Insights:**
- **Conventional RAG** searches text only  
- **Hybrid RAG** routes to tables intelligently  
- Better accuracy for structured data
                            """)
                        
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        with st.expander("Error Details"):
                            st.code(response.text)
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Comparison error: {e}", exc_info=True)
        
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "Comparison Mode Rendering",
                "Error rendering comparison mode"
            )

class PDFUploader:
    """Handles PDF upload functionality with enhanced error handling"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def render_upload_interface(self):
        """Render PDF upload interface in sidebar with comprehensive error handling"""
        try:
            # Simple header
            st.sidebar.header("📄 Document Upload")
            
            # Simple file uploader - no excessive styling
            uploaded_file = st.sidebar.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                key="pdf_uploader"
            )
            
            if uploaded_file is not None:
                # Display file info
                file_size = len(uploaded_file.getvalue())
                file_size_mb = file_size / (1024 * 1024)
                
                st.sidebar.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                        <div style="font-size: 0.85rem;">
                            <strong>📄 {uploaded_file.name}</strong><br>
                            <span style="opacity: 0.9;">Size: {file_size_mb:.2f} MB</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Simple upload button
                if st.sidebar.button("🚀 Upload & Process", type="primary", use_container_width=True):
                    self._handle_pdf_upload(uploaded_file, process_mode="normal")
                    
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "PDF Upload Interface",
                "Error in upload interface"
            )








    def _handle_pdf_upload(self, pdf_file, process_mode="normal"):
        """Handle PDF file upload with simple spinner
        
        Args:
            pdf_file: The uploaded PDF file
            process_mode: Processing mode
        """
        try:
            import time
            
            # Store PDF content for preview
            pdf_content = pdf_file.getvalue()
            
            # Show spinner in main area (st.spinner is the correct API, not st.sidebar.spinner)
            with st.spinner("⏳ Processing your document..."):
                start_time = time.time()
                upload_result = self.api_client.upload_pdf(pdf_file, process_mode=process_mode)
                elapsed = time.time() - start_time
            
            if upload_result.get('success'):
                # Store PDF info and content in session state
                logger.info(f"pdf uuid: {upload_result.get('pdf_uuid')}")
                st.session_state.current_pdf_uuid = upload_result.get('pdf_uuid')
                st.session_state.current_pdf_name = upload_result.get('filename')
                st.session_state.pdf_display_name = upload_result.get('filename')
                st.session_state.pdf_content = pdf_content
                
                # Success message
                st.sidebar.success(f"✅ Upload successful! ({elapsed:.1f}s)")
                logger.info(f"PDF uploaded successfully: {pdf_file.name}")
                
                time.sleep(1)
                st.rerun()
                
            else:
                error_msg = upload_result.get('error', 'Unknown error')
                st.sidebar.error(f"❌ Upload failed: {error_msg}")
                    
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "PDF Upload Handler",
                "Unexpected error during upload"
            )

class StreamlitApp:
    """Main application class with comprehensive error handling"""
    
    def __init__(self):
        self._configure_page()
        self._setup_error_handling()
        self.api_client = self._initialize_api_client()
        if self.api_client:
            self.chat_ui = ChatUI(self.api_client)
            self.pdf_uploader = PDFUploader(self.api_client)
    
    def _configure_page(self):
        """Configure Streamlit page settings"""
        try:
            st.set_page_config(
                page_title="Hybrid RAG Assistant",
                page_icon="🧠",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'About': "Hybrid RAG - Intelligent Document Query System\n\nProcesses both text and tables from PDFs for accurate answers."
                }
            )
            logger.info("Streamlit page configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Streamlit page: {str(e)}")
    
    def _setup_error_handling(self):
        """Setup global error handling"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            logger.info("Error handling setup completed")
        except Exception as e:
            logger.error(f"Failed to setup error handling: {str(e)}")
    
    def _initialize_api_client(self) -> Optional[APIClient]:
        """Initialize API client with error handling"""
        try:
            return APIClient()
        except ConfigurationError as e:
            # Configuration errors are already handled by ErrorHandler
            st.info("Please check the troubleshooting guide below:")
            with st.expander("🔧 Configuration Help"):
                st.markdown("""
                **Setup Steps:**
                1. Create a `.env` file in your project directory
                2. Add your endpoint: `ENDPOINT=https://your-api-endpoint.com`
                3. Restart the application
                
                **File Structure:**
                ```
                your-project/
                ├── app.py
                ├── .env          ← Create this file
                ├── requirements.txt
                └── README.md
                ```
                """)
            st.stop()
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "API Client Initialization",
                "Failed to initialize the application"
            )
            st.stop()
    
    def run(self):
        """Run the main application with error boundaries"""
        try:
            # Modern, clean CSS styling with excellent readability
            st.markdown("""
            <style>
                /* Import modern font */
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                /* Main app - clean white background */
                .stApp {
                    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }
                
                /* Sidebar - modern design with ALWAYS visible text */
                section[data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
                    border-right: none;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                }
                
                /* Force ALL sidebar text to be white and visible */
                section[data-testid="stSidebar"] *,
                section[data-testid="stSidebar"] span,
                section[data-testid="stSidebar"] p,
                section[data-testid="stSidebar"] div,
                section[data-testid="stSidebar"] label,
                section[data-testid="stSidebar"] button,
                section[data-testid="stSidebar"] summary,
                section[data-testid="stSidebar"] a {
                    color: #ffffff !important;
                }
                
                section[data-testid="stSidebar"] .stMarkdown {
                    color: #ffffff !important;
                }
                
                section[data-testid="stSidebar"] h1,
                section[data-testid="stSidebar"] h2,
                section[data-testid="stSidebar"] h3 {
                    color: #ffffff !important;
                    font-weight: 600 !important;
                }
                
                /* Main content text - dark and readable */
                .stApp .main * {
                    color: #1f2937;
                }
                
                .stApp .main h1 {
                    color: #111827 !important;
                    font-weight: 700 !important;
                    font-size: 2.5rem !important;
                    margin-bottom: 0.5rem !important;
                }
                
                .stApp .main h2 {
                    color: #1f2937 !important;
                    font-weight: 600 !important;
                }
                
                .stApp .main h3 {
                    color: #374151 !important;
                    font-weight: 600 !important;
                }
                
                /* Chat messages - better styling */
                .stChatMessage {
                    background-color: #f9fafb !important;
                    border: 1px solid #e5e7eb !important;
                    border-radius: 12px !important;
                    padding: 1.5rem !important;
                    margin: 1rem 0 !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }
                
                /* File uploader - clean styling with visible text */
                section[data-testid="stFileUploader"] {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    padding: 1rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                
                section[data-testid="stFileUploader"] label {
                    color: #ffffff !important;
                    font-weight: 500 !important;
                    font-size: 1rem !important;
                }
                
                /* File uploader dropzone - ensure text is visible */
                section[data-testid="stFileUploaderDropzone"] {
                    background: rgba(255, 255, 255, 0.2) !important;
                    border: 2px dashed rgba(255, 255, 255, 0.5) !important;
                    border-radius: 10px !important;
                    padding: 1.5rem !important;
                }
                
                section[data-testid="stFileUploaderDropzone"] * {
                    color: #ffffff !important;
                    font-weight: 500 !important;
                }
                
                section[data-testid="stFileUploaderDropzone"] small {
                    color: rgba(255, 255, 255, 0.9) !important;
                }
                
                section[data-testid="stFileUploaderDropzone"]:hover {
                    background: rgba(255, 255, 255, 0.25) !important;
                    border-color: rgba(255, 255, 255, 0.7) !important;
                }
                
                /* Buttons - modern gradient */
                .stButton > button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                    font-weight: 600 !important;
                    border: none !important;
                    padding: 0.75rem 2rem !important;
                    border-radius: 8px !important;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                    transition: all 0.3s ease !important;
                }
                
                .stButton > button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
                }
                
                /* Primary buttons in sidebar - ALWAYS visible text */
                section[data-testid="stSidebar"] .stButton > button {
                    background: rgba(255, 255, 255, 0.2) !important;
                    backdrop-filter: blur(10px) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    color: #ffffff !important;
                    font-weight: 600 !important;
                }
                
                /* Browse files button - ensure ALWAYS visible */
                section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
                section[data-testid="stSidebar"] button[kind="secondary"] {
                    color: #ffffff !important;
                    background: rgba(255, 255, 255, 0.25) !important;
                    border: 1px solid rgba(255, 255, 255, 0.4) !important;
                    font-weight: 600 !important;
                }
                
                section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
                section[data-testid="stSidebar"] button[kind="secondary"]:hover {
                    background: rgba(255, 255, 255, 0.35) !important;
                    border-color: rgba(255, 255, 255, 0.6) !important;
                }
                
                /* Chat input */
                .stChatInput {
                    border-radius: 12px !important;
                    border: 2px solid #e5e7eb !important;
                    background-color: #ffffff !important;
                }
                
                .stChatInput input {
                    color: #1f2937 !important;
                    font-size: 1rem !important;
                }
                
                /* Alerts and info boxes */
                .stAlert {
                    border-radius: 12px !important;
                    border: none !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
                }
                
                /* Success message */
                .stSuccess {
                    background-color: #d1fae5 !important;
                    color: #065f46 !important;
                }
                
                /* Info message */
                .stInfo {
                    background-color: #dbeafe !important;
                    color: #1e40af !important;
                }
                
                /* Warning message */
                .stWarning {
                    background-color: #fef3c7 !important;
                    color: #92400e !important;
                }
                
                /* Error message */
                .stError {
                    background-color: #fee2e2 !important;
                    color: #991b1b !important;
                }
                
                /* Radio buttons - ensure text is ALWAYS visible */
                .stRadio > label {
                    color: #1f2937 !important;
                    font-weight: 600 !important;
                }
                
                .stRadio > div {
                    display: flex;
                    justify-content: center;
                    gap: 1rem;
                }
                
                .stRadio label[data-baseweb="radio"] {
                    background-color: white !important;
                    padding: 0.75rem 1.5rem !important;
                    border-radius: 8px !important;
                    border: 2px solid #e5e7eb !important;
                    transition: all 0.3s ease !important;
                }
                
                /* Radio button text - unselected state */
                .stRadio label[data-baseweb="radio"] > div {
                    color: #1f2937 !important;
                    font-weight: 500 !important;
                    font-size: 1rem !important;
                }
                
                .stRadio label[data-baseweb="radio"]:hover {
                    border-color: #667eea !important;
                    background-color: #f5f7fa !important;
                }
                
                /* Selected radio button */
                .stRadio label[data-baseweb="radio"][data-checked="true"] {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    border-color: #667eea !important;
                }
                
                /* Radio button text - selected state */
                .stRadio label[data-baseweb="radio"][data-checked="true"] > div {
                    color: #ffffff !important;
                    font-weight: 600 !important;
                }
                
                /* Ensure ALL text inside radio buttons is visible */
                .stRadio label[data-baseweb="radio"] * {
                    color: #1f2937 !important;
                }
                
                .stRadio label[data-baseweb="radio"][data-checked="true"] * {
                    color: #ffffff !important;
                }
                
                /* Radio input (the actual circle) */
                .stRadio input[type="radio"] {
                    accent-color: #667eea !important;
                }
                
                /* Expander - ALWAYS visible text */
                .streamlit-expanderHeader {
                    background-color: rgba(255, 255, 255, 0.15) !important;
                    border-radius: 8px !important;
                    color: #ffffff !important;
                }
                
                section[data-testid="stSidebar"] .streamlit-expanderHeader,
                section[data-testid="stSidebar"] summary,
                section[data-testid="stSidebar"] details summary {
                    color: #ffffff !important;
                    font-weight: 600 !important;
                    background: rgba(255, 255, 255, 0.15) !important;
                    border-radius: 8px !important;
                    padding: 0.75rem !important;
                }
                
                section[data-testid="stSidebar"] .streamlit-expanderHeader:hover,
                section[data-testid="stSidebar"] summary:hover,
                section[data-testid="stSidebar"] details summary:hover {
                    background: rgba(255, 255, 255, 0.25) !important;
                }
                
                /* Expander content text */
                section[data-testid="stSidebar"] details div,
                section[data-testid="stSidebar"] .streamlit-expanderContent {
                    color: #ffffff !important;
                }
                
                section[data-testid="stSidebar"] details div *,
                section[data-testid="stSidebar"] .streamlit-expanderContent * {
                    color: #ffffff !important;
                }
                
                /* Hide Streamlit branding */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                
                /* Caption text */
                .stCaptionContainer {
                    color: #6b7280 !important;
                }
                
                /* Ensure SVG icons in sidebar are visible */
                section[data-testid="stSidebar"] svg,
                section[data-testid="stSidebar"] .material-icons,
                section[data-testid="stSidebar"] i {
                    fill: #ffffff !important;
                    color: #ffffff !important;
                    opacity: 1 !important;
                }
                
                /* Strong text elements in sidebar */
                section[data-testid="stSidebar"] strong,
                section[data-testid="stSidebar"] b,
                section[data-testid="stSidebar"] em {
                    color: #ffffff !important;
                }
                
                /* List items in sidebar */
                section[data-testid="stSidebar"] li,
                section[data-testid="stSidebar"] ul,
                section[data-testid="stSidebar"] ol {
                    color: #ffffff !important;
                }
                
                /* Code blocks in sidebar */
                section[data-testid="stSidebar"] code,
                section[data-testid="stSidebar"] pre {
                    color: #ffffff !important;
                    background: rgba(0, 0, 0, 0.2) !important;
                }
                
                /* UNIVERSAL RULE: Override any inline styles that hide text in sidebar */
                section[data-testid="stSidebar"] [class*="st-"] {
                    color: #ffffff !important;
                }
                
                section[data-testid="stSidebar"] [class*="emotion-cache"] {
                    color: #ffffff !important;
                }
                
                /* Ensure the dropdown arrow icon is visible */
                section[data-testid="stSidebar"] summary::before,
                section[data-testid="stSidebar"] summary::after {
                    color: #ffffff !important;
                    opacity: 1 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Render sidebar (PDF upload)
            self.pdf_uploader.render_upload_interface()
            
            # Add sidebar info with better design
            with st.sidebar:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show PDF preview if available
                if st.session_state.pdf_content and st.session_state.current_pdf_uuid:
                    st.markdown("### 📄 Document Preview")
                    # Create a download button for the PDF
                    st.download_button(
                        label="📥 Download PDF",
                        data=st.session_state.pdf_content,
                        file_name=st.session_state.current_pdf_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Display PDF using iframe
                    base64_pdf = base64.b64encode(st.session_state.pdf_content).decode('utf-8')
                    pdf_display = f'''
                        <div style="background: white; border-radius: 8px; padding: 8px; margin: 10px 0;">
                            <iframe 
                                src="data:application/pdf;base64,{base64_pdf}" 
                                width="100%" 
                                height="300" 
                                type="application/pdf"
                                style="border-radius: 6px; border: 1px solid rgba(255,255,255,0.3);"
                            ></iframe>
                        </div>
                    '''
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Quick guide
                with st.expander("📘 Quick Guide", expanded=True):
                    st.markdown("""
                    **Getting Started:**
                    
                    1. 📤 Upload a PDF document  
                    2. 🚀 Click "Upload & Process"  
                    3. ⏳ Wait for processing  
                    4. 💬 Ask your questions  
                    
                    **Best Results:**
                    - Documents with tables  
                    - Clear text formatting  
                    - Searchable PDFs (not scanned images)
                    """)
                
                # System capabilities
                with st.expander("🎯 System Capabilities", expanded=False):
                    st.markdown("""
                    **Hybrid RAG Features:**
                    
                    ✨ Text extraction & understanding  
                    ✨ Table data processing with SQL  
                    ✨ Semantic search with embeddings  
                    ✨ Intelligent query routing (LangGraph)  
                    ✨ Context-aware responses  
                    """)
                
                # Footer info
                st.markdown("---")
                st.markdown("""
                    <div style="text-align: center; font-size: 0.85rem; opacity: 0.9;">
                        <p style="margin: 5px 0;"><strong>Powered by</strong></p>
                        <p style="margin: 5px 0;">🧠 LangGraph</p>
                        <p style="margin: 5px 0;">⚡ Gemini AI • Pinecone • PostgreSQL</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Render main chat interface
            self.chat_ui.render_chat_interface()
            
        except Exception as e:
            ErrorHandler.log_error(
                e,
                "Main Application",
                "Critical application error"
            )
            st.error("A critical error occurred. Please refresh the page.")
    
    def _display_connection_status(self):
        """Display API connection status in sidebar"""
        try:
            with st.sidebar:
                st.markdown("### 🔗 Connection Status")
                
                # Test connection button
                if st.button("Test Connection", help="Test API connectivity"):
                    with st.spinner("Testing connection..."):
                        try:
                            response = requests.head(self.api_client.endpoint, timeout=5)
                            if response.status_code < 500:
                                st.success("✅ Connected")
                            else:
                                st.warning(f"⚠️ Server issues (Status: {response.status_code})")
                        except requests.exceptions.RequestException:
                            st.error("❌ Connection failed")
                        except Exception as e:
                            st.error(f"❌ Test failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error displaying connection status: {str(e)}")

def main():
    """Application entry point with top-level error handling"""
    try:
        logger.info("Starting PDF Assistant Chatbot application")
        app = StreamlitApp()
        app.run()
    except Exception as e:
        logger.critical(f"Critical application failure: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        st.error("🚨 Critical application error. Please check the logs and restart.")

if __name__ == "__main__":
    main()
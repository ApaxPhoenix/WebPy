import socket
import threading
import json
from typing import Callable, Dict, Any, Optional, List, Tuple, TypeVar, cast

# Enhanced type variables for improved type safety
T = TypeVar("T", bound=Callable[..., Any])
HandlerType = Callable[[Any, socket.socket], None]


class WebSocket:
    """
    Lightweight WebSocket server implementation with event-driven architecture.

    Provides real-time bidirectional communication capabilities between server and clients
    using a simple event-based model similar to Socket.IO but with reduced complexity.
    The server manages concurrent client connections through threading, handles the complete
    connection lifecycle, and offers flexible message broadcasting.

    Key capabilities:
    - Decorator-based event handler registration
    - Structured communication using JSON message format
    - Automatic client connection management
    - Efficient broadcasting to connected clients
    - Thread-based concurrency for handling multiple clients
    """

    def __init__(self, app: Any):
        """
        Construct a new WebSocket server instance.

        Parameters:
            app: Parent app context that provides access to
                         shared resources, configuration, and services
        """
        self.app = app
        # Active client connection registry
        self.clients: List[socket.socket] = []
        # Event handlers mapped by event name
        self.handlers: Dict[str, HandlerType] = {}

    def on(self, channel: str) -> Callable[[T], T]:
        """
        Register event handlers through a decorator pattern.

        Creates a binding between an event channel name and a handler function.
        When messages arrive with a matching channel name, the corresponding
        handler is invoked with the message payload and client socket.

        Parameters:
            channel: Event identifier that triggers this handler

        Returns:
            Decorator function that registers the handler
        """

        def registration(function: T) -> T:
            """
            Internal decorator implementation that stores handler references.

            Parameters:
                function: Event handler function to register

            Returns:
                Original handler function (unmodified)
            """
            # Register the handler function for the specified event
            self.handlers[channel] = cast(HandlerType, function)
            return function

        return registration

    def emit(self, channel: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Broadcast an event to all connected clients.

        Serializes the event channel and payload as JSON and distributes
        it to all active connections. Automatically handles cleanup of
        disconnected clients during the broadcasting process.

        Parameters:
            channel: Event identifier recognized by clients
            payload: Optional data to send with the event (defaults to empty dict)

        Side effects:
            - Removes disconnected clients from the active clients list
            - Sends messages to all connected clients
        """
        # Prepare JSON message with channel and payload
        packet = json.dumps({"event": channel, "data": payload or {}})
        packet = packet.encode("utf-8")

        # Track disconnected clients for cleanup
        disconnected = []

        # Attempt to send to all clients
        for socket in self.clients:
            try:
                socket.sendall(packet)
            except (BrokenPipeError, ConnectionResetError):
                # Mark failed connections for cleanup
                disconnected.append(socket)

        # Remove disconnected clients from registry
        for socket in disconnected:
            if socket in self.clients:
                self.clients.remove(socket)

    def handle(self, socket: socket.socket, address: Tuple[str, int]) -> None:
        """
        Manage individual client connection lifecycle.

        Runs in a dedicated thread for each client and processes:
        - Message reception and parsing
        - Event dispatch to registered handlers
        - Connection monitoring and error handling
        - Resource cleanup on disconnection

        Parameters:
            socket: Client connection socket object
            address: Client network address as (host, port)
        """
        # Register client in active connections
        self.clients.append(socket)
        print(f"Client connected from {address}")

        try:
            # Process messages until client disconnects
            while True:
                # Receive data with buffer size of 1024 bytes
                data = socket.recv(1024).decode("utf-8")

                # Empty data indicates client disconnection
                if not data:
                    break

                try:
                    # Parse received JSON message
                    message = json.loads(data)

                    # Extract event channel and payload
                    channel = message.get("event")
                    payload = message.get("data", {})

                    # Dispatch to registered handler if found
                    if channel in self.handlers:
                        self.handlers[channel](payload, socket)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received from {address}")

        except ConnectionResetError:
            # Handle unexpected client disconnection
            print(f"Connection reset by client {address}")
        except Exception as error:
            # Log unexpected errors during message processing
            print(f"Error processing client {address}: {str(error)}")
        finally:
            # Ensure proper cleanup regardless of termination cause
            print(f"Client disconnected from {address}")
            if socket in self.clients:
                self.clients.remove(socket)
            socket.close()

    def run(self, host: str = "127.0.0.1", port: int = 8081) -> None:
        """
        Launch the WebSocket server and begin accepting connections.

        Creates a server socket, binds to the specified network interface,
        and enters an acceptance loop that creates a new thread for each
        incoming client connection.

        Parameters:
            host: Network interface address to bind to (default: localhost)
            port: TCP port to listen on (default: 8081)

        Notes:
            - This method blocks indefinitely until interrupted
            - The server automatically handles resource cleanup on exit
            - Client connections are managed in separate daemon threads
        """
        # Create TCP socket with IPv4 addressing
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Configure socket for address reuse
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to specified interface and port
        server.bind((host, port))

        # Listen with connection backlog of 5
        server.listen(5)
        print(f"WebSocket server running on ws://{host}:{port}")

        try:
            # Primary connection acceptance loop
            while True:
                # Wait for incoming client connection
                client, location = server.accept()

                # Create dedicated thread for this client
                worker = threading.Thread(
                    target=self.handle, args=(client, location)
                )
                # Set as daemon thread for automatic cleanup
                worker.daemon = True
                worker.start()

        except KeyboardInterrupt:
            # Handle graceful shutdown on Ctrl+C
            print("Server shutting down...")
        finally:
            # Ensure server socket is properly closed
            server.close()
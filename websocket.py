import socket
import threading
import json
from typing import Callable, Dict, Any, Optional, List, Tuple, TypeVar, cast

# Type variables for better type hinting
T = TypeVar("T", bound=Callable[..., Any])
EventHandler = Callable[[Any, socket.socket], None]


class WebSocket:
    """
    A lightweight WebSocket server implementation that provides event-based communication
    similar to Socket.IO but with a simpler architecture.

    This class enables real-time bidirectional communication between server and clients
    through an event-driven architecture. It handles multiple client connections
    concurrently using threading, manages connection lifecycle, and provides methods
    for both receiving and broadcasting messages.

    Features:
    - Event registration through decorators
    - JSON-based message format for structured communication
    - Automatic connection management and cleanup
    - Broadcast capability to all connected clients
    """

    def __init__(self, app: Any):
        """
        Initialize the WebSocket server with application context.

        Args:
            app (Any): Parent application instance that this WebSocket server
                      will be associated with. This allows the WebSocket server
                      to access application resources and configuration.
        """
        self.app = app
        # Store active client connections for broadcasting messages
        self.connections: List[socket.socket] = []
        # Map event names to their handler functions
        self.events: Dict[str, EventHandler] = {}

    def on(self, event: str) -> Callable[[T], T]:
        """
        Decorator to register handler functions for specific events.

        When a client sends a message with the specified event name, the decorated
        function will be called with the message data and client socket as arguments.

        Args:
            event (str): The event name to listen for in incoming messages.

        Returns:
            Callable[[T], T]: Decorator function that registers the handler.
        """

        def decorator(handler: T) -> T:
            """
            Inner decorator function that registers the handler in the events dictionary.

            Args:
                handler (T): Function to be called when the event is received.

            Returns:
                T: The original handler function (unchanged).
            """
            # Store the handler function in the events dictionary
            self.events[event] = cast(EventHandler, handler)
            return handler

        return decorator

    def emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Broadcast an event with optional data to all connected clients.

        This method serializes the event and data as JSON and sends it to all
        active client connections. It also handles cleanup of disconnected clients.

        Args:
            event (str): Name of the event to emit.
            data (Optional[Dict[str, Any]]): Data payload to send with the event.
                                           Defaults to an empty dictionary if None.
        """
        # Create JSON message with event name and data
        message = json.dumps({"event": event, "data": data or {}})
        message = message.encode("utf-8")

        # Track disconnected clients for cleanup
        clients = []

        # Send message to all connected clients
        for connection in self.connections:
            try:
                connection.sendall(message)
            except (BrokenPipeError, ConnectionResetError):
                # Mark failed connections for removal
                clients.append(connection)

        # Remove disconnected clients from the active connections list
        for client in clients:
            if client in self.connections:
                self.connections.remove(client)

    def connect(self, connection: socket.socket, address: Tuple[str, int]) -> None:
        """
        Handle a client connection in a dedicated thread.

        This method maintains the lifecycle of a single client connection, including:
        - Receiving and parsing messages
        - Dispatching events to registered handlers
        - Handling connection errors and cleanup

        Args:
            connection (socket.socket): Client socket connection object.
            address (Tuple[str, int]): Client address as (host, port) tuple.
        """
        # Register this connection in the active connections list
        self.connections.append(connection)
        print(f"Client connected from {address}")

        try:
            # Message processing loop for this client
            while True:
                # Receive data from client with buffer size of 1024 bytes
                message = connection.recv(1024).decode("utf-8")

                # Empty message indicates client disconnection
                if not message:
                    break

                try:
                    # Parse received JSON message
                    content = json.loads(message)

                    # Extract event name and data payload
                    event = content.get("event")
                    data = content.get("data", {})

                    # Dispatch to registered handler if event exists
                    if event in self.events:
                        self.events[event](data, connection)
                except json.JSONDecodeError:
                    print(f"Received invalid JSON from {address}")

        except ConnectionResetError:
            # Handle case when client disconnects unexpectedly
            print(f"Connection reset by client {address}")
        except Exception as error:
            # Catch and log other unexpected errors
            print(f"Error handling client {address}: {str(error)}")
        finally:
            # Clean up the connection regardless of how it ended
            print(f"Client disconnected from {address}")
            if connection in self.connections:
                self.connections.remove(connection)
            connection.close()

    def run(self, host: str = "127.0.0.1", port: int = 8081) -> None:
        """
        Start the WebSocket server and listen for incoming connections.

        This method sets up the server socket, binds to the specified address,
        and enters a loop that accepts new connections. Each new connection is
        handled in a separate thread.

        Args:
            host (str): IP address to bind the server to.
                       Defaults to "127.0.0.1" (localhost).
            port (int): Port number to listen on. Defaults to 8081.

        Note:
            This method blocks indefinitely until interrupted (e.g., by Ctrl+C).
            The server socket will be properly closed on exit.
        """
        # Create TCP/IP socket using IPv4 addressing
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow socket to reuse the address (prevents "Address already in use" errors)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to specified network interface and port
        server.bind((host, port))

        # Start listening with connection backlog of 5
        server.listen(5)
        print(f"WebSocket server running on ws://{host}:{port}")

        try:
            # Main server loop
            while True:
                # Accept new client connection (blocks until connection arrives)
                connection, address = server.accept()

                # Create and start thread to handle this client connection
                thread = threading.Thread(
                    target=self.connect, args=(connection, address)
                )
                # Set as daemon thread so it terminates when main thread exits
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            # Handle server shutdown on Ctrl+C
            print("Server shutting down...")
        finally:
            # Ensure server socket is closed properly
            server.close()
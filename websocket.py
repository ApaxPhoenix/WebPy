import socket
import threading
import json
from typing import Callable, Dict, Any, Optional, Tuple, TypeVar, cast, List

# Enhanced type definitions for improved type safety and clarity
T = TypeVar("T", bound=Callable[..., Any])
HandlerType = Callable[[Any, socket.socket], None]

# Type aliases for enhanced readability and semantic meaning
ClientId = str
EventChannel = str
EventPayload = Dict[str, Any]
NetworkAddress = Tuple[str, int]
ClientSocket = socket.socket
JsonMessage = str
ClientRegistry = Dict[ClientId, ClientSocket]
HandlerRegistry = Dict[EventChannel, HandlerType]
ServerRegistry = Dict[str, Dict[str, Any]]
HostAddress = str
PortNumber = int


class WebSocket:
    """
    Lightweight WebSocket server implementation with event-driven architecture.

    Provides real-time bidirectional communication capabilities between server and clients
    using a simple event-based model similar to Socket.IO but with reduced complexity.
    The server manages concurrent client connections through threading, handles the complete
    connection lifecycle, and offers flexible message broadcasting with automatic cleanup
    of disconnected clients and comprehensive error handling.
    """

    def __init__(self, app: Any) -> None:
        """
        Construct a new WebSocket server instance.

        Initializes the client registry, event handler mapping, and establishes
        the connection to the parent application context for shared resource access.

        Parameters:
            app: Parent app context that provides access to shared resources,
                 configuration, and services throughout the application lifecycle
        """
        self.app = app
        # Combined registry for clients and event handlers
        # Maps client sockets to their metadata (connection info, active state)
        self.registry: ServerRegistry = {
            "clients": {},  # Maps socket object IDs to socket objects
            "handlers": {},  # Maps event names to handler functions
        }

    def on(self, channel: EventChannel) -> Callable[[T], T]:
        """
        Register event handlers through a decorator pattern.

        Creates a binding between an event channel name and a handler function.
        When messages arrive with a matching channel name, the corresponding
        handler is invoked with the message payload and client socket for
        real-time event processing and response generation.

        Parameters:
            channel: Event identifier that triggers this handler

        Returns:
            Decorator function that registers the handler and preserves original function
        """

        def registration(function: T) -> T:
            """
            Internal decorator implementation that stores handler references.

            Registers the handler function in the event registry for automatic
            invocation when matching events are received from clients.

            Parameters:
                function: Event handler function to register

            Returns:
                Original handler function (unmodified for external use)
            """
            # Register the handler function for the specified event
            self.registry["handlers"][channel] = cast(HandlerType, function)
            return function

        return registration

    def emit(self, channel: EventChannel, payload: Optional[EventPayload] = None) -> None:
        """
        Broadcast an event to all connected clients with automatic cleanup.

        Serializes the event channel and payload as JSON and distributes
        it to all active connections. Automatically handles cleanup of
        disconnected clients during the broadcasting process to maintain
        registry accuracy and prevent resource leaks.

        Parameters:
            channel: Event identifier recognized by clients
            payload: Optional data to send with the event (defaults to empty dict)

        Side effects:
            Removes disconnected clients from the active clients registry
            and sends messages to all connected clients simultaneously
        """
        # Prepare JSON message with channel and payload
        packet: JsonMessage = json.dumps({"event": channel, "data": payload or {}})
        bytes_data: bytes = packet.encode("utf-8")

        # Track disconnected clients for cleanup
        disconnected: List[ClientId] = []

        # Attempt to send to all clients
        identity: ClientId
        client: ClientSocket
        for identity, client in self.registry["clients"].items():
            try:
                client.sendall(bytes_data)
            except (BrokenPipeError, ConnectionResetError):
                # Mark failed connections for cleanup
                disconnected.append(identity)

        # Remove disconnected clients from registry
        for identity in disconnected:
            if identity in self.registry["clients"]:
                del self.registry["clients"][identity]

    def handle(self, client: ClientSocket, address: NetworkAddress) -> None:
        """
        Manage individual client connection lifecycle with comprehensive error handling.

        Runs in a dedicated thread for each client and processes message reception
        and parsing, event dispatch to registered handlers, connection monitoring
        and error handling, plus resource cleanup on disconnection to ensure
        proper memory management and connection state consistency.

        Parameters:
            client: Client connection socket object
            address: Client network address as (host, port) tuple

        Side effects:
            Modifies client registry, processes incoming messages, dispatches events,
            and performs cleanup operations on connection termination
        """
        # Generate unique client ID and register in active connections
        identity: ClientId = f"{address[0]}:{address[1]}_{id(client)}"
        self.registry["clients"][identity] = client
        print(f"Client connected from {address}")

        try:
            # Process messages until client disconnects
            while True:
                # Receive data with buffer size of 1024 bytes
                data: str = client.recv(1024).decode("utf-8")

                # Empty data indicates client disconnection
                if not data:
                    break

                try:
                    # Parse received JSON message
                    message: EventPayload = json.loads(data)

                    # Extract event channel and payload
                    channel: Optional[str] = message.get("event")
                    payload: EventPayload = message.get("data", {})

                    # Dispatch to registered handler if found
                    if channel and channel in self.registry["handlers"]:
                        self.registry["handlers"][channel](payload, client)
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
            if identity in self.registry["clients"]:
                del self.registry["clients"][identity]
            client.close()

    def run(self, host: HostAddress = "127.0.0.1", port: PortNumber = 8081) -> None:
        """
        Launch the WebSocket server and begin accepting connections with graceful shutdown.

        Creates a server socket, binds to the specified network interface,
        and enters an acceptance loop that creates a new thread for each
        incoming client connection. Provides comprehensive error handling
        and graceful shutdown capabilities for production deployment.

        Parameters:
            host: Network interface address to bind to (default: localhost)
            port: TCP port to listen on (default: 8081)

        Notes:
            This method blocks indefinitely until interrupted. The server
            automatically handles resource cleanup on exit, and client
            connections are managed in separate daemon threads for isolation.

        Raises:
            OSError: When unable to bind to the specified host and port
            KeyboardInterrupt: When graceful shutdown is requested
        """
        # Create TCP socket with IPv4 addressing
        server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
                client: ClientSocket
                location: NetworkAddress
                client, location = server.accept()

                # Create dedicated thread for this client
                worker: threading.Thread = threading.Thread(
                    target=self.handle,
                    args=(client, location)
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
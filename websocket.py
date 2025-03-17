import socket
import threading
import json
from typing import Callable, Dict, Any, Optional, List, Tuple, TypeVar, cast

# Type variables for better function typing
T = TypeVar("T", bound=Callable[..., Any])
EventHandler = Callable[[Any, socket.socket], None]


class WebSocket:
    """
    WebSocket class for managing WebSocket connections, event-based communication,
    and real-time message handling similar to Socket.IO.

    This class provides functionality to create a WebSocket server, manage client
    connections, register event handlers, and broadcast messages to connected clients.
    It implements a simplified event-driven architecture for real-time communication.
    """

    def __init__(self, app: Any):
        """
        Initialize the WebSocket with an application instance.

        Sets up internal data structures for tracking client connections and
        event handlers.

        Args:
            app (Any): Application instance with which to register WebSocket connections.
                      This allows integration with the main application.
        """
        self.app = app
        # List to store all active client socket connections
        self.connections: List[socket.socket] = []
        # Dictionary mapping event names to their handler functions
        self.events: Dict[str, EventHandler] = {}

    def on(self, event: str) -> Callable[[T], T]:
        """
        Register a handler function for the specified event.

        This decorator method allows event handlers to be easily defined and
        registered for specific events. When the event is received from a client,
        the corresponding handler will be executed.

        Args:
            event (str): The name of the event to listen for.

        Returns:
            Callable[[T], T]: Decorator function for registering event handlers.

        Example:
            @websocket.on("message")
            def handle_message(data, client_socket):
                # Process incoming message
                print(f"Received message: {data}")
        """

        def decorator(handler: T) -> T:
            """
            Inner decorator function that registers the event handler.

            Args:
                handler (T): The function that will handle the specified event.

            Returns:
                T: The original handler function, unchanged.
            """
            # Register the event handler in the events dictionary
            self.events[event] = cast(EventHandler, handler)
            return handler

        return decorator

    def emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an event to all connected clients with the given data.

        Broadcasts a message with the specified event name and optional data
        to all currently connected clients.

        Args:
            event (str): The name of the event to emit.
            data (Optional[Dict[str, Any]]): Data payload to send with the event.
                                            Defaults to an empty dictionary.

        Example:
            websocket.emit("notification", {"message": "New update available!"})
        """
        # Create a message in JSON format with the event name and data
        message = json.dumps({"event": event, "data": data or {}})

        # Iterate through all connections and send the message
        clients = []
        for connection in self.connections:
            try:
                # Encode and send the message to the client
                connection.sendall(message.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                # Mark connection for removal if sending fails
                clients.append(connection)

        # Clean up disconnected clients
        for client in clients:
            if client in self.connections:
                self.connections.remove(client)

    def connection(self, conn: socket.socket, address: Tuple[str, int]) -> None:
        """
        Manage an individual WebSocket connection from a client.

        This method runs in a separate thread for each client connection. It handles
        incoming messages, parses JSON data, and calls the appropriate event handlers.

        Args:
            conn (socket.socket): Client connection socket object.
            address (Tuple[str, int]): Client addressess as a tuple of (host, port).
        """
        # Add the client connection to the list of active connections
        self.connections.append(conn)
        print(f"Client connected from {address}")

        try:
            while True:
                # Receive data from the client (up to 1024 bytes)
                message = conn.recv(1024).decode("utf-8")

                # If no message is received, the client has disconnected
                if not message:
                    break

                try:
                    # Parse the received JSON message
                    content = json.loads(message)

                    # Extract the event name and data from the message
                    event = content.get("event")
                    data = content.get("data", {})

                    # Call the appropriate event handler if registered
                    if event in self.events:
                        self.events[event](data, conn)
                except json.JSONDecodeError:
                    print(f"Received invalid JSON from {address}")

        except ConnectionResetError:
            # Handle abrupt client disconnection
            print(f"Connection reset by client {address}")
        except Exception as error:
            # Handle other exceptions
            print(f"Error handling client {address}: {str(error)}")
        finally:
            print(f"Client disconnected from {address}")
            # Remove the client from active connections and close the socket
            if conn in self.connections:
                self.connections.remove(conn)
            conn.close()

    def run(self, host: str = "127.0.0.1", port: int = 8081) -> None:
        """
        Start the WebSocket server and listen for incoming connections.

        This method initializes the server socket, binds it to the specified host
        and port, and starts accepting client connections in separate threads.

        Args:
            host (str): Host IP addressess to bind the server. Defaults to "127.0.0.1" (localhost).
            port (int): Port number to bind the server. Defaults to 8081.

        Note:
            This method runs indefinitely until the program is terminated.
        """
        # Create a new TCP socket using IPv4 addressessing
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set socket option to allow addressess reuse (helpful for server restarts)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the specified host and port
        server.bind((host, port))

        # Listen for incoming connections with a backlog queue of 5
        server.listen(5)
        print(f"WebSocket server running on ws://{host}:{port}")

        try:
            # Continuously accept and handle incoming connections
            while True:
                # Accept a new client connection
                connection, address = server.accept()

                # Start a new thread to handle this client connection
                thread = threading.Thread(
                    target=self.connection, args=(connection, address)
                )
                thread.daemon = (
                    True  # Set as daemon so thread exits when main program does
                )
                thread.start()

        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            # Close the server socket
            server.close()

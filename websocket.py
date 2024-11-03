import socket
import threading
import json
from typing import Callable, Dict, Any, Optional, List


class Socket:
    """
    Basic Socket class for managing WebSocket connections, event-based communication,
    and real-time message handling similar to Socket.IO.
    """

    def __init__(self, app: Any):
        """
        Initialize the Socket class with an app instance.
        Args:
            app: Application instance with which to register socket connections.
        """
        self.app = app
        # List to store all active client connections
        self.connections: List[socket.socket] = []
        # Dictionary to store event handlers, mapping event names to functions
        self.events: Dict[str, Callable[[Any, Any], None]] = {}

    def on(self, event: str) -> Callable:
        """
        Listen for an event by registering a handler for the specified event name.
        Args:
            event (str): The name of the event to listen for.
        Returns:
            Callable: Decorator for event handler function.
        """

        def decorator(handler: Callable) -> Callable:
            """
            Decorator function to register event handler.
            Args:
                handler: The function that handles the event.
            Returns:
                The original handler function, registered in the events dictionary.
            """
            # Register the event handler for the specified event
            self.events[event] = handler
            return handler

        return decorator

    def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None):
        """
        Emit an event to all connected clients with the given data.
        Args:
            event_name (str): The name of the event to emit.
            data (Optional[Dict[str, Any]]): Data to send with the event.
        """
        # Create a message in JSON format containing the event and its associated data
        message = json.dumps({"event": event_name, "data": data or {}})

        # Send the message to all connected clients
        for connection in self.connections:
            try:
                # Send message to the client
                connection.sendall(message.encode("utf-8"))
            except BrokenPipeError:
                # If the connection is broken, remove the client
                self.connections.remove(connection)

    def connection(self, conn: socket.socket, addr: tuple) -> None:
        """
        Manage the WebSocket connection, handle incoming messages, and trigger event handlers.
        Args:
            conn (socket.socket): Client connection socket.
            addr (tuple): Address of the connected client.
        """
        # Add the client connection to the list of active connections
        self.connections.append(conn)
        print(f"Connected to {addr}")

        try:
            while True:
                # Receive messages from the client, decode them as UTF-8
                message = conn.recv(1024).decode("utf-8")

                # If no message is received, exit the loop
                if not message:
                    break

                # Parse the received JSON message
                content = json.loads(message)
                # Get the event name and data from the message
                event = content.get("event")
                data = content.get("data")

                # If the event is registered, call its handler with the data and connection
                if event in self.events:
                    self.events[event](data, conn)
        except ConnectionResetError:
            # Handle client disconnection
            pass
        finally:
            print(f"Disconnected from {addr}")
            # Remove the client from active connections
            self.connections.remove(conn)
            conn.close()

    def run(self, host: str = "127.0.0.1", port: int = 8081) -> None:
        """
        Start the WebSocket server and listen for incoming connections.
        Args:
            host (str): Host IP address to bind the server.
            port (int): Port number to bind the server.
        """
        # Create a new socket for the server (IPv4, TCP)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow address reuse for faster restarts
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the server to the specified host and port
        server.bind((host, port))
        # Start listening for incoming connections (with a backlog of 5)
        server.listen(5)
        print(f"WebSocket server running on ws://{host}:{port}")

        # Continuously accept and handle incoming connections
        while True:
            # Accept new client connections
            connection, address = server.accept()
            # Start a new thread to manage the client connection
            threading.Thread(target=self.connection, args=(connection, address)).start()
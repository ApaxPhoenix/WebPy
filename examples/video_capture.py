import cv2
from webpy.webpy import WebPy


class VideoServer:
    def __init__(self):
        # Initialize video capture from the default camera (index 0)
        self.video_capture = cv2.VideoCapture(0)

    def home(self, request, response):
        # HTML content for the home page with the video feed
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OpenCV Video Feed</title>
        </head>
        <body>
            <h1>Live Video Feed</h1>
            <!-- Video feed element -->
            <img id="video_feed" alt="Video Feed">
            <script>
                // Define the video feed element
                const video = document.getElementById('video_feed');

                function updateVideo() {
                    // Fetch the video feed from the server
                    fetch('/feed')
                        .then(response => response.blob())
                        .then(blob => {
                            // Update the video source with the new frame
                            video.src = URL.createObjectURL(blob);
                            // Schedule the next update
                            requestAnimationFrame(updateVideo);
                        });
                }

                // Trigger video feed update when the window loads
                window.onload = updateVideo;
            </script>
        </body>
        </html>
        """
        # Set response headers and body with the HTML content
        response.headers['Content-Type'] = 'text/html'
        response.body = html_content.encode('utf-8')

    def feed(self, request, response):
        # Read a frame from the video capture
        ret, frame = self.video_capture.read()
        if ret:
            # Encode the frame as JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            # Convert the frame to bytes
            frame_bytes = jpeg.tobytes()
            # Set response headers with content type
            response.headers['Content-Type'] = 'image/jpeg'
            # Set response body with the frame bytes
            response.body = frame_bytes
        else:
            # Send an error response if failed to capture frame
            response.send_error(500, "Failed to capture frame from video feed")


# Create a WebPy instance
web_app = WebPy()
# Create a VideoServer instance
video_server = VideoServer()
# Register routes for the home page and video feed
web_app.route("/", methods=['GET'])(video_server.home)
web_app.route("/feed", methods=['GET'])(video_server.feed)
# Run the web application
web_app.run()

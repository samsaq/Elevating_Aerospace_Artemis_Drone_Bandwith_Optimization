# simple script to fetch a few seconds of video from webcam

import cv2
import time
import os

debug = True


# function to fetch x seconds of video from webcam
def fetch_video_file(seconds, output_filename="VideoData/output.avi", codec="XVID"):
    start_time = time.time()

    # Initialize video capture
    cap = cv2.VideoCapture(0)

    # Get camera FPS and calculate total frames needed
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30  # Default to 30 if FPS detection fails

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*codec)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))

    # Calculate total frames needed
    total_frames = seconds * fps

    frames_captured = 0
    encoding_time = 0

    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        frames_captured += 1

        # Time the encoding/writing operation
        write_start = time.time()
        out.write(frame)
        encoding_time += time.time() - write_start

        # Display the frame
        cv2.imshow("frame", frame)

        # Wait for 1/fps seconds (to maintain proper timing)
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord("q"):  # cancel if q is pressed
            break

    total_time = time.time() - start_time

    # Get final file size
    file_size = os.path.getsize(output_filename) / (1024 * 1024)  # Size in MB

    print(f"\nPerformance metrics for {codec} codec:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Encoding time: {encoding_time:.2f} seconds")
    print(f"Frames captured: {frames_captured}")
    print(f"Output file size: {file_size:.2f} MB")
    print(
        f"Average encoding time per frame: {(encoding_time/frames_captured)*1000:.2f} ms"
    )

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def get_video_stream(seconds=None):
    """
    Generator function that yields frames from webcam stream
    Args:
        seconds: Optional duration in seconds. If None, streams indefinitely
    Yields:
        frame: numpy array containing the video frame
    """
    # Initialize video capture
    cap = cv2.VideoCapture(0)

    # Get camera FPS
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30  # Default to 30 if FPS detection fails

    # Calculate total frames if seconds specified
    total_frames = None
    if seconds is not None:
        total_frames = seconds * fps

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret or (total_frames and frame_count >= total_frames):
            break

        yield frame
        frame_count += 1

        # Maintain proper timing
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord("q"):  # cancel if q is pressed
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()


# get video stream from file
def get_video_stream_from_file(filename):
    cap = cv2.VideoCapture(filename)
    return cap


if debug:
    # TODO: Add H264, AV1/AVIF testing
    # print("Comparing codec performance...")
    # for codec in [
    #     "MJPG",
    #     "XVID",
    #     "mp4v",
    # ]:  # note we can't test H246 since it doesn't have proper windows support without manually compiling FFMPEG
    #     print(f"\nTesting {codec}...")
    #     fetch_video_file(
    #         5, output_filename=f"VideoData/output_{codec}.avi", codec=codec
    #     )

    # record a video
    fetch_video_file(10, output_filename="VideoData/output.avi", codec="XVID")

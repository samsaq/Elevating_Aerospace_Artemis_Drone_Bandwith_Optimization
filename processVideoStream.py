# using video files (eg: from fetchVideoStream.py or from file)
# process them to minimize used bandwidth when the resulting video is streamed out

# This for drone video processing (eg: streaming a video of drone POV of an aircraft to analyze)

import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim

debug = True


# strip out long periods of no motion
# period threshold is the number of seconds that must pass with global motion to be removed
# use optical flow for this kind of global motion detection
# motion_threshold is the threshold for what constitutes significant motion (0.0 to 1.0) - this needs to be tuned and is very low typically
def strip_drone_movement(video_file, period_threshold=0.5, motion_threshold=0.15):
    """
    Strips out periods of significant drone movement from video using optical flow.
    Now uses a grid-based approach to better detect global camera motion.

    Args:
        video_file: Path to input video file
        period_threshold: Number of seconds of continuous motion to trigger removal
        motion_threshold: Threshold for what constitutes significant motion (0.0 to 1.0)
    """
    # Ensure VideoData directory exists
    os.makedirs("VideoData", exist_ok=True)

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_file}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_threshold = int(fps * period_threshold)

    # Get video writer ready
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output_path = os.path.join("VideoData", "strip_drone_movement_output.avi")
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (int(cap.get(3)), int(cap.get(4))),
    )

    if not out.isOpened():
        cap.release()
        raise ValueError(f"Could not create output video writer at: {output_path}")

    # Read first frame
    ret, old_frame = cap.read()
    if not ret:
        return

    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    motion_count = 0
    keep_frame = True

    # Calculate grid size for motion analysis
    grid_size = 16  # Divide frame into 16x16 grid

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        # Analyze flow in grid cells
        h, w = flow.shape[:2]
        cell_h, cell_w = h // grid_size, w // grid_size
        motion_scores = []

        for i in range(grid_size):
            for j in range(grid_size):
                # Get flow for this grid cell
                cell_flow = flow[
                    i * cell_h : (i + 1) * cell_h, j * cell_w : (j + 1) * cell_w
                ]

                # Calculate average flow vector for this cell
                avg_flow = cv2.mean(cell_flow)[:2]  # Get x,y components

                # Calculate flow magnitude for this cell
                cell_magnitude = (avg_flow[0] ** 2 + avg_flow[1] ** 2) ** 0.5
                motion_scores.append(cell_magnitude)

        # Use median of cell motions to detect global movement
        # This is more robust than mean for detecting camera motion
        motion_value = np.median(motion_scores)
        normalized_motion = min(
            1.0, motion_value / 10.0
        )  # Normalize with better scaling

        # Check if motion exceeds threshold
        if normalized_motion > motion_threshold:
            motion_count += 1
        else:
            if motion_count < frames_threshold:
                keep_frame = True
            motion_count = 0

        if motion_count >= frames_threshold:
            keep_frame = False

        if keep_frame:
            out.write(frame)

        if debug:
            cv2.putText(
                frame,
                f"Motion: {normalized_motion:.3f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0) if normalized_motion <= motion_threshold else (0, 0, 255),
                2,
            )
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        old_gray = frame_gray

    cap.release()
    out.release()
    cv2.destroyAllWindows()


# strip out long periods of no motion
# keep_segment_length is the number of seconds to keep from the start of the segment of no motion
# keep_every_n_frames is to keep a frame every n frames within the segment of no motion
# period_threshold is the number of seconds that must pass with no motion to be removed
# using yolo to detect motion
def strip_no_motion(
    video_file,
    period_threshold=3,
    keep_segment_length=1,
    keep_every_n_frames=30,  # roughly 1 frame per second at 30fps
):
    pass


# strip out similar frames
def strip_similar_frames(video_file, frame_threshold=3, similarity_threshold=0.95):
    """
    Strips out similar frames from video using SSIM comparison.
    Keeps only the first frame_threshold frames when similar frames are detected.

    Args:
        video_file: Path to input video file
        frame_threshold: Number of initial frames to keep from similar sequences
        similarity_threshold: Threshold for what constitutes similar frames (0.0 to 1.0)
                            Higher values mean more similar (e.g., 0.95)
    """
    # Ensure VideoData directory exists
    os.makedirs("VideoData", exist_ok=True)

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_file}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get video writer ready
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output_path = os.path.join("VideoData", "strip_similar_frames_output.avi")
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (int(cap.get(3)), int(cap.get(4))),
    )

    if not out.isOpened():
        cap.release()
        raise ValueError(f"Could not create output video writer at: {output_path}")

    prev_frame = None
    similar_sequence = False
    frames_in_sequence = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        should_write = True  # Default to writing the frame

        if prev_frame is not None:
            similarity = ssim(prev_frame, frame, channel_axis=2)

            if similarity > similarity_threshold:
                # We're in a sequence of similar frames
                if not similar_sequence:
                    # Start of a new similar sequence
                    similar_sequence = True
                    frames_in_sequence = 1
                else:
                    frames_in_sequence += 1
                    # Only write if we're still within our threshold
                    should_write = frames_in_sequence <= frame_threshold
            else:
                # Different frame detected, reset sequence
                similar_sequence = False
                frames_in_sequence = 0

            if debug:
                cv2.putText(
                    frame,
                    f"Similarity: {similarity:.3f} Seq: {frames_in_sequence}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0) if should_write else (0, 0, 255),
                    2,
                )

        if should_write:
            out.write(frame)

        prev_frame = frame.copy()

        if debug:
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if debug:
        # strip_drone_movement("VideoData/Motionful_output.avi")
        strip_similar_frames("VideoData/Motionful_output.avi")

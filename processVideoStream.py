# using video files (eg: from fetchVideoStream.py or from file)
# process them to minimize used bandwidth when the resulting video is streamed out

# This for drone video processing (eg: streaming a video of drone POV of an aircraft to analyze)

import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim
import torch
from ultralytics import YOLO

debug = False


# strip out long periods of no motion
# period threshold is the number of seconds that must pass with global motion to be removed
# use optical flow for this kind of global motion detection
# motion_threshold is the threshold for what constitutes significant motion (0.0 to 1.0) - this needs to be tuned and is very low typically
def strip_drone_movement(
    video_file,
    period_threshold=0.5,
    motion_threshold=0.15,
    grid_size=16,
    output_file="VideoData/strip_drone_movement_output.avi",
):
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
    out = cv2.VideoWriter(
        output_file,
        fourcc,
        fps,
        (int(cap.get(3)), int(cap.get(4))),
    )

    if not out.isOpened():
        cap.release()
        raise ValueError(f"Could not create output video writer at: {output_file}")

    # Read first frame
    ret, old_frame = cap.read()
    if not ret:
        return

    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    motion_count = 0
    keep_frame = True

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

    if debug:
        input_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # Size in MB
        print(f"Input file size: {input_size:.2f} MB")
        print(f"Output file size: {output_size:.2f} MB")
        print(f"Size ratio: {output_size/input_size:.2%}")


# strip out long periods of no motion
# keep_segment_length is the number of seconds to keep from the start of the segment of no motion
# keep_every_n_frames is to keep a frame every n frames within the segment of no motion
# period_threshold is the number of seconds that must pass with no motion to be removed
# using yolo to detect motion
def strip_no_motion(
    video_file,
    period_threshold=1,
    keep_segment_length=1,
    keep_every_n_frames=30,
    motion_threshold=0.15,
    grid_size=32,
    output_file="VideoData/strip_no_motion_output.avi",
):
    """
    Strips out periods of no motion using optical flow.

    Args:
        video_file: Path to input video file
        period_threshold: Number of seconds with no motion before starting to skip
        keep_segment_length: Number of seconds to keep at start of no-motion period
        keep_every_n_frames: Keep 1 frame every n frames during no-motion periods
        motion_threshold: Threshold for what constitutes significant motion (0.0 to 1.0)
        grid_size: Number of cells to divide frame into for motion analysis
    """
    # Ensure VideoData directory exists
    os.makedirs("VideoData", exist_ok=True)

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_file}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_threshold = int(fps * period_threshold)
    keep_frames_threshold = int(fps * keep_segment_length)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    no_motion_count = 0
    frame_count = 0
    in_no_motion_segment = False

    # Add variables for optical flow
    ret, old_frame = cap.read()
    if not ret:
        return
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        should_write = True

        # Calculate optical flow
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        # Analyze flow in grid cells
        h, w = flow.shape[:2]
        cell_h, cell_w = h // grid_size, w // grid_size
        motion_scores = []

        for i in range(grid_size):
            for j in range(grid_size):
                cell_flow = flow[
                    i * cell_h : (i + 1) * cell_h, j * cell_w : (j + 1) * cell_w
                ]
                avg_flow = cv2.mean(cell_flow)[:2]
                cell_magnitude = (avg_flow[0] ** 2 + avg_flow[1] ** 2) ** 0.5
                motion_scores.append(cell_magnitude)

        # Use median of cell motions to detect movement
        motion_value = np.median(motion_scores)
        normalized_motion = min(1.0, motion_value / 10.0)

        # Check for motion - inverted logic from strip_drone_movement
        if normalized_motion < motion_threshold:
            no_motion_count += 1
        else:
            no_motion_count = 0
            in_no_motion_segment = False

        # Check if we've reached the no-motion threshold
        if no_motion_count >= frames_threshold:
            in_no_motion_segment = True

            # Calculate frames since start of no-motion
            frames_since_start = no_motion_count - frames_threshold

            # Keep initial segment
            if frames_since_start < keep_frames_threshold:
                should_write = True
            # Keep periodic frames
            else:
                should_write = (frames_since_start % keep_every_n_frames) == 0

        if should_write:
            out.write(frame)

        if debug:
            cv2.putText(
                frame,
                f"Motion: {normalized_motion:.3f}, No motion frames: {no_motion_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0) if not in_no_motion_segment else (0, 0, 255),
                2,
            )

            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        old_gray = frame_gray

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if debug:
        input_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # Size in MB
        print(f"Input file size: {input_size:.2f} MB")
        print(f"Output file size: {output_size:.2f} MB")
        print(f"Size ratio: {output_size/input_size:.2%}")


# strip out similar frames
def strip_similar_frames(
    video_file,
    frame_threshold=3,
    similarity_threshold=0.9,
    output_file="VideoData/strip_similar_frames_output.avi",
):
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

    # Get input video properties
    input_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Try to use the same codec as input, fallback to XVID if not possible
    try:
        out = cv2.VideoWriter(
            output_file,
            input_fourcc,  # Use input video's codec
            fps,
            (width, height),
        )
        if not out.isOpened():
            raise ValueError("Failed to open with input codec")
    except:
        print("Warning: Could not use input codec, falling back to XVID")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(
            output_file,
            fourcc,
            fps,
            (width, height),
        )

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

    if debug:
        input_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB
        output_size = os.path.getsize("VideoData/strip_similar_frames_output.avi") / (
            1024 * 1024
        )  # Size in MB
        print(f"Input file size: {input_size:.2f} MB")
        print(f"Output file size: {output_size:.2f} MB")
        print(f"Size ratio: {output_size/input_size:.2%}")


# combine all three functions and calculate the size ratio that is achieved
def process_video(video_file, output_file="VideoData/processed_video.avi"):
    initial_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB

    # Create intermediate filenames
    temp_file1 = "VideoData/temp_step1.avi"
    temp_file2 = "VideoData/temp_step2.avi"

    # Process steps with different input/output files
    strip_drone_movement(video_file, output_file=temp_file1)
    strip_no_motion(temp_file1, output_file=temp_file2)
    strip_similar_frames(temp_file2, output_file=output_file)

    # Clean up temporary files
    if os.path.exists(temp_file1):
        os.remove(temp_file1)
    if os.path.exists(temp_file2):
        os.remove(temp_file2)

    final_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
    print(f"Input file size: {initial_size:.2f} MB")
    print(f"Output file size: {final_size:.2f} MB")
    print(f"Size ratio: {final_size/initial_size:.2%}")


if __name__ == "__main__":
    if debug:
        # strip_drone_movement("VideoData/Motionful_output.avi")
        # strip_similar_frames("VideoData/Motionful_output.avi")
        strip_no_motion("VideoData/Motionful_output.avi")
    else:
        process_video("VideoData/Motionful_output.avi")

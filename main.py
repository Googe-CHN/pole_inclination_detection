from tilt_detector import TiltDetector, LineMerger
from utils import ResultsHandler, LineExtender, PolygonRetriever
import os
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--image', type=str, help='Path to an image.')
    parser.add_argument('--folder', type=str, help="Path to a folder with images to process")
    parser.add_argument('--save_path', type=str, default=None, help="If None, don't save results, show them")

    parser.add_argument('--retrieve', type=int, default=0, help="Retrieve image section defined by the two pole"
                                                                "edge lines detected")
    arguments = parser.parse_args()

    return arguments


def main():

    arguments = parse_args()

    assert arguments.image or arguments.folder, "No input data provided"

    images_to_process = list()

    if arguments.image:

        if os.path.isfile(arguments.image):
            images_to_process.append(arguments.image)
        else:
            print("ERROR: Provided image is not an image")
            sys.exit()

    else:
        if not os.path.isdir(arguments.folder):
            print("ERROR: Provided folder is not a folder")
            sys.exit()

        for image_name in os.listdir(arguments.folder):
            if not any(image_name.endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".JPG", ".JPEG", ".PNG"]):
                continue

            images_to_process.append(os.path.join(arguments.folder, image_name))

    # If save path has been provided, all images will be processed and saved there
    # Otherwise, after each image gets processed it will be shown to a user until
    # he clicks a button to proceed to the next image if any.
    # In order to just calculate and receive angle = flag is 0

    if arguments.save_path is not None:
        if not os.path.exists(arguments.save_path):
            os.mkdir(arguments.save_path)

        results_handling = 1, arguments.save_path
        handler = ResultsHandler(save_path=arguments.save_path)
    else:
        results_handling = 0, ''
        handler = None

    merger = LineMerger()

    detector = TiltDetector(results_handling_way=results_handling,
                            line_merger=merger,
                            results_processor=handler)

    total_error = 0
    images_with_calculated_angles = 0
    images_without_angle_calculated = []

    for path_to_image in images_to_process:

        image_name = os.path.split(path_to_image)[-1]
        print(image_name)

        truth_angle = float(image_name[3:7])
        predicted_tilt_angle, the_lines = detector.process_image(path_to_image)

        if predicted_tilt_angle is not None:
            difference = abs(truth_angle - predicted_tilt_angle)
            error = round(difference / truth_angle, 3)
            print("Error:", error)

            total_error += error
            images_with_calculated_angles += 1
        else:
            images_without_angle_calculated.append(image_name)

        assert the_lines and 1 <= len(the_lines) <= 2, "Wrong number of lines!"

        if arguments.retrieve and the_lines:
            line_extender = LineExtender()
            polygon_retriever = PolygonRetriever(line_extender=line_extender)

            polygon_matrix = polygon_retriever.retrieve_polygon(path_to_image,
                                                                the_lines)


    mean_error = round(total_error / images_with_calculated_angles, 3)
    print("\nMEAN ERROR:", mean_error * 100, "%")

    if images_without_angle_calculated:
        print("FAILED TO CALCULATE ANGLE FOR:",
              ' '.join(map(str, images_without_angle_calculated)))


if __name__ == "__main__":
    main()

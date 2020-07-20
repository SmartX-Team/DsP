import sys
import os
import yaml


def load_setting():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "setting.yaml")

    with open(file_path, 'r') as stream:
        try:
            file_str = stream.read()
            if file_str:
                _setting = yaml.load(file_str, Loader=yaml.FullLoader)
            else:
                exit(1)
        except yaml.YAMLError as exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                exit(1)

    return _setting["mode"].lower()


if __name__ == "__main__":
    mode: str = ""
    if len(sys.argv) == 2:
        mode = sys.argv[1].lower()
    else:
        mode = load_setting()

    if mode == "post":
        from post import __main__
        __main__.main()

    elif mode == "tower":
        from tower import __main__
        __main__.main()

    else:
        print("Execution Failed")

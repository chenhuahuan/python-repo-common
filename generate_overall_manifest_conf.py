import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

file_list = ["a_manifest.conf", "b_manifest.conf", "c_manifest.conf"]

# {"ss_util": ["develop","eagle"]}
project_dict = dict()


def generate_overall_manifest_conf(src_file_list, dest_file="overall.conf"):

    def validate_manifest_conf(two_lines):
        print(two_lines)
        assert isinstance(two_lines, list) and len(two_lines) == 2, "ERROR: Lines must contain only two line."
        assert '=' in two_lines[0] and '=' in two_lines[1], "ERROR: No = in line."
        project_key = ini_string_lines[0].split('=', maxsplit=1)[0]
        branch_key = ini_string_lines[1].split('=', maxsplit=1)[0]
        assert project_key == "p" and branch_key == "b", "ERROR: Wrong manifest format! Should be match: p=xxx, b=xxx"

    for file in src_file_list:
        with open(os.path.join(ROOT_DIR, file), 'r', encoding="utf-8") as cfg:
            ini_string_lines = cfg.read().splitlines()
            print(ini_string_lines)
            for i in range(0, len(ini_string_lines), 2):
                validate_manifest_conf(ini_string_lines[i:i+2])

                project = ini_string_lines[i].split('=', maxsplit=1)[1].strip()
                branch = ini_string_lines[i + 1].split('=', maxsplit=1)[1].strip()

                print(ini_string_lines[i])
                if project not in project_dict:
                    project_dict[project] = [branch]
                elif branch not in project_dict[project]:
                    project_dict[project].append(branch)

    print(project_dict)

    with open(dest_file, 'w', encoding="utf-8") as fp:
        str_concat = ""
        for project, branch_list in project_dict.items():
            for branch in branch_list:
                str_concat += "p={}\n".format(project)
                str_concat += "b={}\n".format(branch)
                str_concat += "t~.*[^\s]\n"
        fp.write(str_concat)

    print(str_concat)


generate_overall_manifest_conf(file_list)




def read_git_release(version):
    branches_list = []
    with open("releases/release-v{}".format(version), "r") as stream:
        try:
            for line in stream:
                line = line.strip()
                if len(line) > 0:
                    branches_list.append(line)
        except:
            pass
        finally:
            stream.close()

    return branches_list


def write_git_release(version, branches):
    with open("releases/release-v{}".format(version), "w") as stream:
        try:
            stream.writelines(map(lambda x: "\n" + x, branches))
            # Write one last linebreak to be compatible for legacy mygit-release
            stream.write("\n")
        except:
            pass
        finally:
            stream.close()

    return

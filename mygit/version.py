def write_version(release_dict):
    with open("version", "w") as stream:
        try:
            stream.writelines("release-v{}-rc{}".format(release_dict['version'], release_dict['candidate']))
        except:
            pass
        finally:
            stream.close()

    return

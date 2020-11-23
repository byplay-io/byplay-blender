import logging
import platform


def plugin_version():
    return (1, 0, 1)


def sys_info():
    sysname, nodename, release, version, machine, _processor = platform.uname()

    blender_version = "unk"
    try:
        import bpy
        blender_version = bpy.app.version_string
    except Exception as e:
        logging.error(e)

    return {
        "blender.version": blender_version,
        "os.name": sysname,
        "node.name": nodename,
        "os.release": release,
        "os.version": version
    }
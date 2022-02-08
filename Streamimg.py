from datetime import datetime
import os
import platform


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


# print(creation_date('static/sv_im/db_image.png'))
img_st_mtime = os.stat('static/sv_im/box.png').st_mtime
str_time = datetime.fromtimestamp(img_st_mtime).strftime("%H:%M:%S")
print(str_time)

current_time = datetime.now().strftime("%H:%M:%S")

FMT = '%H:%M:%S'
tdelta = datetime.strptime(current_time, FMT) - datetime.strptime("15:56:00", FMT)

print(str(tdelta))

if int(str(tdelta).split(':')[1]) > 0 or int(str(tdelta).split(':')[-1]) > 5:
    print('No New Images')

    print('Old Images Deleted')
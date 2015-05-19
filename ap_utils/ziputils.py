import os
import zipfile


def zipdir(dir_path, zip_file_path=None, include_dir_in_zip=True):
    """Zips the given directory including all files and folders recursively.
       Supports large (>4Gb) files. """

    if not zip_file_path:
        zip_file_path = dir_path + ".zip"
    if not os.path.isdir(dir_path):
        raise OSError("dir_path argument must point to a directory. '{0}' does not.".format(dir_path))
        
    parent_dir, dir_to_zip = os.path.split(dir_path)
    
    #Little nested function to prepare the proper archive path
    def trim_path(path):
        archive_path = path.replace(parent_dir, "", 1)
        if parent_dir:
            archive_path = archive_path.replace(os.path.sep, "", 1)
        if not include_dir_in_zip:
            archive_path = archive_path.replace(dir_to_zip + os.path.sep, "", 1)
        return os.path.normcase(archive_path)

    #set allowZip64=True to allow large files
    out_file = zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True)
    for (archive_dir_path, dir_names, file_names) in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(archive_dir_path, file_name)
            out_file.write(file_path, trim_path(file_path))
            
        #Make sure we get empty directories as well
        if not file_names and not dir_names:
            zipInfo = zipfile.ZipInfo(trim_path(archive_dir_path) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            out_file.writestr(zipInfo, "")
    out_file.close()
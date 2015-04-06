import os
import zipfile


def zipdir(dir_path, zip_file_path=None, include_dir_in_zip=True):
    """Zips the given directory including all files and folders recursively.
       Supports large (>4Gb) files. """

    if not zip_file_path:
        zip_file_path = dir_path + ".zip"
    if not os.path.isdir(dir_path):
        raise OSError("dir_path argument must point to a directory. "
            "'%s' does not." % dir_path)
        
    parentDir, dir_to_zip = os.path.split(dir_path)
    
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not include_dir_in_zip:
            archivePath = archivePath.replace(dir_to_zip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    #set allowZip64=True to allow large files
    outFile = zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dir_path):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
            
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()
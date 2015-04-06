import os
import shutil
import stat

                    
def rmtree_with_readonly(path, ignore_errors=False, onerror=None) :
    """As shutil.rmtree() but can also delete read-only files."""
    
    #Remove read-only attribute recursively
    for root, dirs, files in os.walk(path, topdown=False):
        for fname in files:
            full_path = os.path.join(root, fname)
            os.chmod(full_path, stat.S_IWRITE)
        
    #delete
    return shutil.rmtree(path, ignore_errors, onerror)


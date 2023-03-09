from pathlib import Path
import os, re
import numpy as np
from pyunpack import Archive

__all__= ["FindFiles", "seek_to_unzip"]

ZIP_CHR= set(['.rar','.zip','.RAR','.ZIP'])

def __type(obj):
    pattern= re.compile(r"^<\w+..(\w+).>$")
    pattern.search(str(type(obj))).group(1)
    return pattern.search(str(type(obj))).group(1)


VALID_TYPES= (dict, list)


def _is_unzipable(exten: list | str) -> bool:

    # if exten=str --->  set([str]) to avoid  set('asdf')= {'a','s','d','f'} 
    extension= set([exten]) if isinstance(exten,str) else set(exten)

    if not extension.intersection(ZIP_CHR):
        return False
    return True

def _unzip(path:Path) -> Path:
    '''
    unzip files and drop it in folder with the same source and name.

    : param path: source where zip file has been found

    '''
    dst= Path(path.parent,path.stem)
    dst.mkdir() if not dst.exists() else None

    Archive(path).extractall(dst)
    os.remove(path)
    return dst

def __cast(obj,typereturn, extension= None):
    '''
    Casting obj variable to pass list-> dict and vice versa
    '''

    if typereturn not in VALID_TYPES:
        raise TypeError("El tipo de datos devuelto ha de ser <class '{}'>\nNo <class '{}'>".format("'> o <'".join([__type(x()) for x in VALID_TYPES]), __type(typereturn)))


    TYPE= type(obj)

    # no hacemos nada
    if TYPE== type(None):
        return []
    
    # len(obj)==1 or TYPE== typereturn:
    if TYPE== typereturn:
        return obj

    # casting (list()) from dict()
    if TYPE != 'list':
        merged= list()
        for x in list(obj.values()):
            if x:
                if isinstance(x,(list,tuple)):
                    for x in x:
                        merged.append(x)
                else:
                    merged.append(x)

        return merged

    #casting (dict()) from list()
    if TYPE != 'dict' and extension:
        dicc= dict()
        dicc[extension]= obj

        return dicc

def __FindFiles(src:Path, extension) ->list | dict:
    zip_files= []
    all_files= []
    #update root
    #all_files:np.array= np.array([Path(root,name) for root,_,names in os.walk(src) for name in names])
    for root,_,names in os.walk(src):
        for name in names:
            # Checking if zip files exists
            if Path(name).suffix in ZIP_CHR:
                zip_files.append(Path(root, name))
            else:
                all_files.append(Path(root,name)) 

    zip_files= np.array(zip_files)
    all_files= np.array(all_files)


    # extension== ZIP_CHR ----> when call _FindFiles([src,ZIP_CHR])
    if (_is_unzipable(extension) and extension== ZIP_CHR) or isinstance(extension,(list,tuple)) :
        dicc:dict= {}
        for x in extension:
            dicc[x]= __FindFiles(src, x)

        # Always cast to get list if extension is zip_chr
        if _is_unzipable(extension) and extension== ZIP_CHR:
            return __cast(dicc,'list')

        return dicc
            
    # Getting bool array if True extension have been found and False if do not
    bool_files= np.array(list(map(lambda x: True if x.suffix== extension else False, all_files)))
    res= all_files[bool_files== True].tolist()


    if not (len(res)) > 0: # Hit if extension did not found

        # if file is unzipable, We do not want to unzip it, only seek it
        # if there is files unziples
        if  _is_unzipable(extension) or len(zip_files)== 0:
            return None

        # Seek zip files and try to unzip it
        new_files= []
        for x in zip_files:
            folder= _unzip(x)
            files= __FindFiles(folder, extension)
            if files != None:
                new_files.append(files)
        # found_files again   
        return [el for lista in new_files for el in lista]
    
    return res

def seek_to_unzip(src: Path):
    __FindFiles(src= src, extension= "~")

def FindFiles(src:Path, extension, typereturn= list):
    """
    Param 
        :src:        Ruta donde se quiere conocer si existe algun archivo cuya extension sea {extension}
        :extension:  extension del archivo que se desea buscar
        :typereturn: puede ser "list" o "dict" y sirve devolver los datos con un tipo de datos u otro
    """

    files=__FindFiles(src, extension)
    return __cast(obj= files, extension= extension, typereturn= typereturn)

def __FindFilesToString(src:Path, string:str | list):
    if isinstance(string, list|tuple):
        param= "|".join(string)
        pattern= re.compile(rf"({param})", flags=re.IGNORECASE)
    else:
        pattern= re.compile(rf"{string}", flags=re.IGNORECASE)

    for root,_,names in os.walk(src):
        for name in names:
            match= pattern.match(name)
            if match != None:
                yield Path(root, name)

def FindFilesToString(src:Path, string:str| list):
    return list(__FindFilesToString(src,string))

__all__.append(FindFilesToString)





if __name__== "__main__":
    
    ruta= Path.home()/'Downloads'

    a= FindFilesToString(ruta, '[^~].')
    a= FindFiles(ruta, [''], list)
    [print(x) for x in a]

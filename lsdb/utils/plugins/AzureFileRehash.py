class AzureFileRehash():
    def __init__(self):
        pass

    def _test(self):
        pass

    def _run(self, file_count):
        import hashlib
        from lsdb.models import AzureFile

        hasher = hashlib.new('sha256')
        response_dict={}
        file_list=AzureFile.objects.filter(hash_algorithm='md5')[:int(file_count)]
        # return {'file_count':file_count}
        for tohash in file_list:
            # tohash = AzureFile.objects.get(id=file_id)
            oldhash=tohash.hash
            for buf in tohash.file.file.chunks(chunk_size = 65536):
                hasher.update(buf)
                tohash.hash_algorithm='sha256'
                tohash.hash=hasher.hexdigest()
                tohash.save()
            response_dict[str(tohash.id)]={"calculated":hasher.hexdigest(),
            "stored":oldhash}
        return response_dict

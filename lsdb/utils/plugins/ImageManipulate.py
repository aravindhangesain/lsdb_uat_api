class ImageManipulate():
    from PIL import Image, ImageOps
    from lsdb.models import AzureFile
    from io import BytesIO
    from django.utils import timezone
    import zipfile
    from django.http import FileResponse, HttpResponse

    def __init__(self):
        self.image_id = 85

    def _run(self):
        mem_zip = self.BytesIO()
        with self.zipfile.ZipFile(mem_zip, mode='w', compression=self.zipfile.ZIP_DEFLATED) as zf:
            azurefile = self.AzureFile.objects.get(id=self.image_id)
            bytes = self.BytesIO(azurefile.file.file.read())
            bytes.seek(0)
            tempImage = self.Image.open(bytes)
            width, height = tempImage.size
            tempImage = tempImage.rotate(-90, expand=True)
            tempImage = tempImage.resize((height, width))
            tempImage = self.ImageOps.grayscale(tempImage)
            tempImage = self.ImageOps.autocontrast(tempImage)

            image_bytes = self.BytesIO()
            tempImage.save(image_bytes, format="PNG")
            tempImage.close()
            image_bytes.seek(0)

            zf.writestr('{}/{}'.format('images',azurefile.file.name),image_bytes.getvalue())
        filename=self.timezone.now().strftime('%b-%d-%Y-%H%M%S')
        response = self.HttpResponse(mem_zip.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(filename)
        return response

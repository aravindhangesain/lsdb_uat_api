from django.db import models


class Template(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=False, null=False, unique=True)  # db_index provided by unique=True
    description = models.CharField(max_length=256, blank=False, null=False)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)  # report vs email?
    body_source = models.TextField(blank=True, null=True)
    subject_source = models.TextField(blank=True, null=True)
    format = models.ForeignKey('FileFormat', blank=False, on_delete=models.CASCADE)  # html, txt, xlsx,

    # Other things to consider for this:
    #   - variables Required
    #   - may need to change data type of the body.

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)

class HasFileWithName():
    """
    This plugin will accept two parameters: an object to interrogate and a string to
    look for in the attachment file names.

    This plugin cannot be run from the Plugins UI. It must be called from
    inside the server via ActionCompletionCriteria or similar.

    Plugin Params:
        "search_string":"foo"
        "obj": model object with "attachments"
    """
    from lsdb.models import AzureFile
    from lsdb.models import Project

    def __init__(self):
        self.a = None

    def _test(self):
        project:object = self.Project.objects.get(id=1)
        pos_string:str = 'starship-troopers'
        positive = self._run(obj=project.attachments, search_string=pos_string)

        neg_string:str = 'johnny'
        negative = self._run(obj=project.attachments, search_string=neg_string)
        # we want to return True
        return(positive == True and negative == False)


    def _run(self:object, obj:object, search_string:str):
        for attachment in obj.all():
            if search_string.upper() in attachment.name.upper():
                return True
        return(False)

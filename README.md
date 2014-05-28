django-ajaxadmin
================

Simple out-of-the-box multiple file upload widget for Django admin site. Based on jQuery Upload File plugin.

Quick start
-----------

1. Add "ajaxadmin" to your INSTALLED_APPS setting **BEFORE** `django.contrib.admin`
or any other admin replacement (like django-suit or grappelli):

        INSTALLED_APPS = (
            'ajaxadmin',
            'django.contrib.admin',
            ...
        )

2. Inherit your ModelAdmin class from `ajaxadmin.admin.AjaxMultiuploadAdmin`:

        from ajaxadmin.admin import AjaxMultiuploadAdmin

        class MyModelAdmin(AjaxMultiuploadAdmin):
            ...

3. Suppose you've got the following model relationship:

        class Parent(models.Model):
            ...

        class MyImage(models.Model):
            parent = models.ForeignKey(Parent)
            img = models.ImageField(upload_to='my_images')
            img_thumbnail = models.ImageField(upload_to='my_images/thumbnails')

    Than to add admin ajax widget, simply do this:

            class MyModelAdmin(AjaxMultiuploadAdmin):
                ...
        
            MyModelAdmin.add_ajax_input(MyImage, 'parent', 'img', 'img_thumbnail')
        
            admin.site.register(MyImage, MyModelAdmin)

    Here 'parent' is a name of foreign key field, 'img' is a name of file field (could be ImageField or FileField), and 'img_thumbnail' (it's optional) is a name of thumbnail field.

4. Then in any of your admin templates (override `admin/change_form.html`, for example) do the following:

        {% extends "admin/change_form.html" %}
        {% load i18n %}
        {% load staticfiles %}
        {% load ajaxadmin %}

        {% block extrahead %}{{ block.super }}

        <!-- You're gonna need jQuery-cookie and jQuery-Upload-File static files -->
        <script type="text/javascript" src="{% static "js/jquery.cookie.js" %}"></script>
        <link href="http://hayageek.github.io/jQuery-Upload-File/uploadfile.min.css" rel="stylesheet">
        <script src="http://hayageek.github.io/jQuery-Upload-File/jquery.uploadfile.min.js"></script>

        {% endblock extrahead %}

        {% block after_field_sets %}{{ block.super }}

        <h2>My ajax uploader</h2>
        {% uploader "myapp_name" "parent" "myimage" original 230 150 %}

        {% endblock after_field_sets %}

    Here 'myapp_name' stands for django application name, 'parent' is parent model name, 'myimage' is child model name. 230 and 150 are optional width/height restrictions that could be ommited.

5. That's all! Now you can upload a lot of files at once right in your precious django admin.

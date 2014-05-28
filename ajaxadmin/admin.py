from django.contrib import admin
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.core.context_processors import csrf

from ajaxadmin.models import TempFile

import json


class AjaxMultiuploadAdmin(admin.ModelAdmin):

    ajax_models = {}

    def change_view(self, request, object_id, **kwargs):
        if request.method == 'POST':
            obj = self.model.objects.get(pk=object_id)
            ajax_action = request.POST.get('action', None)
            if ajax_action == 'add':
                return self.add_ajax_item(request, obj=obj)
            elif ajax_action == 'get':
                return self.get_ajax_items(request, obj=obj)
            elif ajax_action == 'delete':
                self.delete_ajax_item(request, obj=obj)
                return HttpResponse(json.dumps([request.POST['name']]))
        return super(AjaxMultiuploadAdmin, self).change_view(request, object_id, **kwargs)

    def add_view(self, request, *args, **kwargs):
        if request.method == 'POST':
            ajax_action = request.POST.get('action', None)
            if ajax_action == 'add':
                return self.add_ajax_item(request)
            elif ajax_action == 'get':
                return self.get_ajax_items(request)
            elif ajax_action == 'delete':
                self.delete_ajax_item(request)
                return HttpResponse(json.dumps([request.POST['name']]))
        return super(AjaxMultiuploadAdmin, self).add_view(request, *args, **kwargs)

    def add_ajax_item(self, request, obj=None):
        model_name = request.POST.get('model', "").lower()
        if not model_name or model_name not in self.ajax_models:
            return
        file = request.FILES['ajax']
        cls = self.ajax_models[model_name]['class']
        try:
            temp_instance = cls(**{self.ajax_models[model_name]['file_field']: file})
            temp_instance.full_clean()
        except ValidationError as e:
            total_errors = []
            for errlist in e.message_dict.values():
                total_errors += errlist
            return HttpResponse(json.dumps({'jquery-upload-file-error': '\n'.join(total_errors)}))
        if not obj:
            # tempfiles
            t = TempFile(file=file, key=unicode(csrf(request)['csrf_token']), model_name=model_name)
            t.save()
            resp = t.file.name
        else:
            setattr(temp_instance, self.ajax_models[model_name]['fkey_field'], obj)
            temp_instance.save()
            resp = getattr(temp_instance, self.ajax_models[model_name]['file_field']).name
        return HttpResponse(json.dumps([resp]))

    def delete_ajax_item(self, request, obj=None):
        model_name = request.POST.get('model', "").lower()
        if not model_name or model_name not in self.ajax_models:
            return
        filename = request.POST['name']
        cls = self.ajax_models[model_name]['class']
        # despite pk, rm this file from pre-loaded temp files
        temp = TempFile.objects.filter(file=filename)
        if temp:
            temp.delete()
        else:
            filter_args = {
                self.ajax_models[model_name]['fkey_field']: obj,
                self.ajax_models[model_name]['file_field']: filename
            }
            instance = cls.objects.filter(**filter_args)
            if instance:
                instance.delete()

    def get_ajax_items(self, request, obj=None):
        if obj is None:
            return HttpResponse(json.dumps([]))
        model_name = request.POST.get('model', "").lower()
        if not model_name or model_name not in self.ajax_models:
            return
        cls = self.ajax_models[model_name]['class']
        filter_args = {
            self.ajax_models[model_name]['fkey_field']: obj
        }
        objects = cls.objects.filter(**filter_args)
        response = []
        for o in objects:
            item = {
                'name': getattr(o, self.ajax_models[model_name]['file_field']).name
            }
            if self.ajax_models[model_name]['thumbnail_field']:
                try:
                    item['thumbnail'] = getattr(o, self.ajax_models[model_name]['thumbnail_field']).url
                except:
                    pass
            response.append(item)
        return HttpResponse(json.dumps(response))

    def associate_tempfiles(self, obj, key):
        obj.save()  # just in case it hasn't been saved before
        temp_files = TempFile.objects.filter(key=key)
        for temp in temp_files:
            if temp.model_name in self.ajax_models:
                cls = self.ajax_models[temp.model_name]['class']
                kwargs = {
                    self.ajax_models[temp.model_name]['fkey_field']: obj,
                    self.ajax_models[temp.model_name]['file_field']: temp.file
                }
                cls(**kwargs).save()
        temp_files.delete()

    def save_model(self, request, obj, form, change):
        super(AjaxMultiuploadAdmin, self).save_model(request, obj, form, change)
        self.associate_tempfiles(obj, unicode(csrf(request)['csrf_token']))

    @classmethod
    def add_ajax_input(cls, model, fkey_field, file_field, thumbnail_field=None):
        name = model.__name__.lower()
        cls.ajax_models[name] = {
            'fkey_field': fkey_field,
            'file_field': file_field,
            'class': model,
            'thumbnail_field': thumbnail_field
        }

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.utils.encoding import smart_str
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django_select2.forms import Select2MultipleWidget

import os

from .models import File, FileTag
from .forms import FileUploadForm, FileCreateForm, FileEditForm
from .documents import FileDocument

class FileListView(generic.ListView):
    model = File
    template_name = 'file_list.djhtml'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('Search')
        if query:
            # object_list = self.model.objects.filter(Q(name__icontains = query) |
            #                                         Q(description__icontains = query))
            search_obj = FileDocument.search().query(
                'query_string',
                fields=(
                    'name',
                    'description',
                ),
                query=f'*{query}*'
            )
            object_list = search_obj.to_queryset()
        else:
            object_list = self.model.objects.all()
        return object_list


class FileDetailView(generic.DetailView):
    model = File
    template_name = 'file_detail.djhtml'


class FileAnonCreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = FileCreateForm
    template_name = 'file_create.djhtml'
    success_message = 'File was successfully created!'
    creation_type = 'Anonymously'

    def form_valid(self, form):
        if form.cleaned_data.get('text_format') == '.md':
            form.instance.source = SimpleUploadedFile('file.md', form.instance.text.encode('utf-8'))
        elif form.cleaned_data.get('text_format') == '.txt':
            form.instance.source = SimpleUploadedFile('file.txt', form.instance.text.encode('utf-8'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(FileAnonCreateView, self).get_context_data(**kwargs)
        ctx['creation_type'] = self.creation_type
        return ctx

    def get_success_url(self):
        return self.object.get_absolute_url()


class FileAuthCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.edit.CreateView):
    form_class = FileCreateForm
    template_name = 'file_create.djhtml'
    success_message = 'File was successfully created!'
    login_url = 'login'
    creation_type = 'With your account'

    def form_valid(self, form):
        if form.cleaned_data.get('text_format') == '.md':
            form.instance.source = SimpleUploadedFile('file.md', form.instance.text.encode('utf-8'))
        elif form.cleaned_data.get('text_format') == '.txt':
            form.instance.source = SimpleUploadedFile('file.txt', form.instance.text.encode('utf-8'))
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(FileAuthCreateView, self).get_context_data(**kwargs)
        ctx['creation_type'] = self.creation_type
        return ctx

    def get_success_url(self):
        return self.object.get_absolute_url()


class FileAnonUploadView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = FileUploadForm
    template_name = 'file_upload.djhtml'
    success_message = 'File was successfully uploaded!'
    uploading_type = 'Anonymously'

    def get_context_data(self, **kwargs):
        ctx = super(FileAnonUploadView, self).get_context_data(**kwargs)
        ctx['uploading_type'] = self.uploading_type
        return ctx

    def get_success_url(self):
        return self.object.get_absolute_url()

class FileAuthUploadView(LoginRequiredMixin, SuccessMessageMixin, generic.edit.CreateView):
    form_class = FileUploadForm
    template_name = 'file_upload.djhtml'
    success_message = 'File was successfully uploaded!'
    login_url = 'login'
    uploading_type = 'With your account'

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(FileAuthUploadView, self).get_context_data(**kwargs)
        ctx['uploading_type'] = self.uploading_type
        return ctx

    def get_success_url(self):
        return self.object.get_absolute_url()

class FileEditView(LoginRequiredMixin, SuccessMessageMixin, generic.edit.UpdateView):
    model = File
    form_class = FileEditForm
    template_name = 'file_edit.djhtml'
    success_message = 'File was successfully edited!'
    login_url = 'login'

    def form_valid(self, form):
        file_obj = File.objects.get(slug=str(self.kwargs['slug']))
        form.instance.source = SimpleUploadedFile(f'{settings.MEDIA_ROOT}/{form.instance.name}/{form.instance.name}{file_obj.get_ext()}', form.instance.text.encode('utf-8'))
        file_obj.remove_file()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

class FileDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.edit.DeleteView):
    model = File
    template_name = 'file_delete.djhtml'
    success_url = reverse_lazy('file_list')
    success_message = 'File was successfully deleted!'
    login_url = 'login'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(FileDeleteView, self).delete(request, *args, **kwargs)


def fileDownloadView(self, slug):
    file_path = File.objects.get(slug=slug).source.path
    file_name = File.objects.get(slug=slug).name + File.objects.get(slug=slug).get_ext()

    myfile = open(file_path, 'rb')
    response = HttpResponse(myfile, content_type ='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


class TagListView(generic.ListView):
    model = FileTag
    template_name = 'tag_list.djhtml'


class TaggedFileListView(generic.ListView):
    model = File
    template_name = 'file_list.djhtml'
    tagged_list = True

    def get_queryset(self):
        tagslug = self.kwargs['tag']
        tag = FileTag.objects.get(slug=tagslug)
        files = File.objects.filter(tags=tag)
        return files

    def get_context_data(self, **kwargs):
        ctx = super(TaggedFileListView, self).get_context_data(**kwargs)
        ctx['tagged_list'] = self.tagged_list
        return ctx

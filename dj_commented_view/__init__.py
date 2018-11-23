from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin
from django.db.models.query import QuerySet
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms


name = "dj-commented-view"


class CommentBaseMixin(ContextMixin):
    commentmodel = None
    parentfield = None  # The name of the FKey in Comment


# For viewing comments related to the model. Has mixins and stuff.
# Basically https://github.com/django/django/blob/master/django/views/generic/list.py
class CommentListMixin(CommentBaseMixin):
    commentqueryset = None
    commentordering = None

    def get_comment_queryset(self):
        """
        Returns the list of comments for this view.
        """
        if self.commentqueryset is not None:
            queryset = self.commentqueryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.commentmodel is not None:
            queryset = self.commentmodel._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "{0} is missing a QuerySet for comments. Define {0}.commentmodel, {0}.commentqueryset, or override {0}.get_comment_queryset().".format((self.__class__.__name__,))
            )
        ordering = self.get_comment_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset.filter(**{f'{self.parentfield}__exact': self.object})

    def get_comment_ordering(self):
        """Return the field/fields to use for ordering the queryset"""
        return self.commentordering

    # TODO: def paginate_queryset()
    # TODO: def get_paginate_by()
    # TODO: def get_paginator()
    # TODO: get_paginate_orphans()
    # TODO: get_allow_empty()
    # TODO: get_context_object_name()

    def get_context_data(self, **kwargs):
        # TODO: pagination
        context = {'comment_list': self.get_comment_queryset()}
        context.update(kwargs)
        return super().get_context_data(**context)


# A way to show the form for a new comment
class CommentPostMixin(CommentBaseMixin):
    postcommentinitial = {}
    fields = None
    postcomment_success_url = None
    postcomment_fields = None
    postcomment_object = None

    def post(self, request, *args, **kwargs):
        form = self.get_postcomment_form()
        self.object = self.get_object()
        if form.is_valid():
            return self.postcomment_form_valid(form)
        else:
            return self.postcomment_form_invalid(form)

    def get_postcomment_initial(self):
        return self.postcommentinitial.copy()

    def get_postcomment_form_class(self):
        """ return the form to use for posting comment"""
        if self.commentmodel is not None:
            model = self.commentmodel
        else:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires you to define 'commentmodel' attribute.")

        if self.postcomment_fields is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires you to define 'postcomment_fields' attribute.")
        return model_forms.modelform_factory(model, fields=self.postcomment_fields)

    def get_postcomment_form(self, form_class=None):
        """ Return an instance of form to be used in view"""
        if form_class is None:
            form_class = self.get_postcomment_form_class()
        return form_class(**self.get_postcomment_form_kwargs())

    def get_postcomment_success_url(self):
        """ URL to redirect to after processing valid post comment form"""
        if self.postcomment_success_url:
            url = self.postcomment_success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured("No URL to redirect to. Please provide 'postcomment_success_url' or define a get_absolute_url on the Model")
        return url

    def postcomment_form_valid(self, form):
        self.postcomment_object = form.save(commit=False)
        setattr(self.postcomment_object, self.parentfield, self.object)
        self.postcomment_object.save()
        return HttpResponseRedirect(self.get_postcomment_success_url())

    def postcomment_form_invalid(self, form):
        return HttpResponseRedirect(self.get_context_data(postcommentform=form))

    def get_postcomment_form_kwargs(self):
        """ Return kwargs for instantiating form """
        kwargs = {
            'initial': self.get_postcomment_initial(),
            'prefix': None
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return kwargs

    def get_context_data(self, **kwargs):
        """ Insert the form into the context """
        if 'postcomment_form' not in kwargs:
            kwargs['postcomment_form'] = self.get_postcomment_form()
        return super().get_context_data(**kwargs)

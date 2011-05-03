from datetime import date, datetime, timedelta
from itertools import chain
from operator import attrgetter

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models import Q, get_app
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.importlib import import_module
from django.utils.translation import ugettext

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from pinax.apps.time_track.models import LoggedTime
from pinax.apps.time_track.forms import LoggedTimeForm, EditLoggedTimeForm
from pinax.apps.time_track.forms import UploadLoggedTimeForm, ReportParamsForm
from pinax.apps.time_track.importers import HamsterTsvImporter, FreshbooksCsvImporter



def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx


def overview(request, template_name="time_track/overview.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
    else:
        is_member = False
    
    if group:
        logged_times = group.content_objects(LoggedTime).filter(owner=request.user)
    else:
        logged_times = LoggedTime.objects.filter(owner=request.user)
    
    total_duration = timedelta()
    for logged_time in logged_times:
        total_duration += logged_time.duration()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "logged_times": logged_times,
        "total_duration": total_duration,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def upload(request, form_class=UploadLoggedTimeForm, template_name="time_track/upload.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
    else:
        is_member = False
    
    if request.method == "POST" and request.user.is_authenticated() and is_member:
        upload_time_form = form_class(request.POST, request.FILES)
        if upload_time_form.is_valid():
            uploaded_file = upload_time_form.cleaned_data['file_input']
            file_type = upload_time_form.cleaned_data['file_type']
            importer = globals()[file_type](uploaded_file, request.user)
            try:
                logged_times = importer.get_logged_times()
                for logged_time in logged_times:
                    logged_time.save()
                if request.POST.has_key("upload-more-time"):
                    if group:
                        redirect_to = bridge.reverse("time_track_upload", group)
                    else:
                        redirect_to = reverse("time_track_upload")
                    return HttpResponseRedirect(redirect_to)
                if group:
                    redirect_to = bridge.reverse("time_track_overview", group)
                else:
                    redirect_to = reverse("time_track_overview")
                return HttpResponseRedirect(redirect_to)
            except ValueError, ex:
                upload_time_form.add_file_input_error(ex)
    else:
        upload_time_form = form_class()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "upload_time_form": upload_time_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def report(request, form_class=ReportParamsForm, template_name="time_track/report.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
    else:
        is_member = False
    
    total_duration = timedelta()
    logged_times = tuple()
    if request.method == "POST" and request.user.is_authenticated() and is_member:
        report_params_form = form_class(request.POST)
        if report_params_form.is_valid():
            if group:
                start = report_params_form.cleaned_data['start']
                finish = report_params_form.cleaned_data['finish']
                logged_times = group.content_objects(LoggedTime).filter(start__gte=start, finish__lte=finish)
            else:
                logged_times = LoggedTime.objects # TODO
            for logged_time in logged_times:
                total_duration += logged_time.duration()
    else:
        report_params_form = form_class()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "report_params_form": report_params_form,
        "logged_times": logged_times,
        "total_duration": total_duration,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def detail(request, id, form_class=LoggedTimeForm, template_name="time_track/detail.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
    else:
        is_member = True
    
    logged_time_form = form_class()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "querystring": request.GET.urlencode(),
        "logged_time_form": logged_time_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


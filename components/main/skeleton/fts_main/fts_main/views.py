from django.http import Http404, HttpResponseRedirect,HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from .models import Component

from datetime import datetime

import requests

def home(request):
    return HttpResponse('<h1>Farmer Text Support</h1> See <a href="http://wiki.duboue.net/index.php/Farmer_Text_Support">Web site</a> for details.')

def register(request,component=None):
    if request.META['REMOTE_ADDR'] != '127.0.0.1':
        return HttpResponseForbidden()

    if request.method != 'POST':
        return HttpResponse('<h1>Use POST</h1>')

    if not 'url' in request.POST:
        return HttpResponse('<h1>Missing URL</h1>')

    Component(
        name=component.lower(),
        url=POST['url']
    ).save()
    
    return HttpResponse('<h1>Success</h1>')

def wrap(request, component, **kwargs):
     return HttpResponse(_wrap(request, component, **kwargs))

def _component_url(component):
    url = Component.objects.filter(name=component)
    if url.count() == 0:
        raise Http404('Not implemented')
    return url[0].url
    

def _wrap(request, component, **kwargs):
    url = _component_url(component)
    if request.method == 'POST':
       return requests.post(url + '/' + request.path, data=request.POST).text
    else:
        return requests.get(url + '/' + request.path).text

def question_new(request, component,**kwargs):
    response = _wrap(request, 'question', **kwargs)
    if len(response) > 0:
        # valid question ID
        OutstandingQuestion(
            question_id = int(response),
            since = datetime.now()
        ).save()
    return HttpResponse(response)

def answer_status(request, component,**kwargs):
    response = _wrap(request, 'question', **kwargs)
    if request.method == 'POST' and request.POST['accepted_yes_no'] in ['1','True','true']:
        # get question id associated with answer id
        url = _component_url(component)
        question_id = requests.get("%s/answer/%s/question" % (url,kwargs['aid'])).text
        outstanding = OutstandingQuestion.objects.filter(question_id=question_id)
        if outstanding.count()>0:
            outstanding.delete()
    return HttpResponse(response)



def stub(request,**kwargs):
    return HttpResponse('<h1>Not implemented</h1>')

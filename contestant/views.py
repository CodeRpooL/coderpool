from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from contestant.models import Contestant,Participant

def is_auth(u,g):
    l=u.groups.all()
    for i in l:
        if i.name==g:
            return True
    return False

@login_required
@user_passes_test(lambda u: is_auth(u,'contestant'),login_url='/home/?message=You are unauthorized to view this page')
def register(request):
    if request.method == 'GET':
        ret = {}
        if 'message' in request.GET:
            ret={'message':request.GET['message']}
        ret['u'] = request.user
        return render_to_response('register.html',ret,context_instance=RequestContext(request))
    else:
        c = Contestant(user = request.user,
                       gender = request.POST['gender'],
                       password = request.POST['password'],
                       dept = request.POST['dept'])
        c.save()
        p = Participant(contestant = c,
                       contest = request.POST['contest'],
                       added = False,
                       score = 0)
        p.save()
        return HttpResponseRedirect('/home/')

@login_required
@user_passes_test(lambda u: is_auth(u,'contestant'),login_url='/home/?message=You are unauthorized to view this page')
def changecontest(request):
    if request.method == 'GET':
        ret = {}
        if 'message' in request.GET:
            ret={'message':request.GET['message']}
        ret['p'] = Participant.objects.get(contestant__user = request.user)
        return render_to_response('changecontest.html',ret,context_instance=RequestContext(request))
    else:
        p = Participant.objects.get(contestant__user = request.user)
        if p.contest == int(request.POST['contest']):
            return HttpResponseRedirect('/home/?message=You already belong there')
        p.contest = request.POST['contest']
        p.added = False
        p.score = 0
        p.save()
        return HttpResponseRedirect('/home/')


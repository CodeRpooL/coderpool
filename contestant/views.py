from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from contestant.models import Contestant,Participant
from django.core.servers.basehttp import FileWrapper

def is_auth(u,g):
    l=u.groups.all()
    for i in l:
        if i.name==g:
            return True
    return False

@login_required
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

@login_required
@user_passes_test(lambda u: is_auth(u,'admin'),login_url='/home/?message=You are unauthorized to view this page')
def add(request):
    if request.method == 'GET':
        ret = {}
        if 'message' in request.GET:
            ret={'message':request.GET['message']}
        if 'contest' not in request.session:
            return HttpResponseRedirect('/contestant/selectcontest/')
        ret['p'] = Participant.objects.filter(added = False,contest=request.session['contest'])
        del request.session['contest']
        return render_to_response('list.html',ret,context_instance=RequestContext(request))
    else:
        l = request.POST.getlist('user')
        f = open('add.csv','w')
        f.write('id,first_name,last_name,name,email,gender,role,team,password,group,flag,color,acronym,country,status\n')
        for i in l:
            p = Participant.objects.get(id = i)
            p.added = True
            p.save()
            s = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(p.id,'a','a',p.contestant.user.first_name,p.contestant.user.email,p.contestant.gender,'Contestant',p.contestant.user.email,p.contestant.password,p.contestant.dept,'in','blue',p.contestant.dept,'in','1')
            f.write(s)
        f.close()
        w=FileWrapper(file('add.csv'))
        response = HttpResponse(w,mimetype='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s"%('add.csv')
        return response

@login_required
@user_passes_test(lambda u: is_auth(u,'admin'),login_url='/home/?message=You are unauthorized to view this page')
def selectcontest(request):
    if request.method == 'GET':
        ret = {}
        if 'message' in request.GET:
            ret={'message':request.GET['message']}
        return render_to_response('selectcontest.html',ret,context_instance=RequestContext(request))
    else:
        request.session['contest']=request.POST['contest']
        return HttpResponseRedirect('/contestant/add/')

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from contestant.models import Contestant,Participant
def userLogin(request):
    if request.method=='GET':
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home')
        elif 'e' in request.GET:
            return render_to_response('login.html',{'error':'1'},context_instance=RequestContext(request))
        else:
            return render_to_response('login.html',{},context_instance=RequestContext(request))
    else:
        user=authenticate(username=request.POST['uname'],password=request.POST['passwd'])
        if user is not None and user.is_active:
            login(request,user)
            return HttpResponseRedirect('/home')
        else:
            return HttpResponseRedirect('/login?e=1')

@login_required
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def home(request):
    ret={}
    contests = ['Coderpool','Coderpool Junior','The Girls Who Code']
    if 'message' in request.GET:
        ret={'message':request.GET['message']}
    g = request.user.groups.all()
    if g.filter(name = 'admin'):
        return render_to_response('admin.html',ret,context_instance=RequestContext(request))
    try:
        ret['p'] = Participant.objects.get(contestant__user=request.user)
    except Exception as e:
        return HttpResponseRedirect('/contestant/register/')
    ret['contest'] = contests[ret['p'].contest-1]
    return render_to_response('home.html',ret,context_instance=RequestContext(request))

def welcome(request):
    return render_to_response('welcome.html')

def userLogout(request):
    logout(request)
    return HttpResponseRedirect('/')

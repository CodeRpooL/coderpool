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
@user_passes_test(lambda u: is_auth(u,'admin'),login_url='/home/?message=You are unauthorized to view this page')
def createqn(request):
    if request.method == 'GET':
        ret = {}
        if 'message' in request.GET:
            ret={'message':request.GET['message']}
        ret['u'] = request.user
        return render_to_response('createqn.html',ret,context_instance=RequestContext(request))
    else:
        html = '''
<html>
<body>
<h1>%s</h1>
<h3> Description</h3>
%s
<h3>Input</h3>
%s
<h3>Output</h3>
%s
<h3>Sample Input</h3>
<pre>
%s
</pre>
<h3>Sample Output</h3>
<pre>
%s
</pre>
<table border=1 cellpadding=5>
<tr>
    <td>Time limit:</td>
    <td>%s</td>
    <td>Tags</td>
    <td>%s</td>
</tr>
<tr>
    <td>Author:</td>
    <td>%s</td>
    <td>Contest:</td>
    <td>%s</td>
</tr>
</body>
</html>
        '''%(request.POST['title'],request.POST['desc'],request.POST['ip'],request.POST['op'],request.POST['sip'],request.POST['sop'],request.POST['time'],request.POST['tags'],request.POST['author'],request.POST['contest'])
        f = open('desc.html','w')
        f.write(html)
        f.close()
        w=FileWrapper(file('desc.html'))
        response = HttpResponse(w,mimetype='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s"%('desc.html')
        return response

def team(request,team):
    return render_to_response(team+'.html',context_instance=RequestContext(request))

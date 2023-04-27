from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test

from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/index.html')

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/studentclick.html')

#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')



def adminsignup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'library/adminsignup.html',{'form':form})






def studentsignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)




def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')
    else:
        return render(request,'library/studentafterlogin.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    
    form=forms.BookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        if form.is_valid():
            user=form.save()
            return render(request,'library/bookadded.html')
    return render(request,'library/addbook.html',{'form':form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def updatebook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/updatebook.html',{'books':books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def afterupdatebook_view(request):
    form=forms.BookForm()
    keylist=list(request.POST.keys())
    isbn=keylist[1]
    print(isbn)
    result=models.Book.objects.filter(isbn=isbn).values()
    # print(result)
    # if 'name' in result:
    form.fields['name'].initial=result[0].get('name')
    form.fields['isbn'].initial=result[0].get('isbn')
    # form.fields['isbn'].disabled = True
    form.fields['author'].initial=result[0].get('author')
    form.fields['category'].initial=result[0].get('category')
    return render(request,'library/updaterec.html',{'form':form})  

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def afterupdaterec_view(request):
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        if form.is_valid():
            # user=form.save()
            print(form.cleaned_data)
            # models.Book.objects.filter(isbn=form.cleaned_data['isbn']).update(name=form.cleaned_data['name'], author=form.cleaned_data['author'],category=form.cleaned_data['category'])
            return redirect(updatebook_view)

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def deletebook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/deletebook.html',{'books':books})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def afterdelete_view(request):
    keylist=list(request.POST.keys())
    isbn=keylist[1]
    print(isbn)
    
    # val='delete'
    # for key, value in request.POST:
    #         if val == value:
    #             isbn=key
    # print(isbn)
    
    wishlist = models.Book.objects.get(isbn=isbn)
    wishlist.delete()
    books=models.Book.objects.all()
    return render(request,'library/deletebook.html',{'books':books})





@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    books=models.Book.objects.all()
    return render(request,'library/viewissuedbookbystudent.html',{'books':books})


def aboutus_view(request):
    return render(request,'library/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently = False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form':sub})
